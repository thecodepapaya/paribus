from pydantic import BaseModel


class Hospital(BaseModel):
    name: str
    address: str
    phone: str | None = None
    creation_batch_id: str
