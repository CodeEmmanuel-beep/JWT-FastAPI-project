from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    DateTime,
    String,
    Float,
    ForeignKey,
    UniqueConstraint,
    Enum as SQLEnum,
)
from enum import Enum
from app.core.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta


def current_utc_time():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    username = Column(String)
    password = Column(String)
    name = Column(String)
    age = Column(Integer)
    nationality = Column(String)

    tasks = relationship("Task", back_populates="user")
    markets = relationship("Market", back_populates="user")
    calculations = relationship("Calculate", back_populates="user")
    expenses = relationship("Expense", back_populates="user")
    priorities = relationship("Priority", back_populates="user")
    blogs = relationship("Blog", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    reacts = relationship("React", back_populates="user")
    shares = relationship("Share", back_populates="user")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    complete = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    days_to_execution = Column(Integer)
    day_of_execution = Column(DateTime)
    status = Column(String, default="pending")
    time_of_implementation = Column(DateTime, default=current_utc_time)

    user = relationship("User", back_populates="tasks")


class Market(Base):
    __tablename__ = "markets"
    id = Column(Integer, primary_key=True, index=True)
    section = Column(Integer)
    trade = Column(String)
    traders = Column(Integer)
    sales_per_day = Column(Float)
    taxes = Column(String)
    union = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    time_of_commencement = Column(DateTime, default=current_utc_time)

    user = relationship("User", back_populates="markets")


class Calculate(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String)
    numbers = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    result = Column(Float)
    time_of_calculation = Column(DateTime, default=current_utc_time)

    user = relationship("User", back_populates="calculations")


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    income = Column(Float)
    days_until_next_income = Column(Integer)
    feasible_budget = Column(Float)
    savings_percentage = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)
    message = Column(String)
    data = Column(String)
    time_of_budgetting = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="expenses")


class Priority(Base):
    __tablename__ = "priorities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    essentials = Column(Float)
    extras = Column(Float)
    income = Column(Float)
    status = Column(String)
    message = Column(String)
    data = Column(String, nullable=True)
    time_stamp = Column(DateTime, default=current_utc_time)

    user = relationship("User", back_populates="priorities")


class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    comments_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    reacts_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    time_of_post = Column(DateTime, default=datetime.now(timezone.utc))
    comments = relationship("Comment", back_populates="blog")
    user = relationship("User", back_populates="blogs")
    react = relationship("React", back_populates="blog")

    shares = relationship("Share", back_populates="blog")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    like = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    blog_id = Column(Integer, ForeignKey("blogs.id"))
    reacts_count = Column(Integer, default=0)
    time_of_post = Column(DateTime, default=datetime.now(timezone.utc))
    blog = relationship("Blog", back_populates="comments")
    user = relationship("User", back_populates="comments")
    react = relationship("React", back_populates="comment")


class ReactionType(str, Enum):
    like = "like"
    love = "love"
    angry = "angry"
    laugh = "laugh"
    wow = "wow"
    sad = "sad"


class React(Base):
    __tablename__ = "reacts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(ReactionType), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    blog_id = Column(Integer, ForeignKey("blogs.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"))
    time_of_reaction = Column(DateTime, default=current_utc_time)
    __table_args__ = (
        UniqueConstraint(user_id, blog_id, name="unique_blog_react"),
        UniqueConstraint(user_id, comment_id, name="unique_comment_react"),
    )
    comment = relationship("Comment", back_populates="react")
    blog = relationship("Blog", back_populates="react")
    user = relationship("User", back_populates="reacts")


class ShareType(str, Enum):
    love = "love"
    angry = "angry"
    laugh = "laugh"
    wow = "wow"
    sad = "sad"


class Share(Base):
    __tablename__ = "shares"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blog_id = Column(Integer, ForeignKey("blogs.id"))
    content = Column(String)
    type = Column(SQLEnum(ShareType), nullable=True)
    time_of_share = Column(DateTime, default=current_utc_time)

    user = relationship("User", back_populates="shares")
    blog = relationship("Blog", back_populates="shares")
