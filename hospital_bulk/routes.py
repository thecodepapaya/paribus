import uuid
from datetime import datetime, timezone

from flask import Blueprint, request

from .commons import InvalidCsvException, error_object, success_object
from .upstream import activate_hospital, upload_hospital
from .validation import parsed_hospitals, validated_csv, validated_hospital

bp = Blueprint("hospitals", __name__)


@bp.get("/")
def hello_paribus():
    return {"Hello": "Paribus"}


@bp.post("/hospitals/bulk/validate")
def validate_csv():
    try:
        data = validated_csv(request)
    except InvalidCsvException as e:
        return error_object(400, e.message)

    row_count = len(data)
    hospitals = parsed_hospitals(data, None)
    valid_hospitals = len(validated_hospital(hospitals))

    return success_object(
        "CSV format is valid",
        200,
        {
            "total_rows": row_count,
            "invalid_rows": row_count - valid_hospitals,
            "valid_hospitals": valid_hospitals,
        },
    )


@bp.post("/hospitals/bulk")
def upload_csv():
    try:
        data = validated_csv(request)
    except InvalidCsvException as e:
        return error_object(400, e.message)

    batch_id = str(uuid.uuid4())
    hospitals = validated_hospital(parsed_hospitals(data, batch_id))

    if not hospitals:
        return error_object(400, "No valid hospital to upload")

    start = datetime.now(timezone.utc)

    uploaded_hospitals: list = []
    for hospital in hospitals:
        res = upload_hospital(hospital)
        if res.status_code == 200:
            uploaded_hospitals.append(hospital)

    if not uploaded_hospitals:
        return error_object()

    response = activate_hospital(batch_id)

    end = datetime.now(timezone.utc)

    return {
        "batch_id": batch_id,
        "total_hospitals": len(hospitals),
        "invalid_rows": len(data) - len(hospitals),
        "processed_hospitals": len(uploaded_hospitals),
        "failed_hospitals": len(hospitals) - len(uploaded_hospitals),
        "processing_time_seconds": (end - start).total_seconds(),
        "batch_activated": response.status_code == 200,
        "hospitals": [h.model_dump(mode="json") for h in uploaded_hospitals],
    }
