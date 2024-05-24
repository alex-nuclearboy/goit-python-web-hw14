"""
This script starts the FastAPI application using Uvicorn as the ASGI server.
It is configured to run on localhost at port 8000 and will automatically
reload during development if any changes are detected in the codebase.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
