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
    id: Optional[int]
    description: str
    complete: bool = False
    nationality: str

    model_config = ConfigDict(from_attributes=True)


class CalculateResponse(BaseModel):
    operation: str
    numbers: str
    result: Optional[float] = None

    class Config:
        model_config = ConfigDict(from_attributes=True)


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
