from fastapi import APIRouter, Depends, Query, HTTPException
from app.models import (
    StandardResponse,
    PaginatedResponse,
    PaginatedMetadata,
    Commenter,
    ReactionsSummary,
)
from app.models_sql import Comment, Blog, User, React
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from datetime import datetime, timezone
from app.body.verify_jwt import verify_token
from sqlalchemy import select, delete, func
from app.log.logger import get_loggers


router = APIRouter(prefix="/Comments", tags=["Counter_Expressions"])
logger = get_loggers("comments")


def react_summary(db: Session, comment_id) -> ReactionsSummary:
    counts = db.execute(
        select(React.type, func.count(React.id))
        .where(React.comment_id == comment_id)
        .group_by(React.type)
        .order_by(React.type)
    ).all()
    summary = {
        rtype.name if hasattr(rtype, "name") else rtype: count
        for rtype, count in counts
    }
    return ReactionsSummary(
        like=summary.get("like", 0),
        love=summary.get("love", 0),
        laugh=summary.get("laugh", 0),
        angry=summary.get("angry", 0),
        wow=summary.get("wow", 0),
        sad=summary.get("sad", 0),
    )


@router.get("/security_zone")
async def security(
    db: Session = Depends(get_db), payload: dict = Depends(verify_token)
):
    return {"message": "welcome to the comment section"}


