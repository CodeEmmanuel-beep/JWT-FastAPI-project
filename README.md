# JWT FastAPI project

A full-featured backend API built with **FastAPI** and **SQLAlchemy**, implementing secure **JWT authentication**, **role-based access control**, and **database-driven CRUD operations** across multiple domains.

---

##  Features

- **User Authentication (JWT + Argon2)**
- **Role-based Access**
  - `User` → Task routes  
  - `Developer` → Market routes  
  - `Mathematician` → Calculation routes
- **Secure Token Validation**
- **Full CRUD Support** (Create, Read, Update, Delete)
- **Centralized Logging System**
- **Environment-based Secret Key Management**
- **Optimized SQLAlchemy Integration**

---

## Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** SQLite + SQLAlchemy ORM  
- **Authentication:** JWT (Python-Jose) + Argon2 (Passlib)  
- **Data Validation:** Pydantic  
- **Environment Management:** Python-dotenv  

---

# Setup & Installation

```bash
# Clone the repository
git clone https://github.com/emmanueleke/finishing-fastapi.git
cd finishing-fastapi

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn body.main:app --reload

Access the documentation at:
 http://127.0.0.1:8000/docs

 Authentication

This API uses JWT-based authentication.
Each user type (User, Developer, Mathematician) has unique access privileges.

Register and login through the relevant endpoints (/Auth, /Market Authentification, /Mathematician Auth).

Copy the returned token.

Click Authorize on the Swagger UI and paste the token.

Access your secured routes.


Author
Emmanuel Eke
Backend Developer | FastAPI | SQLAlchemy | JWT | Python
