"""
Contact Management REST API with FastAPI

This FastAPI module provides endpoints for managing user authentication,
contacts, and user accounts in a Contact Management System. It uses Redis
for rate limiting API calls and integrates CORS support to handle
requests from specified origins.

The application includes the following functionalities:

* User Authentication and Registration (details in the /auth documentation)
* Contact Management with CRUD operations (Create, Read, Update, Delete):
    * List all contacts: GET /api/contacts
    * Create a new contact: POST /api/contacts
    * Get details of a specific contact: GET /api/contacts/{id}
    * Update a contact: PUT /api/contacts/{id}
    * Delete a contact: DELETE /api/contacts/{id}
* User Profile Management (details in the /users documentation)

Rate limiting is applied globally to ensure fair usage and prevent abuse.

**Functions:**

* startup() : Initialises the Redis connection and sets up rate limiting.
* read_root() : Returns a greeting message and API documentation path.

**Environment Variables:**

* REDIS_HOST: Hostname for Redis server.
* REDIS_PORT: Port number for Redis server.

**Usage:**

Run this module to start the FastAPI application:

```bash
$ uvicorn main:app --host localhost --port 8000 --reload
```
Once running, navigate to http://localhost:8000/docs for an interactive
API documentation and testing interface.

Author: Alex
Date: 2024-05-24
"""

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routes import contacts, auth, users
from src.conf.config import settings

import logging

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Define allowed origins for CORS
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from different modules
app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup() -> None:
    """
    Asynchronous function to initialise resources on application startup.
    Sets up the Redis instance for rate limiting and ensures all configurations
    are loaded properly.

    Raises:
        ConnectionError: If the connection to Redis fails.
    """
    try:
        r = await redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            encoding="utf-8",
            decode_responses=True
        )
        await FastAPILimiter.init(r)
    except redis.RedisError as e:
        logging.error(f"Failed to connect to Redis: {e}")
        raise ConnectionError("Failed to connect to Redis.") from e


@app.get("/")
def read_root() -> JSONResponse:
    """
    Root endpoint to provide a basic greeting and guide users to the API
    documentation.

    Returns:
        JSONResponse: A JSON response containing a welcome message and
                      a suggestion to visit the API docs.
    """
    return JSONResponse({
        "message": "Contact Management API is up and running!",
        "next_steps": "Please visit the /docs endpoint for detailed API "
        "documentation and interactive exploration of endpoints."
    })
