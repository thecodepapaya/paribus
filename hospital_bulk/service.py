import concurrent.futures
import uuid
from datetime import datetime, timezone

from flask import Request

from .commons import error_object
from .models import CsvHospital, UploadedHospital
from .upstream import activate_hospital, upload_hospital
from .validation import parsed_hospitals, validated_csv


def upload_bulk(request: Request):
    start = datetime.now(timezone.utc)
    batch_id = str(uuid.uuid4())
    data = validated_csv(request)
    hospitals = parsed_hospitals(data, batch_id)

    if not hospitals:
        return error_object(400, "No valid hospital to upload")

    processed_hospitals: list[tuple[CsvHospital, UploadedHospital | None]] = []
    processed_count = 0
    failed_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        responses = executor.map(upload_hospital, hospitals)

    for hospital, response in zip(hospitals, responses):
        if response is not None and response.status_code == 200:
            processed_count += 1
            processed_hospitals.append(
                (hospital, UploadedHospital.model_validate_json(response.content))
            )
            continue
        failed_count += 1
        processed_hospitals.append((hospital, None))

    if processed_count == 0:
        return error_object(400, "No hospitals uploaded, cannot mark active")

    response = activate_hospital(batch_id)
    end = datetime.now(timezone.utc)
    is_batch_activated = response is not None and response.status_code == 200

    return {
        "batch_id": batch_id,
        "total_hospitals": len(hospitals),
        "processed_hospitals": processed_count,
        "failed_hospitals": failed_count,
        "processing_time_seconds": (end - start).total_seconds(),
        "batch_activated": is_batch_activated,
        "hospitals": [
            {
                "row": csv_hospital.row_id,
                "hospital_id": None
                if uploaded_hospital is None
                else uploaded_hospital.id,
                "name": csv_hospital.name,
                "status": "created_and_activated"
                if uploaded_hospital is not None and is_batch_activated
                else "created"
                if uploaded_hospital is not None
                else "failed",
            }
            for csv_hospital, uploaded_hospital in processed_hospitals
        ],
    }
