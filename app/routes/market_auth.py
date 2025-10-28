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
from dotenv import load_dotenv
import os


router = APIRouter(prefix="/Market Authentication", tags=["Secure Development"])
load_dotenv()
ACCESS_CODES = set(map(int, os.getenv("ACCESS_CODES", "").split(",")))
if not ACCESS_CODES:
    raise RuntimeError("can not locate ACCESS_CODES")


@router.post("/registration")
def register(
    developer_code: int = Form(...),
    developer_name: str = Form(...),
    route: str = Form("markets"),
    db: Session = Depends(get_db),
):
    if developer_code not in ACCESS_CODES:
        raise HTTPException(
            status_code=403, detail="access denied, invalid developer_code"
        )
    if route != "markets":
        raise HTTPException(status_code=403, detail="wrong route")
    hashed_code = get_hashed_code(developer_code)
    new_developer = Market(
        developer_code=hashed_code,
        developer_name=developer_name.strip(),
        route=route.strip(),
    )
    db.add(new_developer)
    db.commit()
    db.refresh(new_developer)
    return {
        "status": "success",
        "message": f"{developer_name} registered successfully",
        "data": {"name": developer_name.strip(), "path": route},
    }


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
        db.query(Market).filter(Market.developer_name == developer_name.strip()).first()
    )
    if not mark or not verify_code(developer_code, mark.developer_code):
        raise HTTPException(status_code=401, detail="unauthorized developer")
    token_expires = timedelta(minutes=60)
    create_token = create_access_token(
        data={
            "sub": mark.developer_name,
            "route": mark.route,
        },
        expires_delta=token_expires,
    )
    return {
        "status": "success",
        "message": f"{developer_name} logged in successfully",
        "data": {"access_token": create_token, "token_type": "bearer"},
    }
