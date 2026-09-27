import uuid

from flask import Blueprint, request

from . import service
from .commons import (
    InvalidCsvException,
    MaxCsvLimitException,
    error_object,
    success_object,
)
from .validation import parsed_hospitals, validated_csv

bp = Blueprint("hospitals", __name__)


@bp.get("/")
def hello_paribus():
    return {"Hello": "Paribus"}


@bp.post("/hospitals/bulk/validate")
def validate_csv():
    try:
        data = validated_csv(request)
        _ = parsed_hospitals(data, str(uuid.uuid4()))
        return success_object(200, f"CSV is valid, total_rows {len(data)}")
    except InvalidCsvException as e:
        return error_object(400, e.message)
    except MaxCsvLimitException as e:
        return error_object(400, e.message)


@bp.post("/hospitals/bulk")
def upload_csv():
    try:
        return service.upload_bulk(request)
    except InvalidCsvException as e:
        return error_object(400, e.message)
    except MaxCsvLimitException as e:
        return error_object(400, e.message)
