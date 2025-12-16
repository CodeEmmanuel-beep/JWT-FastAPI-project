from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing or not loaded from .env")
ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM is missing or not loaded from .env")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES is missing or not loaded from .env")

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


def get_fingerprint(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
