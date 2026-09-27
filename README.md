# Hospital Bulk Processing API

Bulk-processing service for the Paribus assignment. Accepts CSV uploads and creates hospitals via the deployed [Hospital Directory API](https://hospital-directory.onrender.com/docs), with batch activation.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/hospitals/bulk` | Upload CSV, create hospitals, activate batch |
| POST | `/hospitals/bulk/validate` | Validate a CSV without creating anything |
| GET | `/` | Health check |

## Workflow

1. Validate the file: present, `.csv` extension, UTF-8, required header (`name`, `address`; `phone` optional).
2. Validate every row. **Any invalid row rejects the whole upload** (see design decisions).
3. Generate a batch ID (UUID).
4. Create each hospital via `POST /hospitals/` upstream, tagged with the batch ID.
5. Activate the batch via `PATCH /hospitals/batch/{batch_id}/activate`.
6. Return per-hospital results and timings.

## Design decisions

- **Validation is a gate.** A CSV with any invalid row is rejected with a 400 before anything is created; partial imports of dirty data are never performed. Consequently `failed_hospitals` in the response counts *upstream creation failures only* — CSV validity is all-or-nothing, upstream failures are per-hospital.
- **Flask over FastAPI.** The spec favors it for minimalism; the workload (≤20 hospitals per request, no streaming) doesn't need async or auto-docs. Would revisit for high-concurrency or streaming use cases.
- **Python 3.10+** for modern union type syntax (`str | None`).
- **`pyproject.toml` is the single source of truth** for dependencies.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

Development:

```bash
flask --app hospital_bulk run
```

Production:

```bash
gunicorn "hospital_bulk:create_app()"
```

## Test

```bash
pytest
```

Suite in progress.