@router.post(
    "/counter_expressions",
    response_model=StandardResponse,
    response_model_exclude_none=True,
)
async def c_express(
    comment: Commenter,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    target = db.get(Blog, comment.blog_id)
    if not target:
        logger.warning(f"No blog found with ID: {comment.blog_id}")
        return StandardResponse(status="failure", message="no such blog exists")
    target.comments_count = (target.comments_count or 0) + 1
    comments = Comment(
        user_id=user_id,
        content=comment.content,
        blog_id=comment.blog_id,
        time_of_post=datetime.now(timezone.utc),
    )
    db.add(comments)
    db.commit()
    db.refresh(comments)
    logger.info(
        f"Comment successfully committed to database by {username} with ID: {comments.id if hasattr(comments, 'id') else 'unknown'}"
    )
    data = Commenter.model_validate(comments)
    return StandardResponse(status="success", message="post successful", data=[data])


@router.get(
    "/view_comments",
    response_model=StandardResponse[PaginatedMetadata[Commenter]],
    response_model_exclude_none=True,
)
async def view(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    username = payload.get("sub")
    if username is None:
        logger.warning("Unauthorized access attempt — missing 'sub' in token payload.")
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Comment)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    result = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    items = []
    for comment in result:
        comment_data = Commenter.model_validate(comment)
        comment_data.reactions = react_summary(db, comment.id)
        items.append(comment_data)
    data = PaginatedMetadata[Commenter](
        items=items,
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info(f"Fetched {len(result)} comments for user={username} (page={page}).")
    return StandardResponse(
        status="success", message="below lies all your counters", data=data
    )


router.get(
    "/search",
    response_model=StandardResponse[PaginatedMetadata[Commenter]],
    response_model_exclude_none=True,
)


async def filter(
    username: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    if user_id is None:
        logger.warning(
            "Unauthorized access attempt — missing 'user_id' in token payload."
        )
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Comment)
    stmt = stmt.where(Comment.user.has(User.username.ilike(f"%{username}%")))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    results = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    items = []
    for comment in results:
        comment_data = Commenter.model_validate(comment)
        comment_data.reactions = react_summary(db, comment.id)
        items.append(comment_data)
    data = PaginatedMetadata[Commenter](
        items=items,
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info(
        f"Fetched {len(results)} comments matching username='{username}' (page={page}, limit={limit})."
    )
    return StandardResponse(
        status="success", message="below lies all your counters", data=data
    )


@router.get(
    "/retrieve_specific_counters",
    response_model=StandardResponse[Commenter],
    response_model_exclude_none=True,
)
async def fetch_some(
    com_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    username = payload.get("sub")
    logger.warning("Unauthorized access attempt — missing 'sub' in token payload.")
    if username is None:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Comment).where(Comment.id == com_id)
    result = db.execute(stmt).scalar_one_or_none()
    if not result:
        logger.info(f"No comment found for com_id={com_id}")
        return StandardResponse(status="failure", message="invalid id")
    data = Commenter.model_validate(result)
    data.reactions = react_summary(db, result.id)
    logger.info(f"Successfully fetched comment com_id={com_id} for user={username}")
    return StandardResponse(status="success", message="requested data", data=data)


@router.get(
    "/discover",
    response_model=StandardResponse[PaginatedMetadata[Commenter]],
    response_model_exclude_none=True,
)
async def trending(
    sorting=Query("recent", enum=["popular", "recent"]),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if username is None:
        logger.warning("Unauthorized access attempt — missing 'sub' in token payload.")
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    offset = (page - 1) * limit
    stmt = select(Comment)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    if sorting == "recent":
        stmt = stmt.order_by(Comment.time_of_post.desc())
    if sorting == "popular":
        stmt = stmt.order_by(Comment.reacts_count.asc())
    result = db.execute(stmt).scalars().all()
    items = []
    for comment in result:
        comment_data = Commenter.model_validate(comment)
        comment_data.reactions = react_summary(db, comment.id)
        items.append(comment_data)
    data = PaginatedMetadata[Commenter](
        items=items,
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info(
        f"Fetched {len(result)} recent comments for user={username} (page={page})"
    )
    return StandardResponse(
        status="success", message="below lies all the recent counters", data=data
    )


@router.put("/edit", response_model=StandardResponse)
async def change(
    blog_id: int,
    content: str | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        logger.warning(
            "Unauthorized access attempt — missing user_id in token payload."
        )
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Comment).where(Comment.user_id == user_id, Comment.id == blog_id)
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.debug(f"Updating content for blog_id={blog_id}")
        logger.info(
            f"Invalid edit attempt: blog_id={blog_id} not found for user_id={user_id}."
        )
        raise HTTPException(status_code=400, detail="invalid section")
    if content:
        data.content = content
    data.time_of_post = datetime.now(timezone.utc)
    db.commit()
    db.refresh(data)
    logger.info(
        f"Successfully edited blog_id={data.id} by user={username} (ID={user_id})"
    )
    return {
        "status": "success",
        "message": "edited counter",
        "data": {
            "id": data.id,
            "content": data.content,
            "commencement": data.time_of_post,
        },
    }


@router.delete("/erase", response_model=StandardResponse)
async def delete_one(
    blog_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        logger.warning(
            "Unauthorized access attempt — missing user_id in token payload."
        )
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = select(Comment).where(Comment.user_id == user_id, Comment.id == blog_id)
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.info(f"No blog found for blog_id={blog_id} and user_id={user_id}.")
        return {"status": "no data", "message": "invalid field"}
    target = db.get(Blog, data.blog_id)
    target.comments_count = max((target.comments_count or 1) - 1, 0)
    db.delete(data)
    db.commit()
    logger.info(
        f"Blog deleted successfully — blog_id={data.id}, user={username} (ID={user_id})"
    )
    return {
        "status": "success",
        "message": "blog successfully deleted",
        "data": {
            "id": data.id,
            "username": username,
        },
    }


@router.delete("/clear all")
async def clear(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not user_id:
        logger.warning(
            "Unauthorized access attempt detected — missing user_id in token payload."
        )
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    stmt = delete(Comment).where(Comment.user_id == user_id)
    data = db.execute(stmt)
    if data.rowcount == 0:
        logger.info(
            f"No comments found for user {username} (ID: {user_id}). Nothing deleted."
        )
        return {"message:": "no available data"}
    db.commit()
    logger.info(
        f"Successfully deleted {data.rowcount} comments for user {username} (ID: {user_id})."
    )
    return {"message": "data wiped"}
