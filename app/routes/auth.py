from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models_sql import User
from app.body.dependencies.db_session import get_db
from app.body.dependencies.auth_jwt import (
    create_access_token,
    verify_password,
    hash_password,
    create_refresh_tokens,
)
from app.body.verify_jwt import verify_token, decode_token
from datetime import timedelta
from fastapi import Form
from app.log.logger import get_loggers
from app.database.scheduler import send_email_name

router = APIRouter(prefix="/Auth", tags=["Authentification"])
logger = get_loggers("auth")


@router.post("/registeration")
async def register(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    nationality: str = Form(...),
    db: Session = Depends(get_db),
):
    user_exists = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
    if user_exists:
        logger.warning(f"Registration failed: Username {username} already exists")
        raise HTTPException(status_code=400, detail="user already exists")
    email_exists = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if email_exists:
        logger.info(f"Registration failed {email} already exists")
        raise HTTPException(
            status_code=400, detail="email already in use by another user"
        )
    password = str(password)
    hashed_password = hash_password(password)
    new_user = User(
        email=email.strip(),
        username=username.strip(),
        password=hashed_password,
        name=name.strip(),
        age=age,
        nationality=nationality.strip(),
    )
    logger.info(f"Registration attempt for username: {username}, email: {email}")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    send_email_name.delay(
        subject="Registerd Successfully",
        body="welcome to beaut citi hope you enjoy your experience, customer support is always available if you need anything, thanks for being a partner",
        to_email=new_user.email,
    )
    logger.info(f"User {username} registered successfully")
    return {
        "status": "success",
        "message": f"{username} registered successfully",
        "data": {"name": username.strip(), "country": nationality},
    }


@router.post("/logins")
async def login(
    username: str, password: str, response: Response, db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.username == username.strip())
    ).scalar_one_or_none()
    if not user or not verify_password(password, user.password):
        logger.warning(f"Login failed for username: {username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "nationality": user.nationality,
            "name": user.name,
        },
        expires_delta=token_expires,
    )
    refresh_access = create_refresh_tokens(
        {
            "sub": user.username,
            "user_id": user.id,
            "nationality": user.nationality,
            "name": user.name,
        }
    )
    response.set_cookie(
        key="refresh", value=refresh_access, httponly=True, secure=False, samesite="lax"
    )
    logger.info(f"User {username} logged in successfully")
    return {
        "status": "success",
        "message": f" {username} logged in successfully",
        "data": {"access_token": access_token, "token_type": "bearer"},
    }


@router.post("/refresh")
async def refresh_token(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    token = request.cookies.get("refresh")
    logger.info("Refresh token attempt")
    if not token:
        logger.warning("Refresh token missing")
        raise HTTPException(status_code=401, detail="missing token")
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh_token":
        logger.warning("Invalid refresh token")
        raise HTTPException(status_code=401, detail="invalid refresh token")
    username = payload.get("sub")
    user_id = payload.get("user_id")
    name = payload.get("name")
    nationality = payload.get("nationality")
    new_access = create_access_token(
        {
            "sub": username,
            "user_id": user_id,
            "nationality": nationality,
            "name": name,
        }
    )
    new_refresh = create_refresh_tokens(
        {
            "sub": username,
            "user_id": user_id,
            "nationality": nationality,
            "name": name,
        }
    )
    response.set_cookie(
        key="refresh", value=new_refresh, httponly=True, samesite="lax", secure=False
    )

    logger.info(f"Refresh token successful for username: {username}")
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
async def sign_out(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh")
    response.delete_cookie("refresh")
    logger.info("User logged out successfully")
    return {"message": "logged out"}
