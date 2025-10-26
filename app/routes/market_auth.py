from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from fastapi import Depends, HTTPException, APIRouter
from app.models_sql import Market
from app.body.dependencies.auth_jwt import (
    verify_code,
    get_hashed_code,
    create_access_token,
)
from datetime import timedelta
from fastapi import Form

router = APIRouter(prefix="/Market Authentification", tags=["Secure Development"])

ACCESS_CODES = {20005, 30005, 40005, 50005}


@router.post("/registration")
def register(
    developer_code: int = Form(...),
    developer_name: str = Form(...),
    db: Session = Depends(get_db),
):
    if developer_code not in ACCESS_CODES:
        raise HTTPException(
            status_code=403, detail="access denied, invalid developer_code"
        )
    hashed_code = get_hashed_code(developer_code)
    mark = db.query(Market).filter(Market.developer_code == hashed_code).first()
    if mark:
        raise HTTPException(status_code=400, detail="developer is already registered")
    new_developer = Market(
        developer_code=hashed_code, developer_name=developer_name.strip()
    )
    db.add(new_developer)
    db.commit()
    db.refresh(new_developer)
    return {developer_name: "you are successfully registerd, welcome"}


@router.post("/logins")
def login(
    developer_code: int = Form(...),
    developer_name: str = Form(...),
    db: Session = Depends(get_db),
):
    if developer_code not in ACCESS_CODES:
        raise HTTPException(
            status_code=403, detail="access denied, invalid developer_code"
        )
    mark = (
        db.query(Market)
        .filter(Market.developer_name.strip() == developer_name.strip())
        .first()
    )
    if not mark or not verify_code(developer_code, mark.developer_code):
        raise HTTPException(status_code=401, detail="unauthorized developer")
    token_expires = timedelta(minutes=60)
    create_token = create_access_token(
        data={"sub": mark.developer_name, "code": mark.developer_code},
        expires_delta=token_expires,
    )
    return {"access_token": create_token, "token_type": "bearer"}
