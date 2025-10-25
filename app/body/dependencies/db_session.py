from body.database.config import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends


def get_db():
    db = Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
