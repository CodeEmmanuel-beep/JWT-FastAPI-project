from fastapi import Depends, Query, APIRouter, HTTPException, Form
from sqlalchemy import select, func
from datetime import datetime, timezone
from app.models_sql import Expense
from app.models import (
    StandardResponse,
    PaginatedMetadata,
    PaginatedResponse,
    Expense_Response,
)
from app.body.verify_jwt import verify_token
from app.body.dependencies.db_session import get_db
from sqlalchemy.orm import Session
from app.log.logger import get_loggers

router = APIRouter(prefix="/Expense_Tracker", tags=["Wise_Spending"])
logger = get_loggers("expense")


@router.get("/security_check")
async def secure(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    return {"welcome, track your expenses"}


@router.post("/spendstar", response_model=StandardResponse)
async def broke_shield(
    income: float,
    days_until_next_income: int,
    savings_percentage: float = Query(ge=0, le=100),
    feasible_budget: float = Form("0"),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")

    shield = Expense(
        days_until_next_income=days_until_next_income,
        savings_percentage=savings_percentage,
        income=income,
        user_id=user_id,
        feasible_budget=feasible_budget,
        time_of_budgetting=datetime.now(timezone.utc),
    )
    feasible_budget = income / days_until_next_income
    save = feasible_budget / 100 * (100 - savings_percentage)
    shield.feasible_budget = feasible_budget
    shield.status = "success"
    shield.message = "accurately determined your feasible budget"
    shield.data = f"amount you can spend per day without getting broke:  {feasible_budget:.2f},  amount you can spend per day and end up saving {savings_percentage} percent of your income:  {save} "
    db.add(shield)
    db.commit()
    db.refresh(shield)
    logger.info(
        f"Spend plan successfully created for user '{username}' (feasible_budget={feasible_budget:.2f}, save={save})"
    )
    return StandardResponse(
        status="success",
        message="accurately determined your feasible budget",
        data={
            "amount you can spend per day without getting broke": f"{feasible_budget:.2f}",
            f"amount you can spend per day and end up saving {savings_percentage} percent of your income": save,
        },
    )


@router.get(
    "/retrieve_all",
    response_model=StandardResponse[PaginatedMetadata[Expense_Response]],
    response_model_exclude_none=True,
)
async def retrieve_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Expense).where(Expense.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    retrieve = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    if not retrieve:
        logger.warning(
            f"No expenses found for user '{username}' (page={page}, limit={limit})"
        )
    else:
        logger.info(
            f"User '{username}' successfully retrieved {len(retrieve)} expense(s) (page={page}, limit={limit})"
        )
    data = PaginatedMetadata[Expense_Response](
        items=[Expense_Response.model_validate(item) for item in retrieve],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    return StandardResponse(
        status="success", message="for requested data check below", data=data
    )


@router.get(
    "/retrieve_specific_expenses/{ex_id}",
    response_model=StandardResponse[Expense_Response],
    response_model_exclude_none=True,
)
async def fetch_some(
    ex_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Expense).where(Expense.user_id == user_id, Expense.id == ex_id)
    result = db.execute(stmt).scalar_one_or_none()
    if not result:
        logger.warning(
            f"Failed attempt: User '{username}' tried to retrieve non-existent expense ID {ex_id}"
        )
        return StandardResponse(status="failure", message="invalid id")
    logger.info(f"Successful retrieval: User '{username}' retrieved expense ID {ex_id}")
    data = Expense_Response.model_validate(result)
    return StandardResponse(status="success", message="requested data", data=data)


@router.delete("/clear all")
async def clear(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Expense).where(Expense.user_id == user_id)
    data = db.execute(stmt).scalars().all()
    if not data:
        logger.warning(
            f"User '{username}' attempted to clear data, but no records were found"
        )
        return {"message:": "no available data"}
    for item in data:
        db.delete(item)
    db.commit()
    logger.info(
        f"User '{username}' successfully cleared all expense data ({len(data)} record(s) deleted)"
    )
    return {"message": "data wiped"}


@router.delete("/erase", response_model=StandardResponse)
async def delete_one(
    expense_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Expense).where(Expense.user_id == user_id, Expense.id == expense_id)
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.warning(
            f"Failed deletion attempt: User '{username}' tried to delete non-existent expense ID {expense_id}"
        )
        return {"status": "no data", "message": "invalid field"}
    db.delete(data)
    db.commit()
    logger.info(f"User '{username}' successfully deleted expense ID {data.id}")
    return {
        "status": "success",
        "message": "section successfully deleted",
        "data": {
            "id": data.id,
            "user": username,
        },
    }
