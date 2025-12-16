# JWT FastAPI Project

A full‑featured backend API built with FastAPI and SQLAlchemy, implementing secure JWT authentication and database‑driven CRUD operations across multiple domains. The project demonstrates production‑ready practices and cloud deployment.

# Features

User Authentication: JWT tokens with Argon2 password hashing for secure login and session management

Secure Token Validation: Robust token verification across all endpoints

CRUD Operations: Full Create, Read, Update, Delete support for multiple entities

Environment‑Based Secret Management: Secure handling of keys and secrets via environment variables

Optimized SQLAlchemy Integration: Efficient ORM usage with PostgreSQL and SQLite support

Pagination and Standardized Responses: Consistent API responses with pagination support


# Tech Stack

**Backend Framework**: FastAPI

**Database**: PostgreSQL + SQLite with SQLAlchemy ORM

**Authentication**: JWT (Python‑Jose) + Argon2 (Passlib)

**Data Validation**: Pydantic

**Environment Management**: Python‑dotenv

# Setup and Installation

 **Clone the repository**
git clone https://github.com/CodeEmmanuel-beep/JWT-FastAPI-project.git
cd JWT-FastAPI-project

 **Install dependencies**
pip install -r requirements.txt
 
 **Run the API**
uvicorn body.main:app --reload

# Authentication Workflow

Register and log in through the provided endpoints.

Copy the returned JWT token.
In Swagger UI, click Authorize and paste the token.

Access secured routes with full authentication.

All credentials are validated through JWT tokens and securely stored using Argon2 hashing, ensuring strong protection across all access levels.

#  Project Outcome

This project delivers a production‑ready backend system with secure authentication, robust database integration, background task automation, and cloud deployment readiness. It demonstrates modern backend practices and can serve as a foundation for scalable applications.


**Author**

Emmanuel Eke

Backend Developer | FastAPI | SQLAlchemy | JWT | Python
