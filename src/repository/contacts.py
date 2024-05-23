from typing import List, Optional
from datetime import date, timedelta
from fastapi import HTTPException
from sqlalchemy import extract, and_, or_
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


async def get_contacts(skip: int,
                       limit: int,
                       user: User,
                       search: str,
                       db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts from the database,
    with optional search filtering and pagination.

    Args:
        skip (int): Number of entries to skip for pagination.
        limit (int): Maximum number of entries to return.
        user (User): The user whose contacts are to be retrieved.
        search (str): Search query to filter contacts by any attribute
                      (first name, last name, email, phone number).
        db (Session): SQLAlchemy session for database access.

    Returns:
        List[Contact]: A list of contacts that match the criteria.
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)
    if search:
        search_filter = (
            (Contact.first_name.ilike(f'%{search}%')) |
            (Contact.last_name.ilike(f'%{search}%')) |
            (Contact.email.ilike(f'%{search}%')) |
            (Contact.phone_number.ilike(f'%{search}%'))
        )
        query = query.filter(search_filter)
    return query.offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact by its ID.

    Args:
        contact_id (int): The unique identifier of the contact.
        user (User): The user whose contact is to be retrieved.
        db (Session): SQLAlchemy session for database access.

    Returns:
        Contact: The contact object if found, otherwise None.
    """
    return (
        db.query(Contact)
        .filter(
            and_(
                Contact.id == contact_id,
                Contact.user_id == user.id
            )
        )
        .first()
    )


async def create_contact(body: ContactModel,
                         user: User,
                         db: Session) -> Contact:
    """
    Creates a new contact in the database.

    Args:
        body (ContactModel): A Pydantic model containing contact data.
        user (User): The user whose contact is to be created.
        db (Session): SQLAlchemy session for database access.

    Returns:
        Contact: The newly created contact with populated fields.
    """
    try:
        contact = Contact(first_name=body.first_name,
                          last_name=body.last_name,
                          email=body.email,
                          phone_number=body.phone_number,
                          birthday=body.birthday,
                          additional_info=body.additional_info,
                          user_id=user.id)
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def remove_contact(contact_id: int,
                         user: User,
                         db: Session) -> Contact | None:
    """
    Deletes a contact from the database by its ID.

    Args:
        contact_id (int): The unique identifier of the contact.
        user (User): The user whose contact is to be deleted.
        db (Session): SQLAlchemy session for database access.

    Returns:
        Contact | None: The deleted contact object if found and deleted,
                        otherwise None.
    """
    contact = (
        db.query(Contact)
        .filter(
            and_(
                Contact.id == contact_id,
                Contact.user_id == user.id
            )
        )
        .first()
    )

    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int,
                         body: ContactUpdate,
                         user: User,
                         db: Session) -> Optional[Contact]:
    """
    Updates an existing contact's information in the database.

    Args:
        contact_id (int): The unique identifier of the contact to update.
        body (ContactUpdate): A Pydantic model containing the fields to update.
        user (User): The user whose contact is to be updated.
        db (Session): SQLAlchemy session for database access.

    Returns:
        Optional[Contact]: The updated contact object if the update
                           was successful, otherwise None.
    """
    contact = (
        db.query(Contact)
        .filter(
            and_(
                Contact.id == contact_id,
                Contact.user_id == user.id
            )
        )
        .first()
    )

    if contact:
        update_data = body.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contact, key, value)
        db.commit()
    return contact


async def get_upcoming_birthdays(db: Session,
                                 user: User,
                                 today: date) -> List[Contact]:
    """
    Retrieves contacts whose birthdays are coming up within the next week.

    Args:
        db (Session): SQLAlchemy session for database access.
        user (User): The user whose contacts' birthdays are being queried.
        today (date): The current date to calculate the range
                      of upcoming birthdays.

    Returns:
        List[Contact]: A list of contacts whose birthdays are
                       within the next week.
    """
    in_a_week = today + timedelta(days=7)
    if today.month == in_a_week.month:
        # Simple case: both dates are in the same month
        return db.query(Contact).filter(
            and_(
                Contact.user_id == user.id,
                extract('month', Contact.birthday) == today.month,
                extract('day', Contact.birthday) >= today.day,
                extract('day', Contact.birthday) <= in_a_week.day
            )
        ).all()
    else:
        # Complex case: dates span over two different months
        return db.query(Contact).filter(
            and_(
                Contact.user_id == user.id,
                or_(
                    # Check for birthdays at the end of the current month
                    and_(
                        extract('month', Contact.birthday) == today.month,
                        extract('day', Contact.birthday) >= today.day
                    ),
                    # Check for birthdays at the start of the next month
                    and_(
                        extract('month', Contact.birthday) == in_a_week.month,
                        extract('day', Contact.birthday) <= in_a_week.day
                    )
                )
            )
        ).all()
