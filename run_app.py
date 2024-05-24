"""
Uvicorn ASGI Server Script
--------------------------

This script starts the FastAPI application using Uvicorn as the ASGI server.
It is configured to run on localhost at port 8000 and will automatically
reload during development if any changes are detected in the codebase.

Usage
.....

Run this module to start the FastAPI application:

.. code-block:: python

    python run_server.py

Once running, navigate to http://localhost:8000 to access the application
or to http://localhost:8000/docs for an interactive API documentation
and testing interface.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
