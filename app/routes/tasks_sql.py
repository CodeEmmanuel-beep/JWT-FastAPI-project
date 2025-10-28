from sqlalchemy.orm import Session
from app.models_sql import Task
from fastapi import APIRouter
from datetime import datetime, timezone
from app.body.dependencies.db_session import get_db
from fastapi import HTTPException, Depends, Query
import logging
from pathlib import Path
from app.body.verify_jwt import verify_token, enrich_input
from app.models import (
    Post,
    TaskResponse,
    PaginatedResponse,
    StandardResponse,
    PaginatedMetadata,
)
from typing import List

router = APIRouter(prefix="/Tasks", tags=["Routines"])
LOGFILE = Path("tasks.log")
LOGFILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    filename=LOGFILE,
    format="%(asctime)s %(levelname)s %(message)s",
)


@router.get("/secure_zone")
def secure(username: str = Depends(verify_token)):
    return {"message": f"welcome {username}, you are verified"}


@router.post("/create")
def create_tasks(
    data: Post = Depends(enrich_input),
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    new_task = Task(
        description=data.description,
        username=data.name,
        nationality=data.nationality,
        time_of_execution=datetime.now(timezone.utc),
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"task saved": new_task.description}


@router.put("/{task_id}")
def update_task(
    task_id: int,
    new_description: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    data = db.query(Task).filter(Task.id == task_id).first()
    if not data:
        raise HTTPException(status_code=409, detail="task not found")
    data.description = new_description
    data.time_of_execution = datetime.now()
    db.commit()
    db.refresh(data)
    return {"message": f"Task {task_id} updated successfully"}


@router.get(
    "/retrieve all",
    response_model=StandardResponse[PaginatedMetadata[TaskResponse]],
    response_model_exclude_none=True,
)
def get_all_tasks(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    username: str = Depends(verify_token),
):
    offset = (page - 1) * limit
    tasks = db.query(Task).offset(offset).limit(limit).all()
    total = db.query(Task).count()
    data = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(item) for item in tasks],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    if not tasks:
        return "no file stored"
    return StandardResponse(status="success", message="every task data", data=data)


@router.get(
    "/search",
    response_model=StandardResponse[PaginatedMetadata[TaskResponse]],
    response_model_exclude_none=True,
)
def filtering(
    description: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit
    total = db.query(Task).count()
    desc = db.query(Task)
    if description:
        desc = desc.filter(Task.description.ilike(f"%{description}%"))
    results = desc.offset(offset).limit(limit).all()
    data = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(item) for item in results],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    return StandardResponse(
        status="success", message="requested task data", data=data.model_dump()
    ).model_dump()


@router.get("/retrieve some/{tasks_id}")
def fetch_some(
    task_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    data = db.query(Task).filter(Task.id == task_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="task not found")
    return {"this is your requested file": data}


@router.get("/mark complete", response_model=StandardResponse)
def completed(
    task_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    tasks = db.query(Task).filter(Task.id == task_id).first()
    if tasks:
        tasks.complete = True
        db.commit()
        db.refresh(tasks)
        return {
            "status": "success",
            "message": "completed task",
            "data": {
                "id": tasks.id,
                "username": tasks.username,
                "description": tasks.description,
                "completed": "Yes",
            },
        }


@router.get("/completed tasks", response_model=List[TaskResponse])
def completed_data(
    db: Session = Depends(get_db), username: str = Depends(verify_token)
):
    data = db.query(Task).filter(Task.complete.is_(True)).all()
    if data:
        return data
    return []


@router.get(
    "/undone tasks", response_model=List[TaskResponse], response_model_exclude_none=True
)
def not_complete(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    data = db.query(Task).filter(Task.complete.is_(False)).all()
    if data:
        return data
    return []


@router.delete("/clear all")
def clear(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    data = db.query(Task).all()
    if not data:
        return {f"no {data} to clear"}
    for item in data:
        db.delete(item)
    db.commit()
    return {"message": "data wiped"}


@router.delete("/erase", response_model=StandardResponse)
def delete_one(
    task_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    data = db.query(Task).filter(Task.id == task_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="task not found")
    logging.info("deleted tasks %s", task_id)
    db.delete(data)
    db.commit()
    return {
        "status": "success",
        "message": "deleted task",
        "data": {
            "id": data.id,
            "username": data.username,
            "fescription": data.description,
            "deleted": "Yes",
        },
    }
