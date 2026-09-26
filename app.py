import csv
import io
import uuid

import requests
from flask import Flask, request
from pydantic import BaseModel

app = Flask(__name__)


class Hospital(BaseModel):
    name: str
    address: str
    phone: str | None = None
    creation_batch_id: str


@app.get("/")
def hello_paribus():
    return {"Hello": "Paribus"}


@app.post("/hospitals/bulk")
def upload_csv():
    if "file" not in request.files:
        return error_object(400, "No file uploaded")
    file = request.files["file"]
    if not allowed_filetype(file.filename):
        return error_object(400, "Only csv files are supported")

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream, skipinitialspace=True)
    except UnicodeDecodeError:
        return error_object(400, "csv file not utf-8 formatted")

    hospitals = validated_hospital(reader)

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


def validated_hospital(reader) -> list[Hospital]:

    batch_id = str(uuid.uuid4())
    hospitals = [Hospital]

    for row in reader:
        name = row["name"].strip() if row["name"] else None
        address = row["address"].strip() if row["address"] else None

        if not name or not address:
            continue

        phone = row["phone"].strip() if row["phone"] else None
        hospital = Hospital(
            name=name,
            address=address,
            phone=phone,
            creation_batch_id=batch_id,
        )
        hospitals.append(hospital)

    return hospitals
