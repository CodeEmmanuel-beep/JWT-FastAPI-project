from datetime import datetime, timezone
from fastapi import Security, status, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from app.models import (
    dev,
    dev_n,
)
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("can not access, SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM not accessible")

security_scheme = HTTPBearer()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        if payload.get("sub") is None:
            raise credentials_exception
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise HTTPException(status_code=401, detail="token has expired")
        return payload
    except JWTError:
        raise credentials_exception


def decode_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not authenticated",
        headers={"WWW-authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise credentials_exception
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="expired token"
            )
        return payload
    except JWTError:
        raise credentials_exception


def augument(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    data: dev = Depends(),
) -> dev_n:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return dev_n(
            union=data.union,
            username=payload.get("sub"),
            name=payload.get("name"),
            nationality=payload.get("nationality"),
        )
    except JWTError:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate"
        )
