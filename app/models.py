from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class Description(BaseModel):
    description: str


class Post(BaseModel):
    description: str
    name: str
    nationality: str
    __tablename__: str


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
    route: str
    result: Optional[float] = None


class CalculateRes(BaseModel):
    id: int
    mathematician: str
    route: str
    operation: Optional[str] = None
    numbers: Optional[str] = None
    result: Optional[float] = None
    time_of_calculation: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class dev(BaseModel):
    union: str


class dev_n(BaseModel):
    developer_name: str
    route: str
    union: str


class TaskResponse(BaseModel):
    id: Optional[int]
    description: Optional[str]
    route: str
    complete: bool = False
    nationality: str
    time_of_execution: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class MarketResponse(BaseModel):
    id: Optional[int]
    developer_name: str
    route: str
    section: Optional[int]
    trade: Optional[str]
    traders: Optional[int]
    sales_per_day: Optional[float]
    taxes: Optional[str]
    union: Optional[str]
    time_of_commencement: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    page: int
    limit: int
    total: int


class PaginatedMetadata(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginatedResponse


class StandardResponse(BaseModel, Generic[T]):
    status: str
    message: str
    data: Optional[T] = None
