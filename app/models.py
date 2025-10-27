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
    operation: str
    numbers: str
    result: Optional[float] = None


class CalculateResponse(BaseModel):
    mathematician: str
    operation: Optional[str] = None
    numbers: Optional[str] = None
    result: Optional[float] = None


class CalculateRes(BaseModel):
    id: int
    mathematician: str
    operation: Optional[str] = None
    numbers: Optional[str] = None
    result: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class dev(BaseModel):
    union: str


class dev_n(BaseModel):
    developer_name: str
    union: str


class TaskResponse(BaseModel):
    id: Optional[int]
    description: Optional[str]
    complete: bool = False
    nationality: str

    model_config = ConfigDict(from_attributes=True)


class MarketResponse(BaseModel):
    id: Optional[int]
    developer_name: str
    section: Optional[int]
    trade: Optional[str]
    traders: Optional[int]
    sales_per_day: Optional[float]
    taxes: Optional[str]
    union: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    status: str = "success"
    page: int
    limit: int
    total: int
    data: List[T]
