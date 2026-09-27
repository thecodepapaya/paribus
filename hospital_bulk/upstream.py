import logging

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
BASE_URL = "https://hospital-directory.onrender.com"


def upload_hospital(hospital):
    payload = hospital.model_dump(mode="json")
    hospital_name = getattr(hospital, "name", "unknown")
    logger.info("Uploading hospital: %s", hospital_name)

    try:
        response = requests.post(f"{BASE_URL}/hospitals/", json=payload, timeout=15)
        logger.info(
            "Upload finished for %s: status=%s", hospital_name, response.status_code
        )
        return response
    except requests.exceptions.RequestException:
        logger.warning("Upload failed for hospital: %s", hospital_name, exc_info=True)
        return None


def activate_hospital(batch_id: str):
    logger.info("Activating batch: %s", batch_id)

    try:
        response = requests.patch(
            f"{BASE_URL}/hospitals/batch/{batch_id}/activate",
            timeout=15,
        )
        logger.info(
            "Batch activation finished for %s: status=%s",
            batch_id,
            response.status_code,
        )
        return response
    except requests.exceptions.RequestException:
        logger.warning("Batch activation failed for %s", batch_id, exc_info=True)
        return None
