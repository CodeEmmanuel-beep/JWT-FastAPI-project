from app.routes import (
    tasks_sql,
    calculations_sql,
    market_sql,
    Expense,
    priority,
    blog_post,
    comment_stars,
    auth,
    profile,
)
from app.routes import reaction
from fastapi import Request, FastAPI, HTTPException, status
from pydantic import ValidationError
import uvicorn
import os
import time
from app.exceptions import get_logger
from app.exceptions import (
    make_global_exception_handler,
    make_http_exception_handler,
    make_validation_exception_handler,
)

app = FastAPI(title="Three Dimensions", version="1.0")


@app.middleware("http")
async def log_request(request: Request, call_next):
    start = time.time()
    try:
        process = await call_next(request)
    except Exception as exc:
        duration = time.time() - start
        logger = get_logger("requests")
        logger.error(
            f"{request.method}  {request.url.path} -error:{exc} - Duration: {duration:.4f}s"
        )
        raise
    duration = time.time() - start
    logger = get_logger("requests")
    logger.info(
        f"{request.method}  {request.url.path} - status:{process.status_code} - Duration: {duration:.4f}s"
    )
    return process


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(reaction.router)
app.include_router(tasks_sql.router)
app.include_router(priority.router)
app.include_router(Expense.router)
app.include_router(blog_post.router)
app.include_router(comment_stars.router)
app.include_router(calculations_sql.router)
app.include_router(market_sql.router)
app.add_exception_handler(HTTPException, make_http_exception_handler())
app.add_exception_handler(Exception, make_global_exception_handler())
app.add_exception_handler(ValidationError, make_validation_exception_handler())


@app.get("/", include_in_schema=False)
def home_page():
    return {
        "message": "Welcome to Three Dimensions API. Visit /docs to explore the endpoints."
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
