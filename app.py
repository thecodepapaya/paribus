import csv
import io

from flask import Flask, request
from pydantic import BaseModel, ConfigDict

app = Flask(__name__)


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
        reader = csv.reader(stream)
        header = next(reader)
    except UnicodeDecodeError:
        return error_object(400, "csv file not utf-8 formatted")
    except StopIteration:
        return error_object(400, "csv file is empty")

    if header != ["name", "address", "phone"]:
        return error_object(
            400,
            "Ill-formatted csv header",
            "Headers must be in the format 'name,address,phone'",
        )

    for row in reader:
        hospital = validated_row(row)
        print(hospital)

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
