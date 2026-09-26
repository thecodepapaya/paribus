import io
from csv import DictReader

from flask import Blueprint, request

from .upstream import activate_hospital, upload_hospital
from .validation import validated_hospital

bp = Blueprint("hospitals", __name__)

import uuid


@bp.get("/")
def hello_paribus():
    return {"Hello": "Paribus"}


@bp.post("/hospitals/bulk")
def upload_csv():
    if "file" not in request.files:
        return error_object(400, "No file uploaded")
    file = request.files["file"]
    if not allowed_filetype(file.filename):
        return error_object(400, "Only csv files are supported")

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = DictReader(stream, skipinitialspace=True)
    except UnicodeDecodeError:
        return error_object(400, "csv file not utf-8 formatted")

    batch_id = str(uuid.uuid4())
    hospitals = validated_hospital(reader, batch_id)

    for hospital in hospitals:
        upload_hospital(hospital)

    activate_hospital(batch_id)

    return {}


def allowed_filetype(filename: str) -> bool:
    if "." not in filename:
        return False
    return filename.rsplit(".", 1)[1] == "csv"


def error_object(status: int, message: str, details: str | None = None):
    response = {"error": message}
    if details:
        response["details"] = details
    return (response, status)
