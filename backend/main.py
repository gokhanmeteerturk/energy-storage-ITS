# backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.exceptions import ITSException, handle_its_exception
from .database import engine, get_db
from .models.student import schema
from .dependencies import get_domain_service, get_student_service, get_pedagogical_service
from .api.routes import topics, progress, quiz, qa
# Create database tables
schema.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Energy Storage ITS")


@app.exception_handler(ITSException)
async def its_exception_handler(request, exc: ITSException):
    """
    Global exception handler for our custom ITS exceptions.
    This ensures consistent error handling across all endpoints.
    """
    http_exc = handle_its_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content={"detail": http_exc.detail}
    )

# Add CORS middleware to allow requests from our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our route modules
app.include_router(topics.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(qa.router, prefix="/api")
# Startup event to initialize student progress
@app.on_event("startup")
async def startup_event():
    # Get our services through dependency injection
    domain_service = get_domain_service()
    student_service = get_student_service()
    db = next(get_db())
    
    # Initialize progress records for all topics
    student_service.initialize_progress(db)