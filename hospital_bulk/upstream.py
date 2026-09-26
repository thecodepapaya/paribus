import requests

BASE_URL = "https://hospital-directory.onrender.com"


def upload_hospital(hospital):
    payload = hospital.model_dump(mode="json")
    response = requests.post(f"{BASE_URL}/hospitals/", json=payload)
    return response


def activate_hospital(batch_id: str):
    response = requests.patch(f"{BASE_URL}/hospitals/batch/{batch_id}/activate")
    return response
