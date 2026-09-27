from flask import Blueprint, request

from . import service
from .commons import InvalidCsvException, MaxCsvLimitException, error_object

bp = Blueprint("hospitals", __name__)


@bp.get("/")
def hello_paribus():
    return {"Hello": "Paribus"}


@bp.post("/hospitals/bulk/validate")
def validate_csv():
    try:
        return service.validate_csv(request)
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
