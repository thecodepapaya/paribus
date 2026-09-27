import io
from csv import DictReader

from flask import Request
from pydantic import ValidationError

from .commons import InvalidCsvException, MaxCsvLimitException
from .models import CsvHospital


def parsed_hospitals(data: list[dict], batch_id: str) -> list[CsvHospital]:
    hospitals: list[CsvHospital] = []

    for i, row in enumerate(data):
        if row.get("extra") is not None:
            raise InvalidCsvException(f"Extra fields in row at position {i + 1}")

        try:
            name = row.get("name")
            address = row.get("address")
            phone = row.get("phone")

            name = name.strip() or None if isinstance(name, str) else None
            address = address.strip() or None if isinstance(address, str) else None
            phone = phone.strip() or None if isinstance(phone, str) else None
            hospital = CsvHospital(
                row_id=i + 1,
                name=name,
                address=address,
                phone=phone,
                creation_batch_id=batch_id,
            )
            hospitals.append(hospital)
        except ValidationError:
            raise InvalidCsvException(f"Invalid row at position {i + 1}")

    return hospitals


def validated_csv(request: Request) -> list[dict]:
    if "file" not in request.files:
        raise InvalidCsvException("No file uploaded")
    file = request.files["file"]
    if not allowed_filetype(file.filename):
        raise InvalidCsvException("Only CSV files are supported")

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = DictReader(stream, skipinitialspace=True, restkey="extra")
    except UnicodeDecodeError:
        raise InvalidCsvException("CSV file not utf-8 formatted")

    required_keys = {"name", "address"}
    if reader.fieldnames and all(key in reader.fieldnames for key in required_keys):
        data = list(reader)
        if len(data) > 20:
            raise MaxCsvLimitException(len(data))
        return data

    raise InvalidCsvException("Missing required fields from CSV header - name, address")


def allowed_filetype(filename: str) -> bool:
    if "." not in filename:
        return False
    return filename.rsplit(".", 1)[1] == "csv"
