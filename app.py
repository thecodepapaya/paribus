import io
import uuid
from csv import DictReader

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


def validated_hospital(reader: DictReader[str], batch_id: str) -> list[Hospital]:

    hospitals: list[Hospital] = []

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


def upload_hospital(hospital: Hospital):
    payload = hospital.model_dump(mode="json")
    response = requests.post(
        "https://hospital-directory.onrender.com/hospitals/", json=payload
    )
    return response


def activate_hospital(batch_id: str):
    response = requests.patch(
        f"https://hospital-directory.onrender.com/hospitals/batch/{batch_id}/activate"
    )
    return response
