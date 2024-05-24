"""
Contact Management API Module
-----------------------------

This module defines the FastAPI routes for a Contact Management Application.
It includes endpoints for managing contact information such as creating,
retrieving, updating, and deleting contacts. Additionally, it features
functionality for listing contacts with upcoming birthdays and standard CRUD
operations for individual contact entries.

It leverages rate limiting and user authentication to ensure the security and
efficiency of the API.
"""
from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse, ContactUpdate
from src.database.models import User
from src.repository import contacts as repository_contacts
from .auth import auth_service

router = APIRouter(prefix='/contacts')


@router.get(
        "/birthdays", response_model=List[ContactResponse],
        description=(
            "Fetches contacts with birthdays coming up within the next week. "
            "Useful for generating reminders or notifications. "
            "Rate-limited to 30 requests per minute to maintain performance "
            "across the service."
        ),
        dependencies=[Depends(RateLimiter(times=30, seconds=60))]
)
async def get_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
) -> List:
    """
    Retrieve contacts whose birthdays occur within the next week.

    :param db: Database session to execute database operations.
    :type db: Session
    :param current_user: The user session from the authentication system.
    :type current_user: User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[ContactResponse]
    """
    today = date.today()
    upcoming_birthdays = (
        await repository_contacts
        .get_upcoming_birthdays(db, current_user, today)
    )
    return upcoming_birthdays


@router.get(
        "/", response_model=List[ContactResponse],
        description=(
            "Retrieves a list of all contacts from the database. "
            "Allows searching by various fields if specified. "
            "Rate-limited to 10 requests per minute to prevent abuse "
            "and ensure service responsiveness."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
) -> List:
    """
    Retrieves a list of contacts owned by the authenticated user.

    :param skip: Number of records to skip for pagination.
    :type skip: int
    :param limit: Maximum number of records to return.
    :type limit: int
    :param search: Optional search term to filter contacts.
    :type search: str
    :param db: Database session to execute database operations.
    :type db: Session
    :param current_user: The user session from the authentication system.
    :type current_user: User
    :return: A list of contact entries matching the criteria.
    :rtype: List[ContactResponse]
    """
    contacts = (
        await repository_contacts
        .get_contacts(skip, limit, current_user, search, db)
    )
    return contacts


@router.get(
        "/{contact_id}", response_model=ContactResponse,
        description=(
            "Retrieves detailed information about a specific contact "
            "by their ID. This endpoint is intended for fetching detailed "
            "data of an individual contact. Rate-limited to 30 requests per "
            "minute to ensure rapid access without overwhelming the service."
        ),
        dependencies=[Depends(RateLimiter(times=30, seconds=60))]
)
async def read_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
) -> ContactResponse:
    """
    Retrieves details for a specific contact identified by ID.

    :param contact_id: The unique identifier for the contact.
    :type contact_id: int
    :param current_user: The user session from the authentication system.
    :type current_user: User
    :param db: Database session to execute database operations.
    :type db: Session
    :return: The detailed information of the requested contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact = (
        await repository_contacts
        .get_contact(contact_id, current_user, db)
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post(
        "/", response_model=ContactResponse,
        status_code=status.HTTP_201_CREATED,
        description=(
            "Creates a new contact entry in the database. "
            "Allows authenticated users to add new contact information. "
            "Each request must include all required fields for a contact. "
            "Rate-limited to 10 requests per minute to ensure service "
            "quality and prevent abuse."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def create_contact(
    body: ContactModel,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
) -> ContactResponse:
    """
    Creates a new contact in the database using provided details.

    :param body: The data model containing all required fields \
                 for creating a contact.
    :type body: ContactModel
    :param current_user: The user session from the authentication system, \
                         indicating the owner of the contact.
    :type current_user: User
    :param db: Database session to execute database operations.
    :type db: Session
    :return: The newly created contact's details.
    :rtype: ContactResponse
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.patch(
        "/{contact_id}", response_model=ContactResponse,
        description=(
            "Updates details of an existing contact identified by its ID. "
            "Authenticated users can modify any of the contact's details "
            "provided in the payload. Rate-limited to 10 requests per minute "
            "to prevent excessive writes and maintain database integrity."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
) -> ContactResponse:
    """
    Updates an existing contact with new information provided by the user.

    :param contact_id: The unique identifier for the contact to update.
    :type contact_id: int
    :param body: The data model with fields that may be updated.
    :type body: ContactUpdate
    :param current_user: The user session from the authentication system, \
                         indicating the owner of the contact.
    :type current_user: User
    :param db: Database session to execute database operations.
    :type db: Session
    :return: The updated contact's details.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact = (
        await repository_contacts
        .update_contact(contact_id, body, current_user, db)
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete(
        "/{contact_id}", response_model=ContactResponse,
        description=(
            "Removes a contact entry from the database by its ID. "
            "This endpoint allows authenticated users to delete contacts. "
            "It's critical and rate-limited  to 10 requests per minute "
            "to avoid accidental or malicious deletions."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
) -> ContactResponse:
    """
    Removes a contact from the database.

    :param contact_id: The unique identifier for the contact to be deleted.
    :type contact_id: int
    :param current_user: The user session from the authentication system, \
                         indicating the owner of the contact.
    :type current_user: User
    :param db: Database session to execute database operations.
    :type db: Session
    :return: Details of the deleted contact if successful.
    :rtype: ContactResponse
    :raises HTTPException: If the contact does not exist.
    """
    contact = (
        await repository_contacts
        .remove_contact(contact_id, current_user, db)
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
