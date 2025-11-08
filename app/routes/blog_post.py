from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models import Blogger, PaginatedMetadata, PaginatedResponse, StandardResponse
from app.models_sql import Blog, User, React, Comment
from sqlalchemy.orm import Session
from app.body.dependencies.db_session import get_db
from datetime import datetime, timezone
from app.body.verify_jwt import verify_token
from app.log.logger import get_loggers
from app.models import ReactionsSummary

router = APIRouter(prefix="/Blogs", tags=["Expressions"])
logger = get_loggers("blogs")


def reactions(db: Session, blog_id: int) -> ReactionsSummary:
    counts = (
        db.execute(
            select(React.type, func.count(React.id))
            .where(React.blog_id == blog_id)
            .group_by(React.type)
            .order_by(React.type),
        )
    ).all()

    summary = {
        rtype.name if hasattr(rtype, "name") else rtype: count
        for rtype, count in counts
    }
    return ReactionsSummary(
        like=summary.get("like", 0),
        love=summary.get("love", 0),
        laugh=summary.get("laugh", 0),
        wow=summary.get("wow", 0),
        angry=summary.get("angry", 0),
        sad=summary.get("sad", 0),
    )


@router.get("/securit_check")
async def access(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    return {"message": "welcome to your blog"}


@router.post(
    "/expressionns", response_model=StandardResponse, response_model_exclude_none=True
)
async def express(
    blog: Blogger,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    username = payload.get("sub")
    user_id = payload.get("user_id")
    if not user_id:
        logger.warning(
            "Author mismatch: token author '%s' vs input author '%s'",
            username,
        )
        raise HTTPException(status_code=403, detail="forbidden entry")
    blogs = Blog(
        user_id=user_id,
        title=blog.title,
        content=blog.content,
        time_of_post=datetime.now(timezone.utc),
    )
    db.add(blogs)
    db.commit()
    db.refresh(blogs)
    logger.info("Blog post successfully created by: %s", username)
    data = Blogger.model_validate(blogs)
    return StandardResponse(status="success", message="post successful", data=data)


@router.get(
    "/view_blogs",
    response_model=StandardResponse[PaginatedMetadata[Blogger]],
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
        raise HTTPException(status_code=403, detail="unauthorized access")
    offset = (page - 1) * limit
    stmt = select(Blog)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    logger.info("Total blogs found for '%s': %d", username, total)
    result = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    logger.info("Number of blogs retrieved on this page: %d", len(result))
    items = []
    for blog in result:
        blog_data = Blogger.model_validate(blog)
        blog_data.reaction = reactions(db, blog.id)
        items.append(blog_data)
    data = PaginatedMetadata[Blogger](
        items=items,
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info("Paginated data prepared successfully for '%s'", username)
    return StandardResponse(
        status="success", message="below lies all your expressions", data=data
    )


@router.get(
    "/search",
    response_model=StandardResponse[PaginatedMetadata[Blogger]],
    response_model_exclude_none=True,
)
async def filter(
    author: str | None = None,
    title: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=403, detail="unauthorized access")
    offset = (page - 1) * limit
    stmt = select(Blog)
    if author:
        stmt = stmt.where(Blog.user.has(User.name.ilike(f"%{author}%")))
    if title:
        stmt = stmt.where(Blog.title.ilike(f"%{title}%"))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    logger.info("Total filtered blogs: %d", total)
    results = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    logger.info("Number of blogs retrieved on this page: %d", len(results))
    items = []
    for blog in results:
        blog_data = Blogger.model_validate(blog)
        blog_data.reaction = reactions(db, blog.id)
        items.append(blog_data)
    data = PaginatedMetadata[Blogger](
        items=items,
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    return StandardResponse(
        status="success", message="below lies all your expressions", data=data
    )


@router.get(
    "/discover",
    response_model=StandardResponse[PaginatedMetadata[Blogger]],
    response_model_exclude_none=True,
)
async def view_trending(
    sorting: str = Query("recent", enum=["popular", "recent"]),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=403, detail="unauthorized access")
    offset = (page - 1) * limit
    stmt = select(Blog)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    logger.info("Total blogs for '%s': %d", username, total)
    if sorting == "recent":
        stmt = stmt.order_by(Blog.time_of_post.desc())
    if sorting == "popular":
        stmt = stmt.order_by(
            Blog.comments_count.asc(), Blog.share_count.asc(), Blog.reacts_count.asc()
        )
    stmt = stmt.offset(offset).limit(limit)
    result = db.execute(stmt).scalars().all()
    logger.info("Number of recent blogs retrieved: %d", len(result))
    items = []
    for blog in result:
        blog_data = Blogger.model_validate(blog)
        blog_data.reaction = reactions(db, blog.id)
        items.append(blog_data)
    data = PaginatedMetadata[Blogger](
        items=items,
        pagination=PaginatedResponse(page=page, limit=limit, total=total),
    )
    logger.info("Recent paginated data prepared successfully for '%s'", username)
    return StandardResponse(
        status="success", message="below lies all the recent expressions", data=data
    )


@router.get(
    "/retrieve_specific_blogs",
    response_model=StandardResponse[Blogger],
    response_model_exclude_none=True,
)
async def fetch_some(
    bl_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=403, detail="unauthorized access")
    stmt = select(Blog).where(Blog.id == bl_id)
    result = db.execute(stmt).scalar_one_or_none()
    if not result:
        logger.warning(f"No blog found with id {bl_id} for {username}")
        return StandardResponse(status="failure", message="invalid id")
    data = Blogger.model_validate(result)
    data.reaction = reactions(db, result.id)
    logger.info(f"Successfully retrieved blog with id {bl_id}: {data}")
    return StandardResponse(status="success", message="requested data", data=data)


@router.put("/edit", response_model=StandardResponse)
async def change(
    bl_id: int,
    title: str | None = None,
    content: str | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    username = payload.get("sub")
    stmt = select(Blog).where(Blog.user_id == user_id, Blog.id == bl_id)
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.warning(f"No blog found with id {bl_id} for {username}")
        raise HTTPException(status_code=400, detail="invalid section")
    if title:
        data.title = title
    if content:
        data.content = content
    data.time_of_post = datetime.now(timezone.utc)
    db.commit()
    db.refresh(data)
    stm = select(User).where(User.username == username)
    re = db.execute(stm).scalar_one_or_none()
    logger.info(f"Updating time_of_post for blog id {bl_id} to {data.time_of_post}")
    return {
        "status": "success",
        "message": "blog successfully updated",
        "data": {
            "id": data.id,
            "author": re.name,
            "title": data.title,
            "content": data.content,
            "nationality": re.nationality,
            "commencement": data.time_of_post,
        },
    }


@router.delete("/erase", response_model=StandardResponse)
async def delete_one(
    bl_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    username = payload.get("sub")
    user_id = payload.get("user_id")
    stmt = select(Blog).where(Blog.user_id == user_id, Blog.id == bl_id)
    data = db.execute(stmt).scalar_one_or_none()
    if not data:
        logger.warning(f"No blog found to delete with id {bl_id} for author {username}")
        return {"status": "no data", "message": "invalid field"}
    db.delete(data)
    db.commit()
    logger.info(f"Successfully deleted blog with id {bl_id}")
    return {
        "status": "success",
        "message": "blog successfully deleted",
        "data": {
            "id": data.id,
            "username": username,
            "title": data.title,
        },
    }


@router.delete("/clear all")
async def clear(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    username = payload.get("sub")
    user_id = payload.get("user_id")
    stmt = select(Blog).where(Blog.user_id == user_id)
    data = db.execute(stmt).scalars().all()
    if not data:
        logger.warning(f"No blogs found to clear for {username}")
        return {"message:": "no available data"}
    for item in data:
        db.delete(item)
    db.commit()
    logger.info(f"All blogs successfully deleted for {username}")
    return {"message": "data wiped"}
