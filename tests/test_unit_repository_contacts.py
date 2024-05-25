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

    @classmethod
    def setUpClass(cls):
        print("=== Start tests ===")

    @classmethod
    def tearDownClass(cls):
        print("=== End tests ===")

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        print("=== Test: Get All Contacts ===")
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit() \
            .all.return_value = contacts
        result = await get_contacts(
            skip=0, limit=10, user=self.user, search="", db=self.session
        )
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        print("=== Test: Get Specific Contact (Found) ===")
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        print("=== Test: Get Specific Contact (Not Found) ===")
        self.session.query().filter().first.return_value = None
        result = await get_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_create_contact(self):
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
        print("=== Test: Remove Contact (Found) ===")
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_remove_note_not_found(self):
        print("=== Test: Remove Contact (Not Found) ===")
        self.session.query().filter().first.return_value = None
        result = await remove_contact(
            contact_id=1, user=self.user, db=self.session
        )
        self.assertIsNone(result)

    async def test_get_upcoming_birthdays_within_week(self):
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
        print("=== Test: Get Contacts' Birthdays Outside of a Week ===")
        self.session.query().filter().all.return_value = []
        result = await get_upcoming_birthdays(
            db=self.session, user=self.user, today=date.today()
        )
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
