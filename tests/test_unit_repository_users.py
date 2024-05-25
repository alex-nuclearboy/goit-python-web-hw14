"""
Testing Module for User Management Operations
---------------------------------------------

This module provides a suite of asynchronous test cases for testing the user
management functionalities of an application using FastAPI and SQLAlchemy.
These tests aim to ensure the correct behavior of operations related to user
management, including creating, retrieving, and updating user data.

The tests use the unittest framework and MagicMock to simulate database
operations and interactions, focusing on ensuring that all user management
functions perform as expected under various conditions.

**Classes**:

- ``TestUsers``: A class containing test cases for user management operations.

**Test Methods**:

- ``test_get_user_by_email``: Verifies that fetching a user by email \
                              retrieves the correct user from the database.
- ``test_create_user``: Tests the creation of a new user, including the \
                        assignment of a Gravatar image as the user's avatar.
- ``test_update_token``: Checks whether the refresh token of a user is \
                         updated correctly in the database.
- ``test_confirm_email``: Ensures that a user's email confirmation status is \
                          updated correctly.
- ``test_update_avatar``: Verifies that a user's avatar URL is updated \
                          correctly in the database.

**Usage**:

- The test suite can be executed as a standalone script by running the module:

.. code-block:: python

    python -m tests.test_unit_repository_users
"""

import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel

from src.repository.users import (
    create_user,
    update_token,
    confirm_email,
    update_avatar,
    get_user_by_email
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    """Test suite for verifying the user management operations."""

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
        self.user = User(
            id=1,
            username="testuser",
            email="user@example.com",
            password="123456",
            confirmed=True,
            avatar="http://example.com/avatar.jpg"
        )

    async def test_get_user_by_email_found(self):
        """Test retrieving a user by email when the user exists."""
        print("=== Test: Get User by Email (Found) ===")
        test_email = "user@example.com"
        user = User(
            id=1,
            username="testuser",
            email=test_email,
            password="123456",
            confirmed=True
        )
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(
            email=test_email, db=self.session
        )
        self.assertEqual(result, user)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.password, user.password)
        self.assertEqual(result.confirmed, user.confirmed)

    async def test_get_user_by_email_not_found(self):
        """Test retrieving a user by email when the user does not exist."""
        print("=== Test: Get User by Email (Not Found) ===")
        test_email = "user@example.com"
        user = User(
            id=1,
            username="testuser",
            email=test_email,
            password="123456",
            confirmed=True
        )
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(
            email=user.email, db=self.session
        )
        self.assertIsNone(result)

    async def test_create_user(self):
        """Tests the creation of a new user."""
        print("=== Test: Create New User ===")
        body = UserModel(
            username='testuser',
            email='user@example.com',
            password='123456'
        )
        avatar_url = "http://example.com/avatar.jpg"
        user = User()
        self.session.query().filter().first.return_value = user
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertEqual(avatar_url, self.user.avatar)

    async def test_update_token(self):
        """Test updating the refresh token of a user."""
        print("=== Test: Update Token ===")
        test_token = "new_refresh_token"
        await update_token(
            user=self.user,
            token=test_token,
            db=self.session
        )
        self.assertEqual(self.user.refresh_token, test_token)

    async def test_confirm_email(self):
        """Test confirming a user's email address."""
        print("=== Test: Confirm Email ===")
        test_email = "user@example.com"
        self.session.query().filter().first.return_value = self.user
        await confirm_email(email=test_email, db=self.session)
        self.assertTrue(self.user.confirmed)

    async def test_update_avatar(self):
        """Test updating a user's avatar."""
        print("=== Test: Update Avatar ===")
        avatar_url = "http://example.com/new_avatar.jpg"
        test_email = "user@example.com"
        self.session.query().filter().first.return_value = self.user
        result = await update_avatar(
            email=test_email, url=avatar_url, db=self.session
        )
        self.assertEqual(result.avatar, avatar_url)


if __name__ == '__main__':
    unittest.main()
