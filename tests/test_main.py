from fastapi.testclient import TestClient
from sqlalchemy import create_engine
import app


from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app

from app.database import Base, get_db

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Celestius Registration Backend is running"
    }

def test_event_status():
    response = client.get("/event")

    assert response.status_code == 200

    data = response.json()
    assert data["event_name"] == "Backend Development Workshop"
    assert data["capacity"] == 50
    assert "registered" in data
    assert "seats_remaining" in data

def test_invalid_email():
    response = client.post(
        "/register",
        json={
            "name": "Test Student",
            "email": "not-an-email",
            "college": "Test College",
            "department": "IT"
        }
    )

    assert response.status_code == 422
def test_duplicate_email():
    registration_data = {
        "name": "Test Student",
        "email": "duplicate@example.com",
        "college": "Test College",
        "department": "IT",
    }

    first_response = client.post(
        "/register", json=registration_data
    )
    second_response = client.post(
        "/register", json=registration_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
def test_registration_not_found():
    response = client.get("/registrations/99999")

    assert response.status_code == 404
