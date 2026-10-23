from contextlib import asynccontextmanager
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.config import EVENT_CAPACITY, EVENT_DATE, EVENT_NAME
from app.database import Base, engine, get_db
from app.schemas import RegistrationCreate, RegistrationResponse


registration_lock = Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Celestius Registration Backend",
    description="Backend API for workshop registrations",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid or missing information",
            "errors": exc.errors(),
        },
    )


@app.get("/")
def home():
    return {"message": "Celestius Registration Backend is running"}


@app.get("/event")
def event_status(db: Session = Depends(get_db)):
    registered = db.scalar(
        select(func.count()).select_from(models.Registration)
    )
    return {
        "event_name": EVENT_NAME,
        "event_date": EVENT_DATE,
        "capacity": EVENT_CAPACITY,
        "registered": registered,
        "seats_remaining": max(0, EVENT_CAPACITY - registered),
        "is_full": registered >= EVENT_CAPACITY,
    }


@app.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegistrationCreate,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    with registration_lock:
        existing = db.scalar(
            select(models.Registration).where(
                func.lower(models.Registration.email) == email
            )
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="This email is already registered",
            )

        registered = db.scalar(
            select(func.count()).select_from(models.Registration)
        )
        if registered >= EVENT_CAPACITY:
            raise HTTPException(
                status_code=409,
                detail="The event is full",
            )

        registration = models.Registration(
            name=payload.name,
            email=email,
            college=payload.college,
            department=payload.department,
        )
        db.add(registration)

        try:
            db.commit()
            db.refresh(registration)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="This email is already registered",
            )

    return registration


@app.get(
    "/registrations",
    response_model=list[RegistrationResponse],
)
def list_registrations(db: Session = Depends(get_db)):
    statement = select(models.Registration).order_by(
        models.Registration.id
    )
    return db.scalars(statement).all()


@app.get(
    "/registrations/email/{email}",
    response_model=RegistrationResponse,
)
def get_registration_by_email(
    email: str,
    db: Session = Depends(get_db),
):
    registration = db.scalar(
        select(models.Registration).where(
            func.lower(models.Registration.email)
            == email.strip().lower()
        )
    )
    if registration is None:
        raise HTTPException(
            status_code=404,
            detail="Registration not found",
        )
    return registration


@app.get(
    "/registrations/{registration_id}",
    response_model=RegistrationResponse,
)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db),
):
    registration = db.get(models.Registration, registration_id)
    if registration is None:
        raise HTTPException(
            status_code=404,
            detail="Registration not found",
        )
    return registration