from datetime import datetime

from pydantic import BaseModel


class Hospital(BaseModel):
    name: str
    address: str
    phone: str | None = None


class CsvHospital(Hospital):
    row_id: int
    creation_batch_id: str | None


class UploadedHospital(Hospital):
    id: int
    creation_batch_id: str
    active: bool
    created_at: datetime
