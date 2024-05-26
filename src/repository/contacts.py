"""
Contact Management Operations Module
------------------------------------

This module provides asynchronous functions to handle CRUD operations
for contacts in a Contact Management App using FastAPI and SQLAlchemy.
Functions are designed to interact with a PostgreSQL database
to manage contact data associated with specific users.

The functionality provided by this module includes creating, retrieving,
updating, and deleting contacts, as well as fetching contacts with upcoming
birthdays. Each function is designed to be used as a dependency in FastAPI
route handlers.

Functions:

- ``get_contacts``: Fetch a list of contacts with optional search filtering.
- ``get_contact``: Retrieve a single contact by ID.
- ``create_contact``: Create a new contact in the database.
- ``remove_contact``: Delete a contact by ID.
- ``update_contact``: Update details of an existing contact.
- ``get_upcoming_birthdays``: Retrieve contacts with birthdays coming up \
                              within the next week.

Each function handles database interactions safely, ensuring that sessions
are managed correctly to prevent data leaks and maintain integrity.
"""
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

    :param skip: Number of entries to skip for pagination.
    :type skip: int
    :param limit: Maximum number of entries to return.
    :type skip: int
    :param user: The user whose contacts are to be retrieved.
    :type user: User
    :param search: Search query to filter contacts by any attribute \
                   (first name, last name, email, phone number).
    :type search: str
    :param db: SQLAlchemy session for database access.
    :type db: Session
    :return: A list of contacts that match the criteria
    :rtype: List[Contact]
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

    :param contact_id: The unique identifier of the contact.
    :type contact_id: int
    :param user: The user whose contact is to be retrieved.
    :type user: User
    :param db: SQLAlchemy session for database access.
    :type db: Session
    :return: The contact object if found, otherwise None.
    :rtype: Contact
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

    :param body: A Pydantic model containing contact data.
    :type body: ContactModel
    :param user: The user whose contact is to be created.
    :type user: User
    :param db: SQLAlchemy session for database access.
    :type db: Session
    :return: The newly created contact with populated fields.
    :rtype: Contact
    :raises HTTPException: If an error occurs during the creation process.
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
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Failed to create contact: {str(err)}"
        )


async def remove_contact(contact_id: int,
                         user: User,
                         db: Session) -> Contact | None:
    """
    Deletes a contact from the database by its ID.

    :param contact_id: The unique identifier of the contact.
    :type contact_id: int
    :param user: The user whose contact is to be deleted.
    :type user: User
    :param db: SQLAlchemy session for database access.
    :type db: Session
    :return: The deleted contact object if found and deleted, otherwise None.
    :rtype: Contact | None
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

    :param contact_id: The unique identifier of the contact to update.
    :type contact_id: int
    :param body: A Pydantic model containing the fields to update.
    :type body: ContactUpdate
    :param user: The user whose contact is to be updated.
    :type user: User
    :param db: SQLAlchemy session for database access.
    :type db: Session
    :return: The updated contact object if the update was successful, \
             otherwise None.
    :rtype: Optional[Contact]
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
        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contact, key, value)
        db.commit()
    return contact


async def get_upcoming_birthdays(db: Session,
                                 user: User,
                                 today: date) -> List[Contact]:
    """
    Retrieves contacts whose birthdays are coming up within the next week.

    :param db: SQLAlchemy session for database access.
    :type db: Session
    :param user: The user whose contacts' birthdays are being queried.
    :type user: User
    :param today: The current date to calculate the range of upcoming \
                  birthdays.
    :type today: date
    :return: A list of contacts whose birthdays are within the next week.
    :rtype: List[Contact]
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
