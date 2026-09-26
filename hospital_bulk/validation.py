from csv import DictReader

from .models import Hospital


def validated_hospital(reader: DictReader[str], batch_id: str) -> list[Hospital]:

    hospitals: list[Hospital] = []

    for row in reader:
        name = row["name"].strip() if row["name"] else None
        address = row["address"].strip() if row["address"] else None

        if not name or not address:
            continue

        phone = row["phone"].strip() if row["phone"] else None
        hospital = Hospital(
            name=name,
            address=address,
            phone=phone,
            creation_batch_id=batch_id,
        )
        hospitals.append(hospital)

    return hospitals
