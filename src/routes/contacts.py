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
):
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
):
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
):
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
):
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
):
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
):
    contact = (
        await repository_contacts
        .remove_contact(contact_id, current_user, db)
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
