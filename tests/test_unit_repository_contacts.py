"""
Testing Module for Contact Management Operations
------------------------------------------------

This module provides a suite of asynchronous test cases for testing the CRUD
operations and additional functionalities of a Contact Management API
using FastAPI and SQLAlchemy. These tests aim to verify the correct behavior
of the API's interaction with a PostgreSQL database, focusing on creating,
retrieving, updating, deleting contacts, and getting birthdays.

The tests utilize the usest framework and MagicMock to simulate database
operations and interactions.

**Classes**:

- ``TestContacts``: A class containing test cases for the contact management
                    operations.

**Test Methods**:

- ``test_get_contacts``: Verifies fetching multiple contacts with pagination \
                         and optional search.
- ``test_get_contact_found``: Ensures that retrieving an existing contact \
                              by ID works correctly.
- ``test_get_contact_not_found``: Checks the behavior when an attempt is made \
                                  to retrieve a non-existent contact.
- ``test_create_contact``: Tests the creation of a new contact and checks \
                           if the contact's data is correctly stored.
- ``test_update_contact_found``: Confirms that updating an existing contact's \
                                 information works as expected.
- ``test_update_contact_not_found``: Tests the update operation when \
                                     the contact does not exist.
- ``test_remove_contact_found``: Tests the removal of an existing contact \
                                 from the database.
- ``test_remove_contact_not_found``: Verifies that the removal operation \
                                     behaves correctly when the contact \
                                     does not exist.
- ``test_get_upcoming_birthdays_within_week``: Checks if the system correctly \
                                               identifies contacts with \
                                               upcoming birthdays within \
                                               the next week.
- ``test_get_upcoming_birthdays_outside_week``: Ensures that contacts whose \
                                                birthdays are not within \
                                                the next week are not \
                                                incorrectly fetched.

**Usage**:

- The test suite can be executed as a standalone script by running the module:

.. code-block:: python

    python -m tests.test_unit_repository_contacts
"""
import unittest
from unittest.mock import MagicMock

from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate

from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_upcoming_birthdays,
    create_contact,
    update_contact,
    remove_contact
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    """Test suite for verifying the contact management operations."""

    @classmethod
    def setUpClass(cls):
        """Prints a message when the test suite starts."""
        print("=== Start tests ===")

    @classmethod
    def tearDownClass(cls):
        """Prints a message when the test suite ends."""
        print("=== End tests ===")

    def setUp(self):
        """Prepare resources for each test method."""
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        """Tests retrieval of multiple contacts with pagination and search."""
        print("=== Test: Get Multiple Contacts ===")
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit() \
            .all.return_value = contacts
        result = await get_contacts(
            skip=0, limit=10, user=self.user, search="", db=self.session
        )
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        """Ensures retrieving a specific contact by ID is successful."""
        print("=== Test: Get Specific Contact (Found) ===")
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        """Checks the behavior when no contact is found with the given ID."""
        print("=== Test: Get Specific Contact (Not Found) ===")
        self.session.query().filter().first.return_value = None
        result = await get_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_create_contact(self):
        """Tests the creation of a new contact and validates stored data."""
        print("=== Test: Create New Contact ===")
        body = ContactModel(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="380638541296",
            birthday="2000-01-01",
            additional_info="Test"
        )
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await create_contact(
            body=body, user=self.user, db=self.session
        )
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.additional_info, body.additional_info)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        """Confirms that updating a contact's information works as expected."""
        print("=== Test: Update Contact (Found) ===")
        body = ContactUpdate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="380508541296",
            birthday="1995-03-01",
            additional_info="Test update"
        )
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        """Tests update operation when the contact does not exist."""
        print("=== Test: Update Contact (Not Found) ===")
        body = ContactUpdate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="380508541296",
            birthday="1995-03-01",
            additional_info="Test update"
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        """Tests the removal of a contact found in the database."""
        print("=== Test: Remove Contact (Found) ===")
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_remove_note_not_found(self):
        """
        Ensures the correct behavior when attempting to remove
        a non-existent contact.
        """
        print("=== Test: Remove Contact (Not Found) ===")
        self.session.query().filter().first.return_value = None
        result = await remove_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_get_upcoming_birthdays_within_week(self):
        """
        Tests the ability to fetch contacts with birthdays occurring
        within the next week.
        """
        print("=== Test: Get Contacts' Birthdays Within a Week ===")
        today = date(2024, 5, 28)  # Example date that causes month transition
        upcoming_birthdays_same_month = [
            Contact(birthday=today + timedelta(days=i), user_id=self.user.id)
            for i in range(1, 4)  # Dates from May 29th to May 31st
        ]
        upcoming_birthdays_next_month = [
            Contact(birthday=today + timedelta(days=i), user_id=self.user.id)
            for i in range(4, 8)  # Dates from June 1st to June 4th
        ]
        upcoming_birthdays = (
            upcoming_birthdays_same_month + upcoming_birthdays_next_month
        )

        self.session.query().filter().all.return_value = upcoming_birthdays
        result = await get_upcoming_birthdays(
            db=self.session, user=self.user, today=today
        )
        self.assertEqual(result, upcoming_birthdays)

    async def test_get_upcoming_birthdays_outside_week(self):
        """
        Ensures that no birthdays are incorrectly returned
        if outside the next week.
        """
        print("=== Test: Get Contacts' Birthdays Outside of a Week ===")
        self.session.query().filter().all.return_value = []
        result = await get_upcoming_birthdays(
            db=self.session, user=self.user, today=date.today()
        )
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
