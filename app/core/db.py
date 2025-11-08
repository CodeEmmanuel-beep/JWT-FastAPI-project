from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
