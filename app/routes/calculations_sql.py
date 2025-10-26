import math
import operator
from functools import reduce
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from app.models_sql import Calculate
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query
from pathlib import Path
from app.body.verify_jwt import verify_mathematician, add_post
from app.models import secret, CalculateResponse, PaginatedResponse
from typing import List

router = APIRouter(prefix="/Cal_Sql", tags=["Mathematics"])
LOGFILE = Path("calculations.log")
LOGFILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    filename=LOGFILE,
    format="%(asctime)s %(levelname)s %(message)s",
)


@router.get("/security zone")
def secure(payload: dict = Depends(verify_mathematician)):
    return {"Welcome, mathematician"}


@router.post("/calculate", response_model=List(CalculateResponse))
def mathing(
    data: CalculateResponse = Depends(add_post),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_mathematician),
):
    calc = Calculate(
        id=len(calc) + 1,
        number=data.numbers,
        operation=data.operation,
        result=data.result,
        mathematician=data.mathematician,
        time_of_calculation=datetime.now(timezone.utc),
    )

    numbers_list = [float(num.strip()) for num in calc.numbers.split(",")]

    if calc.operation == "add":
        result = sum(numbers_list)
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {
            "message": "Calculation done successfully",
            "data": CalculateResponse(
                mumbers=calc.numbers,
                operation=calc.operation,
                result=calc.result,
                mathematician=calc.mathematician,
            ),
        }
    elif calc.operation == "minus":
        result = reduce(lambda x, y: x - y, numbers_list)
        logging.info(f"calculation done {calc.operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {"message": "Calculation done successfully", "data": result}
    elif calc.operation == "times":
        result = reduce(operator.mul, numbers_list)
        logging.info(f"calculation done {calc.operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    elif calc.operation == "divide":
        try:
            result = reduce(operator.truediv, numbers_list)
        except ZeroDivisionError:
            raise HTTPException(status_code=400, detail="Cannot divide by zero")
        logging.info(f"calculation done {calc.operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    elif calc.operation == "sqrt":
        result = math.sqrt(numbers_list[0])
        logging.info(f"calculation done {calc.operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    else:
        raise HTTPException(status_code=400, detail="unsupported operation")


@router.get("/retrieve all datas", response_model=List[PaginatedResponse])
def get_all(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    payload: dict = Depends(verify_mathematician),
):
    offset = (page - 1) * limit
    total = db.query(Calculate).count()
    data = db.query(Calculate).offset(offset).limit(limit).all()
    if not data:
        return {"message": "no file stored"}
    return PaginatedResponse(total=total, page=page, limit=limit, data=data)


@router.get("/filter")
def search(operation: str, db: Session = Depends(get_all)):
    query = db.query(Calculate)
    if operation:
        query = query.filter(Calculate.operation.ilike(f"%{operation}%"))
    result = query.all()
    return {"result": result}


@router.get("/retrieve some/{calcs_id}")
def fetch_some(
    calc_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_mathematician),
):
    data = db.query(Calculate).filter(Calculate.id == calc_id).first()
    if not data:
        return {"message": "invalid id"}
    return data


@router.get("/recent Calculations")
def recent_calculations(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=10),
    limit: int = Query(10, le=100),
    payload: dict = Depends(verify_mathematician),
):
    offset = (page - 1) * limit
    total = db.query(Calculate).count()
    data = db.query(Calculate).offset(offset).limit(limit).all()
    if data:
        sorted_calcs = sorted(
            data,
            key=lambda x: x.time_of_calculation,
            reverse=True,
        )
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "most recent calculation": sorted_calcs,
        }
    else:
        return {"message": "no calculations found for this user"}


@router.delete("/clear all")
def clear(db: Session = Depends(get_db), payload: dict = Depends(verify_mathematician)):
    data = db.query(Calculate).all()
    if not data:
        return {"message:": "no available data"}
    for item in data:
        db.delete(item)
    db.commit()
    return {"message": "data wiped"}


@router.delete("/erase")
def delete_one(
    calc_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_mathematician),
):
    data = db.query(Calculate).filter(Calculate.id == calc_id).first()
    if not data:
        return {"message:": "invalid task id"}
    logging.info("deleted tasks %s", calc_id)
    db.delete(data)
    db.commit()
    return {"message": f"{calc_id} deleted"}
