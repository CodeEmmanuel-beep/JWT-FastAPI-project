from sqlalchemy.orm import Session, selectinload
from app.models_sql import Task
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, delete
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta
from app.body.dependencies.db_session import get_db
from fastapi import HTTPException, Depends, Query
from app.body.verify_jwt import verify_token
from app.models import (
    TaskResponse,
    PaginatedResponse,
    StandardResponse,
    PaginatedMetadata,
)
from typing import List
from app.log.logger import get_loggers

router = APIRouter(prefix="/Tasks", tags=["Routine"])
logger = get_loggers("tasks")


@router.get("/secure_zone")
async def secure(username: str = Depends(verify_token)):
    return {"message": f"welcome {username}, you are verified"}


@router.post("/create")
async def create_tasks(
    days_to_execution: int,
    description: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=403, detail="Username mismatch. Unauthorized task creation."
        )
    day_of_execution = datetime.now(timezone.utc) + timedelta(days=days_to_execution)
    new_task = Task(
        user_id=user_id,
        description=description,
        days_to_execution=days_to_execution,
        day_of_execution=day_of_execution,
        time_of_implementation=datetime.now(timezone.utc),
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    logger.info(f"task successfully created by {username}. task: {description}")
    return {"task saved": new_task.description}


@router.put("/update", response_model=StandardResponse)
async def update_task(
    task_id: int,
    new_days_to_execution: int | None = None,
    new_description: str | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=403, detail="Username mismatch. Unauthorized task creation."
        )
    stmt = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.warning(f"{username}, tried updating a nonexistent task")
        raise HTTPException(status_code=409, detail="task not found")
    if new_days_to_execution is not None:
        data.days_to_execution = new_days_to_execution
        data.day_of_execution = datetime.now(timezone.utc) + timedelta(
            days=new_days_to_execution
        )
        data.time_of_implementation = datetime.now()
    if new_description is not None:
        data.description = new_description
        data.time_of_implementation = datetime.now(timezone.utc)
    db.commit()
    db.refresh(data)
    logger.info(f"task successfully updated from by {username}")
    return StandardResponse(
        status="success",
        message="Task updated successfully",
        data={
            "new deadline": new_days_to_execution,
            "new_description": new_description,
            "time of update": datetime.now(timezone.utc),
        },
    )


@router.get(
    "/list_tasks",
    response_model=StandardResponse[PaginatedMetadata[TaskResponse]],
    response_model_exclude_none=True,
)
async def view_all_tasks(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    logger.info(
        f"Fetching tasks for user_id={user_id}, username={username}, page={page}, limit={limit}"
    )
    offset = (page - 1) * limit
    stmt = select(Task).where(Task.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    tasks = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    if not tasks:
        logger.warning(f"all tasks queried, but none found for {username}")
        return StandardResponse(status="success", message="No tasks found")
    data = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(task) for task in tasks],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info(
        f"all tasks fetched successfully by {username}, page={page}, limit={limit}, total={total}"
    )
    return StandardResponse(status="success", message="tasks data", data=data)


@router.get(
    "/search",
    response_model=StandardResponse[PaginatedMetadata[TaskResponse]],
    response_model_exclude_none=True,
)
async def search_tasks(
    description: str,
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
    stmt = select(Task).where(Task.user_id == user_id)
    stmt = stmt.where(Task.description.ilike(f"%{description}%"))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    results = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    data = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(item) for item in results],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info(f"{username} did a global search for tasks")
    return StandardResponse(status="success", message="requested task data", data=data)


@router.get(
    "/retrieve_specific_tasks/{tasks_id}",
    response_model=StandardResponse[TaskResponse],
    response_model_exclude_none=True,
)
async def fetch_some(
    task_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    result = db.execute(stmt).scalar_one_or_none()
    if not result:
        logger.warning(f"{username} unsuccessfully queried task with id {task_id}")
        return StandardResponse(
            status="failure", message="Task not found or access denied"
        )
    data = TaskResponse.model_validate(result)

    logger.info(f"{username}, fetched for task with id {task_id}")
    return StandardResponse(status="success", message="requested data", data=data)


@router.get("/mark_complete", response_model=StandardResponse)
async def completed(
    task_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    tasks = db.execute(stmt).scalar_one_or_none()
    if not tasks:
        logger.warning(
            f"{username}, tried marking an invalid id as complete, id attempted, {task_id}"
        )
        return StandardResponse(
            status="failure", message="Task not found or access denied"
        )
    tasks.complete = True
    logger.info(
        f"{username} successfully marked task with task id '{task_id}' as complete"
    )
    try:
        db.commit()
    except IntegrityError:
        logger.info(f"Integrity error by {username}")
        db.rollback()
        return StandardResponse(
            status="failure", message="Duplicate entry or constraint violation"
        )
    db.refresh(tasks)
    return {
        "status": "success",
        "message": "completed task",
        "data": {
            "id": tasks.id,
            "username": username,
            "description": tasks.description,
            "completed": "Yes",
        },
    }


@router.get(
    "/completed_tasks",
    response_model=StandardResponse[PaginatedMetadata[TaskResponse]],
    response_model_exclude_none=True,
)
async def completed_data(
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
    stmt = select(Task).where(Task.user_id == user_id, Task.complete.is_(True))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    data = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    logger.info(f"{username} successfully queried completed tasks")
    check = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(task) for task in data],
        pagination=PaginatedResponse(
            page=page,
            limit=limit,
            total=total,
        ),
    )
    return StandardResponse(
        status="success",
        message="task executed",
        data=check,
    )


@router.get(
    "/undone_tasks",
    response_model=StandardResponse[PaginatedMetadata[TaskResponse]],
    response_model_exclude_none=True,
)
async def not_complete(
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
    stmt = select(Task).where(Task.user_id == user_id, Task.complete.is_(False))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    data = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    logger.info(f"{username} successfully queried uncompleted tasks")
    check = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(task) for task in data],
        pagination=PaginatedResponse(
            page=page,
            limit=limit,
            total=total,
        ),
    )
    return StandardResponse(
        status="success",
        message="task executed",
        data=check,
    )


@router.get(
    "/expired_deadline",
    response_model=StandardResponse[PaginatedMetadata[TaskResponse]],
    response_model_exclude_none=True,
)
async def expired_deadline(
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
    now = datetime.now(timezone.utc)
    stmt = select(Task).where(
        Task.user_id == user_id,
        Task.day_of_execution <= now,
        Task.complete.is_(False),
    )
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    data = (
        db.execute(
            stmt.order_by(Task.day_of_execution.asc()).offset(offset).limit(limit)
        )
        .scalars()
        .all()
    )
    logger.info(f"{username} successfully queried expired tasks")
    check = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(task) for task in data],
        pagination=PaginatedResponse(
            page=page,
            limit=limit,
            total=total,
        ),
    )
    return StandardResponse(status="success", message="task executed", data=check)


@router.delete("/clear all")
async def delete_all(
    db: Session = Depends(get_db), payload: dict = Depends(verify_token)
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = delete(Task).where(Task.user_id == user_id)
    data = db.execute(stmt)
    if data.rowcount == 0:
        logger.warning(f"{username}, tried deleting a blank database")
        return {"no data to clear"}
    db.commit()
    logger.info(f"{username} successfully wiped their database")
    return {"message": "data wiped"}


@router.delete("/erase", response_model=StandardResponse)
async def delete_one(
    task_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Task).where(Task.user_id == user_id, Task.id == task_id)
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.warning(
            f"{username}, tried deleting a nonexistent task, task id: {task_id}"
        )
        return {"status": "no data", "message": "invalid field"}
    logger.info("deleted tasks %s", task_id)
    db.delete(data)
    db.commit()
    return {
        "status": "success",
        "message": "deleted task",
        "data": {
            "id": data.id,
            "username": username,
            "description": data.description,
            "deleted": "Yes",
        },
    }
