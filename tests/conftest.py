import json
import uuid

import pytest

from hospital_bulk import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def make_multipart(content, filename="a.csv"):
    if isinstance(content, str):
        content = content.encode()
    body = (
        f'--x\r\nContent-Disposition: form-data; name="file"; '
        f'filename="{filename}"\r\n\r\n'
    ).encode() + content + b"\r\n--x--"
    return {"data": body, "content_type": "multipart/form-data; boundary=x"}


class FakeUpstreamResponse:
    def __init__(self, status_code=200, hospital_id=1):
        self.status_code = status_code
        self.content = json.dumps(
            {
                "id": hospital_id,
                "name": "x",
                "address": "y",
                "phone": None,
                "creation_batch_id": str(uuid.uuid4()),
                "active": False,
                "created_at": "2026-01-01T00:00:00Z",
            }
        ).encode()


@pytest.fixture()
def multipart():
    return make_multipart
