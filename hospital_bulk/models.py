from pydantic import BaseModel


class Hospital(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    creation_batch_id: str | None = None
