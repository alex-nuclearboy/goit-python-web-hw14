.. Contact Management API documentation master file, created by
   sphinx-quickstart on Fri May 24 14:46:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Contact Management API's documentation!
==================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


REST API configuration
======================
.. automodule:: src.conf.config
  :members:
  :undoc-members:
  :show-inheritance:
  :exclude-members: model_computed_fields, model_config, model_fields,
                    env_file, env_file_encoding, algorithm,
                    cloudinary_api_key, cloudinary_api_secret,
                    cloudinary_name, mail_from, mail_password,
                    mail_port, mail_server, mail_username,
                    postgres_db, postgres_host, postgres_password,
                    postgres_port, postgres_user, redis_host,
                    redis_port, secret_key, sqlalchemy_database_url


REST API main
=============
.. automodule:: main
  :members:
  :undoc-members:
  :show-inheritance:


REST API run
=============
.. automodule:: run_app
  :members:
  :undoc-members:
  :show-inheritance:


REST API Pydantic Models
========================
.. automodule:: src.schemas
  :members:
  :undoc-members:
  :show-inheritance:
  :exclude-members: first_name, last_name, email, phone_number, birthday,
                    additional_info, model_computed_fields, model_config,
                    model_fields, from_attributes, created_at, updated_at, id,
                    access_token, refresh_token, token_type,
                    username, password, detail, user, avatar


REST API Database
=================
.. automodule:: src.database.db
  :members:
  :undoc-members:
  :show-inheritance:

.. automodule:: src.database.models
  :members:
  :undoc-members:
  :show-inheritance:
  :exclude-members: id, first_name, last_name, email, phone_number, birthday,
                    additional_info, created_at, updated_at, user_id, user,
                    avatar, refresh_token, confirmed, username, password


REST API repository Contacts
============================
.. automodule:: src.repository.contacts
  :members:
  :undoc-members:
  :show-inheritance:

.. automodule:: tests.test_unit_repository_contacts
  :members:
  :undoc-members:
  :show-inheritance:


REST API repository Users
=========================
.. automodule:: src.repository.users
  :members:
  :undoc-members:
  :show-inheritance:

.. automodule:: tests.test_unit_repository_users
  :members:
  :undoc-members:
  :show-inheritance:


REST API routes Contacts
=========================
.. automodule:: src.routes.contacts
  :members:
  :undoc-members:
  :show-inheritance:

.. automodule:: tests.test_route_contacts
  :members:
  :undoc-members:
  :show-inheritance:


REST API routes Users
=====================
.. automodule:: src.routes.users
  :members:
  :undoc-members:
  :show-inheritance:


REST API routes Auth
====================
.. automodule:: src.routes.auth
  :members:
  :undoc-members:
  :show-inheritance:

.. automodule:: tests.test_route_auth
  :members:
  :undoc-members:
  :show-inheritance:


REST API service
======================
.. automodule:: src.services.auth
  :members:
  :undoc-members:
  :show-inheritance:
  :exclude-members: ALGORITHM, SECRET_KEY, oauth2_scheme, pwd_context, r

.. automodule:: src.services.email
  :members:
  :undoc-members:
  :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
