from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models_sql import Task
from app.body.dependencies.db_session import get_db
from app.body.dependencies.auth_jwt import (
    create_access_token,
    verify_password,
    hash_password,
)
from datetime import timedelta
from fastapi import Form

router = APIRouter(prefix="/Auth", tags=["Authentication"])


@router.post("/registration")
def register(
    username: str = Form(...),
    password: str = Form(...),
    nationality: str = Form(...),
    route: str = Form("tasks"),
    db: Session = Depends(get_db),
):
    user_exists = db.query(Task).filter(Task.username == username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="user already exists")
    if route != "tasks":
        raise HTTPException(status_code=400, detail="wrong route")
    password = str(password)
    hashed_password = hash_password(password)
    new_user = Task(
        username=username.strip(),
        password=hashed_password,
        nationality=nationality.strip(),
        route=route.strip(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "status": "success",
        "message": f"{username} registered successfully",
        "data": {"name": username.strip(), "country": nationality},
    }


@router.post("/logins")
def login(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(Task).filter(Task.username == username.strip()).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.username, "nationality": user.nationality},
        expires_delta=token_expires,
    )
    return {
        "status": "success",
        "message": f" {username} logged in successfully",
        "data": {"access_token": access_token, "token_type": "bearer"},
    }
