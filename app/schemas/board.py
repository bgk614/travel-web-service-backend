from pydantic import BaseModel

class Board(BaseModel):
    title: str
    contents: str
    created_by: str