from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime, timezone
from enum import Enum

T = TypeVar("T")


class UserResponse(BaseModel):
    id: Optional[int]
    email: str
    username: str
    name: str
    age: int
    nationality: str
    model_config = ConfigDict(from_attributes=True)


class CalculateRes(BaseModel):
    id: int
    operation: str
    numbers: str
    result: Optional[float] = None
    time_of_calculation: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class dev(BaseModel):
    union: str


class dev_n(BaseModel):
    username: str
    name: str
    nationality: str
    union: str


class TaskResponse(BaseModel):
    id: Optional[int]
    user_id: int
    description: Optional[str]
    days_to_execution: int
    day_of_execution: Optional[datetime]
    complete: bool = False
    status: Optional[str]
    time_of_implementation: Optional[datetime]

    @computed_field
    def days_remaining(self) -> int:
        remaining = self.day_of_execution - datetime.now()
        seconds = remaining.total_seconds()
        if seconds <= 0:
            return "expired"
        days = int(seconds // 86400)
        hours = round(int(seconds % 86400) / 3600, 1)
        minutes = round(int(seconds % 86400) / 3600 / 60, 1)
        if days > 1:
            return f"'{days}' days,'{hours}' hrs, '{minutes}' mins"
        elif hours > 1:
            return f"'{hours}' hrs, '{minutes}' mins"
        else:
            return f"'{minutes}' mins"

    model_config = ConfigDict(from_attributes=True)


class MarketResponse(BaseModel):
    id: Optional[int]
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


class Expense_Response(BaseModel):
    id: Optional[int]
    income: float
    days_until_next_income: float
    feasible_budget: float
    savings_percentage: float
    status: Optional[str]
    message: Optional[str]
    data: Optional[str]
    time_of_budgetting: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class Priority_Response(BaseModel):
    id: Optional[int]
    essentials: float
    extras: float
    income: float
    status: Optional[str]
    message: Optional[str]
    data: Optional[str]
    time_stamp: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class ReactionsSummary(BaseModel):
    like: int = 0
    love: int = 0
    angry: int = 0
    laugh: int = 0
    wow: int = 0
    sad: int = 0


class Commenter(BaseModel):
    id: Optional[int] = None
    blog_id: int
    content: str = Field(..., max_length=180)
    reacts_count: int | None = None
    reactions: List[ReactionsSummary] = Field(default_factory=list)
    time_of_post: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class Blogger(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., max_length=50)
    content: str = Field(...)
    comments_count: int | None = None
    reacts_count: int | None = None
    share_count: int | None = None
    reaction: List[ReactionsSummary] = Field(default_factory=list)
    comments: List[Commenter] = Field(default_factory=list)
    time_of_post: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class Sharing(Enum):
    love = "love"
    angry = "angry"
    laugh = "laugh"
    wow = "wow"
    sad = "sad"


class Sharer(BaseModel):
    id: Optional[int] = None
    blog_id: int
    type: Optional[Sharing] = None
    content: Optional[str] = None
    blog: Blogger = Field(default_factory=list)
    time_of_share: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
