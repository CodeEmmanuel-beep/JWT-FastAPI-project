from fastapi import Depends, HTTPException, APIRouter, status
from app.body.dependencies.auth_jwt import (
    verify_secret,
    create_access_token,
    get_hashed_secret,
)
from app.models_sql import Calculate
from datetime import timedelta
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from fastapi import Form
from dotenv import load_dotenv
import os

router = APIRouter(prefix="/Mathematician Auth", tags=["Secured Calculations"])
load_dotenv()
TRUE_SECRETS = set(os.getenv("TRUE_SECRETS", "").split(","))
if not TRUE_SECRETS:
    raise RuntimeError("TRUE_SECRETS NOT ACCESSED")


@router.post("/registration")
def register(
    mathematician: str = Form(...),
    mathematician_secret: str = Form(...),
    route: str = Form("calculations"),
    db: Session = Depends(get_db),
):
    if mathematician_secret not in TRUE_SECRETS:
        raise HTTPException(
            status_code=403, detail="access denied, you do not know the secret"
        )
    if route != "calculations":
        raise HTTPException(status_code=403, detail="wrong route")
    hashed_secret = get_hashed_secret(mathematician_secret)
    new_mathematician = Calculate(
        mathematician=mathematician.strip(),
        mathematician_secret=hashed_secret.strip(),
        route=route.strip(),
    )
    db.add(new_mathematician)
    db.commit()
    db.refresh(new_mathematician)
    return {
        "status": "success",
        "message": f"{mathematician} registered successfully",
        "data": {"name": mathematician.strip(), "path": route},
    }


@router.post("/logins")
def login(
    mathematician: str = Form(...),
    mathematician_secret: str = Form(...),
    db: Session = Depends(get_db),
):
    if mathematician_secret not in TRUE_SECRETS:
        raise HTTPException(
            status_code=403, detail="access denied, you do not know the secret"
        )
    calc = (
        db.query(Calculate)
        .filter(Calculate.mathematician == mathematician.strip())
        .first()
    )
    if not calc:
        raise HTTPException(status_code=403, detail="access denied, invalid entry")
    if not verify_secret(mathematician_secret.strip(), calc.mathematician_secret):
        raise HTTPException(status_code=403, detail="hidden secret")
    token_expires = timedelta(minutes=60)
    create_access = create_access_token(
        data={
            "sub": calc.mathematician,
            "route": calc.route,
        },
        expires_delta=token_expires,
    )
    return {
        "status": "success",
        "message": f"{mathematician} logged in successfully",
        "data": {"access_token": create_access, "token_type": "bearer"},
    }
