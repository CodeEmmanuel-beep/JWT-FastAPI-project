from app.core.db import SessionLocal, engine
from sqlalchemy.orm import Session


def get_db():
    db: Session = SessionLocal
    try:
        yield db
    finally:
        db.close()
