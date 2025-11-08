# JWT FastAPI project

A full-featured backend API built with **FastAPI** and **SQLAlchemy**, implementing secure **JWT authentication**, **role-based access control**, and **database-driven CRUD operations** across multiple domains.

---

##  Features

- **User Authentication (JWT + Argon2)**
- **Role-based Access**
- **Secure Token Validation**
- **Full CRUD Support** (Create, Read, Update, Delete)
- **Dynamic Logging System**
- **Environment-based Secret Key Management**
- **Optimized SQLAlchemy Integration**
- **Pagination, StandardResponse and DynamicResponse**
- **Automation** some features are automated using redis and celery
- **User Profile** an endpoint dedicated for users to view their activities
- **Smart endpoints** State of the art endpoin which can carry out functions like blog, comment, react, smart task enpoint that goes beyound CRUD, it also indicates when you have missed a deadline and sends you an email powered by sendgrid to notify you also when you have done the task a notification email is sent to you as well. The endpoints across this FastAPI are state of the art.

---

## Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** SQLite + PostgreSQL + SQLAlchemy ORM  
- **Authentication:** JWT (Python-Jose) + Argon2 (Passlib)
- **Automation:** Celery + Redis  
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


All credentials are validated through JWT tokens and securely stored using Argon2 hashing, ensuring robust protection across all access levels.

Register and login through the desired endpoints 

Copy the returned token.

Click Authorize on the Swagger UI and paste the token.

Access your secured routes.


Author
Emmanuel Eke
Backend Developer | FastAPI | SQLAlchemy | JWT | Python
