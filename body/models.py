from pydantic import BaseModel


class Description(BaseModel):
    description: str


class Post(BaseModel):
    description: str
    name: str
    nationality: str
