# Hospital Bulk Processing API

Bulk-processing service for the Paribus assignment. Accepts CSV uploads and creates hospitals via the deployed [Hospital Directory API](https://hospital-directory.onrender.com/docs), with batch activation.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/hospitals/bulk` | Upload CSV, create hospitals, activate batch |
| POST | `/hospitals/bulk/validate` | Validate a CSV without creating anything |
| GET | `/` | Health check |

## Workflow

1. Validate the file: present, `.csv` extension, UTF-8, required header (`name`, `address`; `phone` optional), at most 20 data rows.
2. Validate every row: all-or-nothing gate (see design decisions). Rows with extra columns, or missing/empty `name` or `address`, are rejected.
3. Generate a batch ID (UUID).
4. Create each hospital via `POST /hospitals/` upstream, tagged with the batch ID — up to 10 concurrent requests, 15s timeout each.
5. If at least one hospital was created, activate the batch via `PATCH /hospitals/batch/{batch_id}/activate`.
6. Return per-hospital results and timings.

## Design decisions

- **Validation is a gate.** A CSV with any invalid row is rejected with a 400 before anything is created; partial imports of dirty data are never performed. The error reports the first invalid row (spec is silent on reporting all of them). Consequently `failed_hospitals` in the response counts *upstream creation failures only*.
- **Activation policy.** The spec's "once all hospitals are created successfully" is ambiguous (its own example response shows a partial-failure shape). Read here as: activate once all creation calls have completed and at least one succeeded; the response self-documents partial batches via `failed_hospitals` and per-hospital `status` (`created_and_activated` / `created` / `failed`).
- **20-row limit.** The spec's Technical Constraints cap a CSV at 20 hospitals; the example response showing 25 is illustrative, the constraint wins.
- **Threads, not async.** Upstream creations run concurrently on a bounded `ThreadPoolExecutor` (10 workers). This is concurrent I/O, not asyncio — Flask is WSGI, and the workload doesn't justify a framework change.
- **Flask over FastAPI.** The spec favors it for minimalism; ≤20 hospitals per request needs no async framework or auto-docs.
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

Production (gunicorn):

```bash
gunicorn --workers 2 --bind 0.0.0.0:8000 "hospital_bulk:create_app()"
```

Docker:

```bash
docker compose up --build
```

## Test

```bash
pytest
```

Six tests covering the core contracts: validation gate (accept / reject), bulk happy path (full response shape), partial upstream failure, failed activation, and gate-before-upload. The upstream API is mocked in all tests.
