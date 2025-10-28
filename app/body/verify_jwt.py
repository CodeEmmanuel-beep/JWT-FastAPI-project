from datetime import datetime, timezone
from fastapi import Security, status, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from app.models import Description, Post, CalculateResponse, secret, dev, dev_n
from dotenv import load_dotenv
import os

SECRET_KEY = "-B05Ab54rkxOyFEWSEaceHzhb_xxZE7KT1O2ebnmDe8"
load_dotenv()
ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM environment variable is missing or empty")

security_scheme = HTTPBearer()


def verify_mathematician(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
):
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        if payload.get("mathematician_secret") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="you are not a mathematician",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you are not a mathematician",
        )


def verify_developer(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
):
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        if payload.get("route") != "markets":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="you are not a developer",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a developer"
        )


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
        if payload.get("nationality") is None:
            raise credentials_exception
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise HTTPException(status_code=401, detail="token has expired")
        return payload
    except JWTError:
        raise credentials_exception


def enrich_input(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    body: Description = Depends(),
) -> Post:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return Post(
            description=body.description,
            name=payload.get("sub"),
            route=payload.get("route"),
            nationality=payload.get("nationality"),
        )
    except JWTError:
        return credentials_exception


def add_post(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    data: secret = Depends(),
) -> CalculateResponse:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return CalculateResponse(
            numbers=data.numbers,
            operation=data.operation,
            result=data.result,
            route=payload.get("route"),
            mathematician=payload.get("sub"),
        )
    except JWTError:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate"
        )


def augument(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    data: dev = Depends(),
) -> dev_n:
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return dev_n(
            route=payload.get("route"),
            union=data.union,
            developer_name=payload.get("sub"),
        )
    except JWTError:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate"
        )
