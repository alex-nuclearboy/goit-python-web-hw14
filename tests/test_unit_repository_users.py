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

- ``test_get_user_by_email_found``: Verifies that fetching a user by email \
                                    retrieves the correct user from the db.
- ``test_get_user_by_email_not_found``: Checks the behavior when no user \
                                        is found with the given email.
- ``test_create_user``: Tests the creation of a new user, including the \
                        assignment of a Gravatar image as the user's avatar.
- ``test_update_token``: Checks whether the refresh token of a user is \
                         updated correctly in the database.
- ``test_confirm_email``: Ensures that a user's email confirmation status is \
                          updated correctly.
- ``test_confirm_email_user_not_found``: Verifies the behavior when \
                                         attempting to confirm the email \
                                         of a non-existent user.
- ``test_update_avatar``: Verifies that a user's avatar URL is updated \
                          correctly in the database.
- ``test_update_avatar_user_not_found``: Checks the behavior when updating \
                                         the avatar of a non-existent user.

**Usage**:

- The test suite can be executed as a standalone script by running the module:

.. code-block:: python

    python -m tests.test_unit_repository_users
"""

import unittest
from unittest.mock import MagicMock, patch

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
        user = self.user
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
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(
            email=test_email, db=self.session
        )
        self.assertIsNone(result)

    async def test_create_user(self):
        """Tests the creation of a new user."""
        print("=== Test: Create New User ===")
        avatar_url = "http://example.com/avatar.jpg"

        with patch('src.repository.users.Gravatar') as mock_avatar:
            mock_avatar.return_value.get_image.return_value = avatar_url
            body = UserModel(
                username='testuser',
                email='user@example.com',
                password='123456'
            )
            user = User(
                username=body.username,
                email=body.email,
                password=body.password,
                avatar=avatar_url
            )
            # Mocking up methods of the user creation function
            self.session.add = MagicMock(user)
            self.session.commit = MagicMock()
            self.session.refresh = MagicMock(user)

            result = await create_user(body=body, db=self.session)

            # Checking method calls
            self.session.add.assert_called_once_with(result)
            self.session.commit.assert_called_once()
            self.session.refresh.assert_called_once_with(result)
            # Checking result attributes
            self.assertEqual(result.username, body.username)
            self.assertEqual(result.email, body.email)
            self.assertEqual(result.password, body.password)
            self.assertEqual(result.avatar, avatar_url)
            # Checking Gravatar calls
            mock_avatar.assert_called_once_with(body.email)
            mock_avatar.return_value.get_image.assert_called_once()

    async def test_update_token(self):
        """Test updating the refresh token of a user."""
        print("=== Test: Update Token ===")
        test_token = "new_refresh_token"
        self.session.commit = MagicMock()
        await update_token(
            user=self.user,
            token=test_token,
            db=self.session
        )
        self.assertEqual(self.user.refresh_token, test_token)
        self.session.commit.assert_called_once()  # Ensure commit was called

    async def test_confirm_email(self):
        """Test confirming a user's email address."""
        print("=== Test: Confirm Email ===")
        test_email = "user@example.com"
        user = self.user
        self.session.query().filter().first.return_value = user
        self.session.commit = MagicMock()
        await confirm_email(email=test_email, db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()  # Ensure commit was called

    async def test_confirm_email_user_not_found(self):
        """
        Test confirming a user's email address when the user does not exist.
        """
        print("=== Test: Confirm Email (User Not Found) ===")
        test_email = "user@example.com"
        self.session.query().filter().first.return_value = None
        self.session.commit = MagicMock()
        self.session.rollback = MagicMock()
        with self.assertRaises(ValueError) as context:
            await confirm_email(email=test_email, db=self.session)

        self.assertEqual(
            str(context.exception), f"User with email {test_email} not found."
        )
        self.session.commit.assert_not_called()  # Ensure commit was not called
        self.session.rollback.assert_called_once()

    async def test_update_avatar(self):
        """Test updating a user's avatar."""
        print("=== Test: Update Avatar ===")
        new_avatar_url = "http://example.com/new_avatar.jpg"
        test_email = "user@example.com"
        user = self.user
        self.session.query().filter().first.return_value = user
        self.session.commit = MagicMock()
        result = await update_avatar(
            email=test_email, url=new_avatar_url, db=self.session
        )
        self.assertEqual(result.avatar, new_avatar_url)
        self.session.commit.assert_called_once()  # Ensure commit was called

    async def test_update_avatar_user_not_found(self):
        """Test updating a user's avatar when the user does not exist."""
        print("=== Test: Update Avatar (User Not Found) ===")
        new_avatar_url = "http://example.com/new_avatar.jpg"
        test_email = "user@example.com"
        self.session.query().filter().first.return_value = None
        self.session.commit = MagicMock()
        self.session.rollback = MagicMock()

        with self.assertRaises(ValueError) as context:
            await update_avatar(
                email=test_email, url=new_avatar_url, db=self.session
            )

        self.assertEqual(
            str(context.exception), f"User with email {test_email} not found."
        )
        self.session.commit.assert_not_called()  # Ensure commit was not called
        self.session.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
