from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f"{name}.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def make_http_exception_handler():
    async def http_exception_handler(request: Request, exc: HTTPException):
        router_name = getattr(request.scope.get("router"), "prefix", "root")
        logger = get_logger(f"http_{router_name.strip("/") or "root"}")
        logger.warning(f"HTTPException: {exc.detail} | Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail},
        )

    return http_exception_handler


def make_validation_exception_handler():

    async def validation_exception_handler(request: Request, exc: ValidationError):
        router_name = getattr(request.scope.get("router"), "prefix", "root")
        logger = get_logger(f"validation_{router_name.strip("/") or "root"}")
        logger.warning(f"Validation Error on {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "status": "FAILED",
                "message": "Validation Error",
                "detail": exc.errors(),
            },
        )

    return validation_exception_handler


def make_global_exception_handler():

    async def global_exception_handler(request: Request, exc: Exception):
        router_name = getattr(request.scope.get("router"), "prefix", "root")
        logger = get_logger(f"exce_{router_name.strip("/") or "root"}")
        logger.error(f"unhandled errors on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "internal server error"},
        )

    return global_exception_handler
