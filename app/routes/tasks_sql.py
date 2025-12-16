from sqlalchemy.orm import Session
from app.models_sql import Task
from fastapi import APIRouter
from datetime import datetime, timezone
from app.body.dependencies.db_session import get_db
from fastapi import HTTPException, Depends, Query
import logging
from pathlib import Path
from app.body.verify_jwt import verify_token, enrich_input
from app.models import Post

router = APIRouter(prefix="/tasks", tags=["Routines"])
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


@router.put("/update/{task_id}")
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


@router.get("/retrieve_all")
def get_all_tasks(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    username: dict = Depends(verify_token),
):
    offset = (page - 1) * limit
    tasks = db.query(Task).offset(offset).limit(limit).all()
    total = db.query(Task).count()
    if not tasks:
        return "no file stored"
    return {"total": total, "page": page, "limit": limit, "tasks": tasks}


@router.get("/search")
def filtering(description: str | None = None, db: Session = Depends(get_db)):
    desc = db.query(Task)
    if description:
        desc = desc.filter(Task.description.ilike(f"%{description}%"))
    results = desc.all()
    if results:
        logging.info("search successful")
        return {"results": results}
    return {"message": "such tasks does not exist"}


@router.get("/retrieve_some/{task_id}")
def fetch_some(
    task_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    data = db.query(Task).filter(Task.id == task_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="task not found")
    logging.info("retrieved task %s", task_id)
    return {"this is your requested file": data}


@router.get("/mark_complete{task_id}")
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
        logging.info("marked task as complete %s", task_id)
        return {"message": f"{task_id } completed"}
    return "invalid id"


@router.get("/completed_tasks")
def completed_data(
    db: Session = Depends(get_db), username: str = Depends(verify_token)
):
    data = db.query(Task).filter(Task.complete == True).all()
    if data:
        logging.info("queried completed tasks")
        return {"you have completed these tasks": data, "total completed": len(data)}
    return {"message": "no tasks completed"}


@router.get("/undone_tasks")
def not_complete(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    data = db.query(Task).filter(Task.complete == False).all()
    if data:
        logging.info("queried undone tasks")
        return {
            "you have not completed these tasks": data,
            "total completed": len(data),
        }
    return {"message": "all task data found"}


@router.delete("/clear_all")
def clear(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    data = db.query(Task).all()
    if not data:
        return {f"no {data} to clear"}
    for item in data:
        db.delete(item)
    db.commit()
    logging.info("deleted tasks")
    return {"message": "data wiped"}


@router.delete("/erase/{task_id}")
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
    return {"message": f"{task_id} deleted"}
