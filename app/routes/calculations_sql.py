import operator
from functools import reduce
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from app.models_sql import Calculate
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query
from pathlib import Path
from app.body.verify_jwt import verify_token
from app.models import (
    PaginatedResponse,
    CalculateRes,
    StandardResponse,
    PaginatedMetadata,
)
from app.log.logger import get_loggers
from sqlalchemy import select, func, delete

router = APIRouter(prefix="/maths", tags=["Calculations"])
logger = get_loggers("calculations")


@router.get("/security zone")
async def secure(payload: dict = Depends(verify_token)):
    return {"message": "Welcome, mathematician"}


@router.post("/calculate")
async def calculator(
    numbers: str,
    operation: str,
    result: float | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=403, detail="unauthorizes accesss")
    calc = Calculate(
        user_id=user_id,
        numbers=numbers,
        operation=operation,
        result=result,
        time_of_calculation=datetime.now(timezone.utc),
    )

    num = [float(n.strip()) for n in numbers.split(",")]

    if operation == "add":
        result = sum(num)
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        logger.info(f"Addition result: {result}")
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    elif calc.operation == "minus":
        result = reduce(lambda x, y: x - y, num)
        logging.info(f"calculation done {calc.operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        logger.info(f"Subtraction result: {result}")
        return {"message": "Calculation done successfully", "data": result}
    elif calc.operation == "times":
        result = reduce(operator.mul, num)
        logging.info(f"calculation done {calc.operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        logger.info(f"Multiplication result: {result}")
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    elif calc.operation == "divide":
        try:
            result = reduce(operator.truediv, num)
        except ZeroDivisionError:
            logger.error("Division by zero encountered.")
            raise HTTPException(status_code=400, detail="Cannot divide by zero")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        logger.info(f"Division result: {result}")
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    else:
        logger.warning(f"Unsupported operation requested: {calc.operation}")
        return {"message": "Invalid operation"}


@router.get(
    "/view_all",
    response_model=StandardResponse[PaginatedMetadata[CalculateRes]],
    response_model_exclude_none=True,
)
async def get_all_calculations(
    db: Session = Depends(get_db),
    page: int = (Query(1, ge=1)),
    limit: int = (Query(10, le=100)),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Calculate).where(Calculate.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    logger.info(f"Ttal calculations found for {username}: {total}")
    result = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    logger.info(f"Fetched {len(result)} calculation records for page {page}")
    data = PaginatedMetadata[CalculateRes](
        items=[CalculateRes.model_validate(t) for t in result],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info(f"Successfully fetched calculations for mathematician: {username}")
    return StandardResponse(
        status="success", message="fetched tasks successfully", data=data
    )


@router.get(
    "/filter",
    response_model=StandardResponse[PaginatedMetadata[CalculateRes]],
    response_model_exclude_none=True,
)
async def search_calculations(
    operation: str,
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
    stmt = select(Calculate).where(Calculate.user_id == user_id)
    stmt = stmt.where(Calculate.operation.ilike(f"%{operation}%"))
    logger.info(f"Applied operation filter: {operation}")
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    logger.info(f"Total calculations found: {total}")
    result = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    logger.info(f"Fetched {len(result)} calculations for page {page}")
    data = PaginatedMetadata[CalculateRes](
        items=[CalculateRes.model_validate(t) for t in result],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )

    logger.info(f"Search completed successfully for: {username}")
    return StandardResponse(status="success", message="requested data", data=data)


@router.get(
    "/retrieve_specific_calculations/{calcs_id}",
    response_model=StandardResponse[CalculateRes],
    response_model_exclude_none=True,
)
async def fetch_some(
    calc_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Calculate).where(
        Calculate.user_id == user_id, Calculate.id == calc_id
    )
    result = db.execute(stmt).scalar_one_or_none()
    if not result:
        logger.warning(
            f"No calculation found with id {calc_id} for mathematician {username}"
        )
        return StandardResponse(status="failure", message="invalid id")
    data = CalculateRes.model_validate(result)
    logger.info(
        f"Successfully retrieved calculation with id {calc_id} for mathematician {username}"
    )
    return StandardResponse(status="success", message="requested data", data=data)


@router.get(
    "/recent Calculations",
    response_model=StandardResponse[PaginatedMetadata[CalculateRes]],
    response_model_exclude_none=True,
)
async def recent_calculations(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Calculate).where(Calculate.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    logger.info(f"Total calculations available for {username}: {total}")
    stmt = stmt.order_by(Calculate.time_of_calculation.desc())
    data = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    logger.info(f"Fetched {len(data)} recent calculation records for page {page}")
    mark = PaginatedMetadata[CalculateRes](
        items=[CalculateRes.model_validate(it) for it in data],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info(
        f"Successfully fetched recent calculations for mathematician: {username}"
    )
    return StandardResponse(
        status="success", message="most recent calculations fetched properly", data=mark
    )


@router.delete("/clear all")
async def clear(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = delete(Calculate).where(Calculate.user_id == user_id)
    data = db.execute(stmt)
    if data.rowcount == 0:
        logger.warning(f"No calculations found to delete for mathematician: {username}")
        return {"message": "no available data"}
    db.commit()
    logger.info(f"All calculations successfully deleted for mathematician: {username}")
    return {"message": "data wiped"}


@router.delete("/erase", response_model=StandardResponse)
async def delete_one(
    calc_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Calculate).where(
        Calculate.user_id == user_id, Calculate.id == calc_id
    )
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.warning(
            f"No calculation found with id {calc_id} for mathematician {user_id}"
        )
        return {"status": "no data", "message": "invalid field"}
    db.delete(data)
    db.commit()
    logger.info(f"Successfully deleted calculation id {calc_id}")
    return {
        "status": "success",
        "message": "section successfully deleted",
        "data": {
            "id": data.id,
            "operation": data.operation,
            "mathematician": username,
        },
    }
