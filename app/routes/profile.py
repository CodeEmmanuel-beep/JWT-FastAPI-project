from app.models_sql import (
    Blog,
    User,
    Calculate,
    Comment,
    Expense,
    Priority,
    Market,
    Task,
    Share,
)
from app.models import (
    Blogger,
    UserResponse,
    Commenter,
    TaskResponse,
    MarketResponse,
    CalculateRes,
    Priority_Response,
    Expense_Response,
    Sharer,
)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from app.body.verify_jwt import verify_token
from app.models import (
    PaginatedMetadata,
    PaginatedResponse,
)
from sqlalchemy import select, func
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/Information", tags=["Profile"])


@router.get(
    "/view_profile",
)
async def view(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    offset = (page - 1) * limit
    stmt = select(User).where(User.username == username)
    total = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one_or_none()
    user = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    users = PaginatedMetadata[UserResponse](
        items=[UserResponse.model_validate(item) for item in user],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Blog).where(Blog.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    blog = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    blogs = PaginatedMetadata[Blogger](
        items=[Blogger.model_validate(item) for item in blog],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Comment).where(Comment.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    comment = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    counter = PaginatedMetadata[Commenter](
        items=[Commenter.model_validate(item) for item in comment],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Task).where(Task.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    task = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    tasks = PaginatedMetadata[TaskResponse](
        items=[TaskResponse.model_validate(item) for item in task],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Calculate).where(Calculate.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    calc = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    calcs = PaginatedMetadata[CalculateRes](
        items=[CalculateRes.model_validate(item) for item in calc],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Expense).where(Expense.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    expense = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    expen = PaginatedMetadata[Expense_Response](
        items=[Expense_Response.model_validate(item) for item in expense],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Priority).where(Priority.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    priority = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    prio = PaginatedMetadata[Priority_Response](
        items=[Priority_Response.model_validate(item) for item in priority],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Market).where(Market.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    market = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    mark = PaginatedMetadata[MarketResponse](
        items=[MarketResponse.model_validate(item) for item in market],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    stmt = select(Share).where(Share.user_id == user_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    sha = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    shar = PaginatedMetadata[Sharer](
        items=[Sharer.model_validate(i) for i in sha],
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )

    return {
        "success": "your full profile",
        "user": users,
        "blogs": blogs,
        "comments": counter,
        "tasks": tasks,
        "calculations": calcs,
        "expenditure": expen,
        "finance_guage": prio,
        "Market": mark,
        "shares": shar,
    }
