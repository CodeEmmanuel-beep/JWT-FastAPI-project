import math
import operator
from functools import reduce
from sqlalchemy.orm import Session
from body.body.dependencies.db_session import get_db
from body.models_sql import Calculate
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from body.body.verify_jwt import verify_mathematician

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


@router.post("/calculate")
def mathing(
    username: str,
    numbers: str,
    operation: str,
    result: float | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_mathematician),
):
    calc = Calculate(
        username=username,
        numbers=numbers,
        operation=operation,
        time_of_calculation=datetime.now(timezone.utc),
    )

    numbers_list = [float(num.strip()) for num in numbers.split(",")]

    if operation == "add":
        result = sum(numbers_list)
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    elif operation == "minus":
        result = reduce(lambda x, y: x - y, numbers_list)
        logging.info(f"calculation done {operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {"message": "Calculation done successfully", "data": result}
    elif operation == "times":
        result = reduce(operator.mul, numbers_list)
        logging.info(f"calculation done {operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    elif operation == "divide":
        try:
            result = reduce(operator.truediv, numbers_list)
        except ZeroDivisionError:
            raise HTTPException(status_code=400, detail="Cannot divide by zero")
        logging.info(f"calculation done {operation}, result{result} ")
        calc.result = result
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return {
            "message": "Calculation done successfully",
            "data": result,
        }
    elif operation == "sqrt":
        result = math.sqrt(numbers_list[0])
        logging.info(f"calculation done {operation}, result{result} ")
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


@router.get("/retrieve all datas")
def get_all(
    db: Session = Depends(get_db), payload: dict = Depends(verify_mathematician)
):
    data = db.query(Calculate).all()
    if not data:
        return {"message": "no file stored"}
    return {"total": len(data), "calculations": data}


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
    db: Session = Depends(get_db), payload: dict = Depends(verify_mathematician)
):
    data = db.query(Calculate).all()
    if data:
        sorted_calcs = sorted(
            data,
            key=lambda x: x.time_of_calculation,
            reverse=True,
        )
        return sorted_calcs
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
