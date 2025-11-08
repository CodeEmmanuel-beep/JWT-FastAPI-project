from datetime import timezone, timedelta, datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import status, Depends, HTTPException
from dotenv import load_dotenv
import re
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("could not access SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise RuntimeError("could not access ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str | int):
    if len(password) < 8:
        raise HTTPException(
            status_code=401,
            detail="weak password, password should be morethan 7 characters",
        )
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(
            status_code=401,
            detail="Weak password: must contain both letters and numbers.",
        )
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode["type"] = "access_token"
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_tokens(data: dict, expire_days=7):
    to_encode = data.copy()
    to_encode["type"] = "refresh_token"
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token
