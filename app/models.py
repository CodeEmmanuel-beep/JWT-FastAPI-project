from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Generic, TypeVar

T = TypeVar("T")


class Description(BaseModel):
    description: str


class Post(BaseModel):
    description: str
    name: str
    nationality: str


class plain(BaseModel):
    username: str


class secret(BaseModel):
    mathematician: str
    operation: str
    numbers: str


class dev(BaseModel):
    developer_code: str


class dev_n(BaseModel):
    developer_name: str
    developer_code: str


class TaskResponse(BaseModel):
    id: Optional[int]
    description: str
    complete: bool = False
    nationality: str

    model_config = ConfigDict(from_attributes=True)


class CalculateResponse(BaseModel):
    mathematician: str
    operation: Optional[str] = None
    numbers: Optional[str] = None
    result: Optional[float] = None


class MarketResponse(BaseModel):
    id: Optional[int]
    developer_name: str
    section: int
    trade: str
    traders: int
    sales_per_day: float
    taxes: str
    union: str

    class Config:
        model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    status: str = "success"
    page: int
    limit: int
    total: int
    data: List[T]
