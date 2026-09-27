import uuid
from unittest.mock import patch

from conftest import FakeUpstreamResponse

GOOD_CSV = "name,address,phone\nA Hospital,123 Main St,\nB Hospital,456 Side Ave,555\n"
BAD_ROW_CSV = "name,address,phone\nA Hospital,123 Main St,\n,456 Side Ave,\n"


def test_validate_accepts_valid_csv(client, multipart):
    r = client.post("/hospitals/bulk/validate", **multipart(GOOD_CSV))
    assert r.status_code == 200
    assert r.get_json() == {"message": "CSV is valid, total_rows 2"}


def test_validate_rejects_invalid_row(client, multipart):
    r = client.post("/hospitals/bulk/validate", **multipart(BAD_ROW_CSV))
    assert r.status_code == 400
    assert "Invalid row at position 2" in r.get_json()["error"]


def test_bulk_creates_and_activates(client, multipart):
    with patch(
        "hospital_bulk.service.upload_hospital",
        side_effect=[FakeUpstreamResponse(hospital_id=11), FakeUpstreamResponse(hospital_id=12)],
    ), patch(
        "hospital_bulk.service.activate_hospital", return_value=FakeUpstreamResponse()
    ):
        r = client.post("/hospitals/bulk", **multipart(GOOD_CSV))

    assert r.status_code == 200
    body = r.get_json()
    uuid.UUID(body["batch_id"])
    assert body["total_hospitals"] == 2
    assert body["processed_hospitals"] == 2
    assert body["failed_hospitals"] == 0
    assert body["batch_activated"] is True
    assert [h["row"] for h in body["hospitals"]] == [1, 2]
    assert [h["hospital_id"] for h in body["hospitals"]] == [11, 12]
    assert all(h["status"] == "created_and_activated" for h in body["hospitals"])


def test_bulk_reports_partial_upstream_failure(client, multipart):
    with patch(
        "hospital_bulk.service.upload_hospital",
        side_effect=[FakeUpstreamResponse(hospital_id=11), None],
    ), patch(
        "hospital_bulk.service.activate_hospital", return_value=FakeUpstreamResponse()
    ):
        r = client.post("/hospitals/bulk", **multipart(GOOD_CSV))

    assert r.status_code == 200
    body = r.get_json()
    assert body["processed_hospitals"] == 1
    assert body["failed_hospitals"] == 1
    assert [h["status"] for h in body["hospitals"]] == ["created_and_activated", "failed"]


def test_bulk_reports_failed_activation(client, multipart):
    with patch(
        "hospital_bulk.service.upload_hospital",
        side_effect=[FakeUpstreamResponse(hospital_id=11), FakeUpstreamResponse(hospital_id=12)],
    ), patch("hospital_bulk.service.activate_hospital", return_value=None):
        r = client.post("/hospitals/bulk", **multipart(GOOD_CSV))

    assert r.status_code == 200
    body = r.get_json()
    assert body["batch_activated"] is False
    assert all(h["status"] == "created" for h in body["hospitals"])


def test_bulk_rejects_invalid_csv_before_any_upload(client, multipart):
    with patch("hospital_bulk.service.upload_hospital") as upload:
        r = client.post("/hospitals/bulk", **multipart(BAD_ROW_CSV))
    upload.assert_not_called()
    assert r.status_code == 400
