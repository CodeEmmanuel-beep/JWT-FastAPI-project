from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


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
    username: str


class dev(BaseModel):
    developer_code: str


class dev_n(BaseModel):
    developer_name: str
    developer_code: str


class TaskResponse(BaseModel):
    id: int
    username: str
    description: str
    complete: bool = False
    nationality: str
    time_of_execution: datetime

    model_config = ConfigDict(from_attributes=True)


class CalculateResponse(BaseModel):
    id: int
    mathematician: str
    operation: str
    numbers: str
    result: Optional[float] = None
    time_of_calculation: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


class MarketResponse(BaseModel):
    id: int
    developer_name: str
    section: int
    trade: str
    traders: int
    sales_per_day: float
    taxes: str
    union: str

    class Config:
        model_config = ConfigDict(from_attributes=True)
