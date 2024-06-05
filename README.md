# Contact Management API

This repository extends a previous project, which can be found [here](https://github.com/alex-nuclearboy/goit-python-web-hw13/tree/main/first_task), enhancing a REST API for contact management with comprehensive documentation generated using Sphinx. Built with FastAPI and SQLAlchemy, it supports advanced features including user authentication, contact searches, rate limiting, and integration with Cloudinary for avatar updates. This extension focuses on improved documentation and testing.

## Table of Contents

1. [Key Features](#key-features)
   - [Original](#original)
   - [New in this extension](#new-in-this-extension)
2. [Technologies Used](#technologies-used)
3. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Generating and Viewing Project Documentation](#generating-and-viewing-project-documentation)
   - [Testing](#testing)
   - [Starting the FastAPI Application](#starting-the-fastapi-application)
4. [Using the API](#using-the-api)
   - [Using the API with Swagger UI](#using-the-api-with-swagger-ui)
   - [Using the API with Postman](#using-the-api-with-postman)
5. [Shutting Down and Exiting](#shutting-down-and-exiting)
   - [Stopping the Application](#stopping-the-application)
   - [Shutting Down the PostgreSQL Server](#shutting-down-the-postgresql-server)
   - [Exiting the Poetry Environment](#exiting-the-poetry-environment)

## Key Features

#### Original:

- **Create new contacts:** Add new contact entries to the database.
- **Retrieve all contacts:** Fetch all contacts with pagination support.
- **Retrieve a single contact by ID:** Get details of a specific contact.
- **Update existing contacts:** Modify details of existing contacts.
- **Delete contacts:** Remove contact entries from the database.
- **Search for contacts:** Look up contacts by name, email, or phone number.
- **List upcoming birthdays:** Get contacts whose birthdays occur within the next week.
- **User Authentication:** Allows new users to register and returning users to authenticate using secure hashing and JWT tokens.
- **Authorization:** Secures API endpoints with JWT-based authorization to ensure that only authorized users can access specific actions.
- **Email Verification:** Implements a mechanism to verify the email addresses of registered users.
- **Rate Limiting:** Restricts the number of requests to contact routes to prevent abuse, specifically limiting the rate of contact creation.
- **CORS Support:** Enables Cross-Origin Resource Sharing (CORS) for the REST API.
- **User Avatar Update:** Integrates with the Cloudinary service to allow users to update their avatar images.

#### New in this extension:

- **Enhanced Documentation:** Comprehensive documentation is added and can be generated using Sphinx.
- **Tests:** Tests to ensure the robustness of the API.

## Technologies Used

- **FastAPI:** For creating the REST API.
- **SQLAlchemy:** As the ORM for database interactions.
- **PostgreSQL:** As the backend database.
- **Pydantic:** For data validation.
- **Alembic:** For database migrations.
- **Docker:** Used to containerize the application and PostgreSQL database.
- **Poetry:** For managing Python package dependencies and virtual environments.
- **Sphinx:** For generating project documentation.
- **Unittest** and **Pytest:** For writing and running tests.

## Getting Started

### Prerequisites

- **Docker and Docker Compose:** Ensure you have Docker and Docker Compose installed on your system to handle the application and database containers.
- **Python:** Ensure Python 3.10 or higher is installed on your system.
- **Poetry:** This project uses Poetry for dependency management. Install Poetry by following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

### Installation

- **Clone the repository:**
```bash
git clone https://github.com/alex-nuclearboy/goit-python-web-hw14.git
```

- **Navigate to the project directory:**
```bash
cd goit-python-web-hw14
```

- **To set up the environment** use the following commands depending on your operating system:
   - Unix/Linux/macOS:
   ```bash
   cp .env.example .env
   ```
   - Windows:
   ```powershell
   copy .env.example .env
   ```

Adjust `.env` file with your settings

- **Activate the Poetry environment and install dependencies:**
```bash
poetry shell
poetry install --no-root
```

- **Start the PostgreSQL server:**
```bash
docker compose up -d
```

- **Run database migrations**
```bash
alembic upgrade head
```

### Generating and Viewing Project Documentation

The project includes comprehensive documentation that can be generated using Sphinx. To generate and view the documentation:

- **Navigate to the `docs` directory:**
```bash
cd docs
```

- **To generate the documentation** use the following commands depending on your operating system:
   - Unix/Linux/macOS:
   ```bash
   make html
   ```
   - Windows:
   ```powershell
   make.bat html
   ```
- **View the generated HTML documentation** in a web browser:
   - Unix/Linux:
   ```bash
   xdg-open _build/html/index.html
   ```
   - macOS:
   ```bash
   open _build/html/index.html
   ```
   - Windows:
   ```powershell
   start _build\html\index.html
   ```
### Testing

#### Unit tests

Unit tests are written using the `unittest` framework. To run the unit tests, use the following commands:

- **Return to the root directory:**
```bash
cd ..
```
- **Run unit tests for contact repository:**
```bash
python -m tests.test_unit_repository_contacts
```
- **Run unit tests for user repository:**
```bash
python -m tests.test_unit_repository_users
```

#### `Pytest` framework

Integration tests are written using the `pytest` framework. To run tests, use the following commands:
- **Run tests for authentication routes:**
```bash
pytest tests/test_route_auth.py -v
```
- **Run tests for contact routes:**
```bash
pytest tests/test_route_contacts.py -v
```

### Starting the FastAPI Application

- **To launch the FastAPI server** use the following commands depending on your operating system:
   - Unix/Linux/macOS:
   ```bash
   python3 run_app.py
   ```
   - Windows:
   ```powershell
   py run_app.py
   ```

This command will start the API server accessible at [http://localhost:8000](http://localhost:8000).

## Using the API

### Using the API with Swagger UI

Once the server is running, you can access the Swagger UI to test the API endpoints at [http://localhost:8000/docs](http://localhost:8000/docs).

### Using the API with Postman

- **Register a New User:**

Send a POST request to `http://localhost:8000/api/auth/signup` with a JSON body containing `username`, `email`, and `password`.

Example:
```bash
{
  "username": "usertest",
  "email": "test@api.com",
  "password": "123456"
}
```

- **Login:**

Send a POST request to `http://localhost:8000/api/auth/login` with `email` and `password` to receive access and refresh tokens.

- **Access Secure Endpoints:**

Include the Authorization: Bearer `<access_token>` header in requests to secured endpoints.

## Shutting Down and Exiting

### Stopping the Application

To stop the FastAPI application, you simply need to press `CTRL+C` in the terminal window where the server is running. This command will terminate the server process.

### Shutting down the PostgreSQL Server:

If you've started the PostgreSQL server using Docker Compose and wish to stop it, you can use the following command:

- **To stop and remove containers, networks, and volumes:**
```bash
docker compose down
```

- **To stop the server without removing resources:**
```bash
docker compose stop
```

### Exiting the Poetry Environment
```bash
exit
```

This command will deactivate the virtual environment and return you to your system's default environment.

<a href="#contact-management-api" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; display: inline-block; border-radius: 8px; text-decoration: none;">Back to Top</a>
