Celestius Registration Backend Task

A REST API built with Python and FastAPI to manage registrations for the Celestius Backend Development Workshop.

Features

- to allow participants to register
- Prevent duplicate email registrations
- Set a maximum capacity of 50 participants
- Retrieve all registrations
- Retrieve a registration by ID or email
- View event details, registration count, and remaining seats
- Return appropriate HTTP status codes for successful and unsuccessful requests
- Automated API tests using pytest

Tech Stack

- Python — application logic
- FastAPI — REST API framework
- SQLAlchemy — database ORM
- SQLite — database
- Pydantic — request validation and response schemas
- Pytest — automated testing
- HTTPX — API test client dependency


Setup and Installation

1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "celestius backend event"

Replace the placeholder with your actual repository URL.

2. Create a virtual environment

python -m venv .venv

3. Activate the virtual environment

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

4. Install dependencies

python -m pip install -r requirements.txt

5. Run the application

python -m uvicorn app.main:app --reload

The API will be available at:

- Base URL: "http://127.0.0.1:8000"
- Interactive API documentation: "http://127.0.0.1:8000/docs"

The SQLite database is created locally when the application starts.

* POST `/register` – Register a participant

* GET `/registrations` – Get all registrations

* GET `/registrations/{id}` – Get a registration by ID

* GET `/stats` – Get registration statistics


Example Registration Request

"POST /register"

{
  "name": "Test Student",
  "email": "student@example.com",
  "college": "Example College",
  "department": "Information Technology"
}

Important HTTP Status Codes

- "201 Created" — registration successful
- "200 OK" — request successful
- "409 Conflict" — duplicate email or event capacity reached
- "404 Not Found" — registration does not exist
- "422 Unprocessable Entity" — invalid request data

Running Automated Tests

Run the test suite from the project root:

python -m pytest -v

The tests cover the home endpoint, event status, invalid email validation, duplicate email prevention, and handling a registration that does not exist.

Design Notes

- Separation of concerns: API routes, database configuration, database models, and validation schemas are kept in separate modules.
- Input validation: Pydantic validates incoming registration data.
- Data integrity: Unique email constraints and registration checks help prevent duplicate registrations.
- Capacity management: The API checks the configured participant limit before accepting registrations.
- Testing isolation: Automated tests use a separate in-memory SQLite database to avoid modifying the local registration database.

