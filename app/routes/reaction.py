from sqlalchemy.orm import Session
from app.models_sql import React, Blog, Comment, ReactionType, Share, ShareType
from app.log.logger import get_loggers
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import timezone, datetime
from app.body.dependencies.db_session import get_db
from app.body.verify_jwt import verify_token
from sqlalchemy import select, func
from app.models import Sharing, Sharer, StandardResponse, Blogger

router = APIRouter(prefix="/Reaction", tags=["Reactions"])
logger = get_loggers("react")


@router.post("/react")
async def react_type(
    reaction_type: str,
    blog: str | None = None,
    comment: str | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    if not user_id:
        logger.warning("Unauthorized reaction attempt")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    try:
        reaction_enum = ReactionType(reaction_type)
    except ValueError:
        logger.warning(f"Invalid reaction type '{reaction_type}' by user {user_id}")
        raise HTTPException(status_code=400, detail="invalid reaction type")
    if (blog is None and comment is None) or (blog is not None and comment is not None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="must input one reaction"
        )
    if blog:
        target = db.get(Blog, blog)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="must react on existing blog(s)",
            )
    if comment:
        target = db.get(Comment, comment)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="must react on existing comment(s)",
            )
    stmt = select(React).where(React.user_id == user_id)
    if blog:
        stmt = stmt.where(React.blog_id == blog)
    if comment:
        stmt = stmt.where(React.comment_id == comment)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        existing.type = reaction_enum
        existing.time_of_reaction = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        logger.info(f"User {user_id} updated reaction {existing.id}")
        return {"message": "Reaction updated", "reaction": existing.type}

    new_react = React(
        user_id=user_id,
        type=reaction_enum,
        blog_id=blog,
        comment_id=comment,
        time_of_reaction=datetime.now(timezone.utc),
    )
    if blog:
        target.reacts_count = (target.reacts_count or 0) + 1
    if comment:
        target.reacts_count = (target.reacts_count or 0) + 1
    db.add(new_react)
    db.commit()
    db.refresh(new_react)
    logger.info(f"User {user_id} added new reaction {new_react.id}")
    return {"message": "Reaction added", "reaction": new_react.id}


@router.post(
    "/share", response_model=StandardResponse, response_model_exclude_none=True
)
async def sharing(
    share: Sharer,
    react_type: str | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token),
):
    user_id = payload.get("user_id")
    if not user_id:
        logger.warning("Forbidden: user_id missing in payload")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    share_emu = None
    if share.type:
        try:
            share_emu = ShareType(react_type)
            # share.type )  # .value if isinstance(share.type, ShareType) else share.type)
            logger.info("Share type parsed: %s", share_emu)
        except ValueError:
            logger.error("Invalid share type: %s", share.type)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="input a valid reaction"
            )
    blog_id = getattr(share, "blog_id", None)
    blog = db.get(Blog, blog_id)
    if not blog:
        logger.error("Blog not found. blog_id: %s", blog_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    new_share = Share(
        user_id=user_id,
        type=share_emu,
        content=share.content,
        blog_id=share.blog_id,
        time_of_share=datetime.now(timezone.utc),
    )
    blog.share_count = (blog.share_count or 0) + 1
    db.add(new_share)
    db.commit()
    db.refresh(new_share)
    logger.info("New share created. share_id: %s, user_id: %s", new_share.id, user_id)
    data = Sharer.model_validate(new_share)
    return StandardResponse(status="success", message="blog shared", data=data)
