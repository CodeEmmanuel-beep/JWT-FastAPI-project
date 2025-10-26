from fastapi import Depends, HTTPException, APIRouter, status
from app.body.dependencies.auth_jwt import (
    verify_secret,
    get_fingerprint,
    create_access_token,
    get_hashed_secret,
)
from app.models_sql import Calculate
from datetime import timedelta
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from fastapi import Form

router = APIRouter(prefix="/Mathematician Auth", tags=["Secured Calculations"])

TRUE_SECRETS = {"pie", "radius", "trig", "fraction"}


@router.post("/registration")
def register(
    mathematician: str = Form(...),
    mathematician_secret: str = Form(...),
    db: Session = Depends(get_db),
):
    if mathematician_secret not in TRUE_SECRETS:
        raise HTTPException(
            status_code=403, detail="access denied, you do not know the secret"
        )
    fingerprint = get_fingerprint(mathematician_secret)
    calc = db.query(Calculate.mathematician_secret).all()
    for (stored_secret,) in calc:
        if get_fingerprint(stored_secret) and stored_secret == fingerprint:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="you can not tell the same secret twice",
            )
    hashed_secret = get_hashed_secret(mathematician_secret)
    new_mathematician = Calculate(
        mathematician=mathematician.strip(), mathematician_secret=hashed_secret
    )
    db.add(new_mathematician)
    db.commit()
    db.refresh(new_mathematician)
    return {mathematician: "you are successfully registerd, welcome"}


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
        .filter(Calculate.mathematician.strip() == mathematician.strip())
        .first()
    )
    if not calc or not verify_secret(mathematician_secret, calc.mathematician_secret):
        raise HTTPException(status_code=403, detail="access denied, invalid entry")
    token_expires = timedelta(minutes=60)
    create_access = create_access_token(
        data={
            "sub": calc.mathematician,
            "mathematician_secret": calc.mathematician_secret,
        },
        expires_delta=token_expires,
    )
    return {"access token": create_access, "token_type": "bearer"}
