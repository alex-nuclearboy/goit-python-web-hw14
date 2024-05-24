# Contact Management API

This repository is an extension of a previous project, which can be found [here](https://github.com/alex-nuclearboy/goit-python-web-hw13/tree/main/first_task).
The original project includes a REST API for managing contact information, built with FastAPI and SQLAlchemy, and leverages PostgreSQL as the backend database. It supports basic CRUD operations for contact management along with additional functionalities such as searching for contacts by various attributes, retrieving contacts with upcoming birthdays, user authentication, and authorization. This extended version adds comprehensive project documentation that can be generated using Sphinx.

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

#### Extended:

- **Detailed Documentation:** Comprehensive documentation is added and can be generated using Sphinx.

## Technologies Used

- **FastAPI:** For creating the REST API.
- **SQLAlchemy:** As the ORM for database interactions.
- **PostgreSQL:** As the backend database.
- **Pydantic:** For data validation.
- **Alembic:** For database migrations.
- **Docker:** Used to containerize the application and PostgreSQL database.
- **Poetry:** For managing Python package dependencies and virtual environments.
- **Sphinx:** For generating project documentation.

## Installation and Usage

### Prerequisites

- **Docker and Docker Compose:** Ensure you have Docker and Docker Compose installed on your system to handle the application and database containers.
- **Python:** Ensure Python 3.10 or higher is installed on your system.
- **Poetry:** This project uses Poetry for dependency management. Install Poetry by following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

### Setting Up the Project

- **Clone the Repository:**
```bash
git clone https://github.com/alex-nuclearboy/goit-python-web-hw14.git
```

- **Navigate to the Project Directory:**
```bash
cd goit-python-web-hw14
```

- **Environment Setup**

Create a `.env` file with the following content and substitute your values:

```plaintext
# Database PostgreSQL
POSTGRES_DB=rest_app
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# JWT authentication
SECRET_KEY=
ALGORITHM=HS256

# Email service
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=
MAIL_SERVER=

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Cloud Storage
CLOUDINARY_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

- **Activate the Poetry Environment and Install Dependencies:**
```bash
poetry shell
poetry install --no-root
```

- **Start the PostgreSQL Server:**
```bash
docker compose up -d
```

- **Run Alembic Migrations**
```bash
alembic upgrade head
```

### Starting

- **Running the FastAPI application**:
    - Unix/Linux/macOS:
    ```bash
    python3 run_app.py
    ```
    - Windows:
    ```powershell
    py run_app.py
    ```

This command will start the API server accessible at [http://localhost:8000](http://localhost:8000).

## Using the API with Swagger UI

Once the server is running, you can access the Swagger UI to test the API endpoints at [http://localhost:8000/docs](http://localhost:8000/docs).

## Using the API with Postman

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

## Generating and Viewing Project Documentation

The project includes comprehensive documentation that can be generated using Sphinx. To generate and view the documentation:

- **Navigate to the docs Directory:**
```bash
cd docs
```

- **Generate the Documentation:**
    - Unix/Linux/macOS:
    ```bash
    make html
    ```
    - Windows:
    ```powershell
    make.bat html
    ```
- **View the Documentation:**

Open the generated HTML documentation by navigating to the _build/html directory and opening the index.html file in a web browser.

## Stopping the Application and Exiting

When you are finished using the application, follow these steps to properly shut down the server and exit the development environment:

- **Stopping the Application:**

To stop the FastAPI application, you simply need to press `CTRL+C` in the terminal window where the server is running. This will terminate the server process.

- **Shutting Down the PostgreSQL Server:**

If you've started the PostgreSQL server using Docker Compose and wish to stop it, you can use the following command:
```bash
docker compose down
```

This command stops the running containers and removes the containers created by docker compose up, along with their networks. It’s a clean way to ensure that no unnecessary Docker processes remain running. If you wish to stop the container but not remove it, you can use:
```bash
docker compose stop
```

- **Exiting the Poetry Environment**
```bash
exit
```

This command will deactivate the virtual environment and return you to your system's default environment.
