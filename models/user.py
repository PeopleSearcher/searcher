from pydantic import BaseModel
from uuid import UUID, uuid4

from models.data import Phone


class Person(BaseModel):
    id: UUID = uuid4()  # generate random UUID
    fio: str
    phone: Phone
