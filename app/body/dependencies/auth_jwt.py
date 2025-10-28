from datetime import timezone, timedelta, datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import status, Depends, HTTPException
from fastapi import Security
from dotenv import load_dotenv
import os

SECRET_KEY = "-B05Ab54rkxOyFEWSEaceHzhb_xxZE7KT1O2ebnmDe8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    if len(password) < 8:
        raise HTTPException(
            status_code=401, detail="weak password, should be morethan 7 letters"
        )
    return pwd_context.hash(password)


def verify_code(plain_code: int, hashed_code: str):
    return pwd_context.verify(str(plain_code), hashed_code)


def get_hashed_code(code: int) -> str:
    return pwd_context.hash(str(code))


def verify_secret(plain_secret: str, hashed_secret: str):
    return pwd_context.verify(plain_secret, hashed_secret)


def get_hashed_secret(secret: str):
    return pwd_context.hash(secret)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
