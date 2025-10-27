from app.models_sql import Market
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException, Depends, Query
import logging
from pathlib import Path
from app.body.verify_jwt import verify_developer, augument
from app.models import dev_n, MarketResponse, PaginatedResponse
from typing import List

router = APIRouter(prefix="/Market Sections_sql", tags=["Contract"])
LOGFILE = Path("market.log")
LOGFILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    filename=LOGFILE,
    format="%(asctime)s %(levelname)s %(message)s",
)


@router.get("/Security")
def secure(payload: dict = Depends(verify_developer)):
    return {"welcome": "Developer, you are verified"}


@router.get(
    "/reveal_all_market_sections",
    response_model=PaginatedResponse[MarketResponse],
    response_model_exclude_none=True,
)
def get_all(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    payload: dict = Depends(verify_developer),
):
    offset = (page - 1) * limit
    total = db.query(Market).count()
    mark = db.query(Market).offset(offset).limit(limit).all()
    data = [MarketResponse.model_validate(item) for item in mark]
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data,
    }


@router.get(
    "/search", response_model=List[MarketResponse], response_model_exclude_none=True
)
def locator(
    trade: str | None = None,
    union: str | None = None,
    taxes: str | None = None,
    db: Session = Depends(get_db),
):
    locate = db.query(Market)
    if trade:
        locate = locate.filter(Market.trade.ilike(f"%{trade}%"))
    if union:
        locate = locate.filter(Market.union.ilike(f"%{union}%"))
    if taxes:
        locate = locate.filter(Market.taxes.ilike(f"%{taxes}%"))
    result = locate.all()
    return result


@router.get("/fetch required_market_sections")
def getting_some(
    section: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_developer),
):
    Mark = db.query(Market).filter(Market.section == section).first()
    if not Mark:
        return {"message": "section not found"}
    return Mark


@router.post("/market_section")
def dev(
    section: int,
    trade: str,
    traders: int,
    sales: float,
    taxes: str,
    data: dev_n = Depends(augument),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_developer),
):
    mark = Market(
        section=section,
        trade=trade,
        traders=traders,
        sales_per_day=sales,
        taxes=taxes,
        union=data.union,
        developer_name=data.developer_name,
    )
    logging.info("Section Name %s", section)
    logging.info("Trade Type %s", mark.trade)
    logging.info("Number of Traders %s", traders)
    logging.info("Sales Per Day %s", mark.sales_per_day)
    logging.info("Taxes Applied %s", taxes)
    logging.info("Union Name %s", data.union)
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return {"message": "section developed successfully"}


@router.put("/update")
def change(
    section: str,
    trade: str,
    traders: str | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_developer),
):
    data = db.query(Market).filter(Market.section == section).first()
    if not data:
        raise HTTPException(status_code=400, detail="invalid section")
    data.trade = trade
    data.traders = traders
    logging.info("section update %s", section, trade)
    db.commit()
    db.refresh(data)
    return {"message": "update successful"}


@router.delete("/clear_all")
def clear(db: Session = Depends(get_db), payload: dict = Depends(verify_developer)):
    data = db.query(Market).all()
    if not data:
        return {f"no {data} to clear"}
    for item in data:
        db.delete(item)
    db.commit()
    return {"message": "data successfully wiped"}


@router.delete("/erase")
def delete_one(
    section: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_developer),
):
    data = db.query(Market).filter(Market.section == section).first()
    if not data:
        return {"message": "invalid task id"}
    logging.info("deleted tasks %s", section)
    db.delete(data)
    db.commit()
    return {"message": f"{section} deleted"}
