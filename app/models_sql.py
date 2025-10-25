from sqlalchemy import Column, Integer, Boolean, DateTime, String, Float
from app.database.config import Base
from datetime import datetime, timezone


def current_utc_time():
    return datetime.now(timezone.utc)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    description = Column(String)
    complete = Column(Boolean, default=False)
    nationality = Column(String)
    time_of_execution = Column(DateTime, default=current_utc_time)


class Market(Base):
    __tablename__ = "markets"
    id = Column(Integer, primary_key=True, index=True)
    developer_code = Column(Integer, unique=True)
    developer_name = Column(String)
    section = Column(Integer)
    trade = Column(String)
    traders = Column(Integer)
    sales_per_day = Column(Float)
    taxes = Column(String)
    union = Column(String)


class Calculate(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True, index=True)
    mathematician = Column(String)
    mathematician_secret = Column(String)
    username = Column(String)
    operation = Column(String)
    numbers = Column(String)
    result = Column(Float)
    time_of_calculation = Column(DateTime, default=current_utc_time)
