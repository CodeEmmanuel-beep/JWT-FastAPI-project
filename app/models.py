from pydantic import BaseModel
from typing import Optional


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
