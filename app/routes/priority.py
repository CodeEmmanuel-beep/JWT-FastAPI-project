from fastapi import Depends, Query, APIRouter, HTTPException
from sqlalchemy import select, func, delete
from datetime import datetime, timezone
from app.models_sql import Priority, User
from app.models import (
    StandardResponse,
    PaginatedMetadata,
    PaginatedResponse,
    Priority_Response,
)
from app.body.verify_jwt import verify_token
from app.body.dependencies.db_session import get_db
from sqlalchemy.orm import Session
from app.log.logger import get_loggers

router = APIRouter(prefix="/Pocket_Health", tags=["Debt_Saver"])
logger = get_loggers("priority")


@router.get("/security_check")
async def secure(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    return {"message": "welcome, in whatever you do make sure you avoid debts"}


@router.post("/Priorities", response_model=StandardResponse)
async def budget_wisely(
    essentials: float,
    extras: float,
    income: float,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        logger.warning(
            "Unauthorized budget creation attempt detected (no user_id in payload)"
        )
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    budget = Priority(
        user_id=user_id,
        essentials=essentials,
        extras=extras,
        income=income,
        time_stamp=datetime.now(timezone.utc),
    )
    total = essentials + extras
    if total > income:
        logger.warning(
            f"Overbudget detected for user '{username}': total={total}, income={income}"
        )
        budget.status = "danger"
        budget.message = "your budget will put you in debt"
        budget.data = f"total_expenses: {total}"
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return StandardResponse(
            status="danger",
            message="your budget will put you in debt",
            data={"total expense": total},
        )
    elif total == income:
        logger.info(f"User '{username}' has no savings: total={total}, income={income}")
        budget.status = "unsafe"
        budget.message = "your budget will leave you with no savings"
        budget.data = f"total expenses: {total}"
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return StandardResponse(
            status="unsafe",
            message="your budget will leave you with no savings",
            data={
                "total_expenses": total,
            },
        )
    elif extras > income * 0.49:
        logger.warning(
            f"High extras spending detected for user '{username}': extras={extras}, income={income}"
        )
        budget.status = "unsafe"
        budget.message = "you should priotorize savings, your extras should never consume 50 percent of your income"
        budget.data = f"budget of non-essential: {extras}"
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return StandardResponse(
            status="unsafe",
            message="you should priotorize savings, your extras should never consume 50 percent of your income",
            data={
                "budget of non-essential": extras,
            },
        )
    elif total < income / 100 * 80:
        savings = round(income - total, 2)
        budget.status = "perfect"
        budget.message = f"congratulations you have a budget of {total} against an income of {income} "
        budget.data = f"savings after budget: {savings}"
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return StandardResponse(
            status="perfect",
            message=f"congratulations you have a budget of {total} against an income of {income} ",
            data={
                "savings after budget": savings,
            },
        )

    else:
        logger.info(
            f"Okay budgeting for user '{username}': total={total}, income={income}"
        )
        budget.status = "okay"
        budget.message = (
            "Your budget is within range, but consider increasing your savings."
        )
        budget.data = f"total_expenses: {total}"
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return StandardResponse(
            status="okay",
            message="Your budget is within range, but consider increasing your savings.",
            data={"total_expenses": total},
        )


@router.get(
    "/retrieve_all_datas",
    response_model=StandardResponse[PaginatedMetadata[Priority_Response]],
    response_model_exclude_none=True,
)
async def view_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        logger.warning(
            "Unauthorized access attempt detected in view_all (no user_id in payload)"
        )
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Priority).where(Priority.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    retrieve = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    data = PaginatedMetadata[Priority_Response](
        items=[Priority_Response.model_validate(item) for item in retrieve],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info("view_all endpoint completed successfully")
    return StandardResponse(
        status="success", message="for requested data check below", data=data
    )


@router.get(
    "/filter",
    response_model=StandardResponse[PaginatedMetadata[Priority_Response]],
    response_model_exclude_none=True,
)
async def search(
    username: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    if not user_id:
        logger.warning("Unauthorized filter attempt detected (no user_id in payload)")
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Priority).where(Priority.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    stmt = stmt.where(Priority.user.has(User.username.ilike(f"%{username}%")))
    result = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    data = PaginatedMetadata(
        items=[Priority_Response.model_validate(t) for t in result],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info("search endpoint (/filter) completed successfully")
    return StandardResponse(status="success", message="requested data", data=data)


@router.get(
    "/retrieve_specific_priorities/{pri_id}",
    response_model=StandardResponse[Priority_Response],
    response_model_exclude_none=True,
)
async def fetch_some(
    pri_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    if not user_id:
        logger.warning(
            "Unauthorized data retrieval attempt detected (no user_id in payload)"
        )
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    result = db.execute(
        select(Priority).where(Priority.user_id == user_id, Priority.id == pri_id)
    ).scalar_one_or_none()
    if not result:
        logger.warning(
            f"No Priority record found for user_id={user_id}, pri_id={pri_id}"
        )
        return StandardResponse(status="failure", message="invalid id")
    data = Priority_Response.model_validate(result)
    logger.info("fetch_some endpoint completed successfully")
    return StandardResponse(status="success", message="requested data", data=data)


@router.delete("/clear all")
async def clear(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        logger.warning("Unauthorized clear attempt detected (no user_id in payload)")
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = delete(Priority).where(Priority.user_id == user_id)
    data = db.execute(stmt)
    if data.rowcount == 0:
        return {"message:": "no available data"}
    logger.info("clear endpoint completed successfully")
    db.commit()
    return {"message": "data wiped"}


@router.delete("/erase", response_model=StandardResponse)
async def delete_one(
    priority_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        logger.warning("Unauthorized delete attempt detected (no user_id in payload)")
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Priority).where(
        Priority.user_id == user_id, Priority.id == priority_id
    )
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        return {"status": "no data", "message": "invalid field"}
    ("deleted tasks %s", priority_id)
    db.delete(data)
    db.commit()
    logger.info("delete_one endpoint completed successfully")
    return {
        "status": "success",
        "message": "section successfully deleted",
        "data": {
            "id": data.id,
            "user": username,
        },
    }
