FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY hospital_bulk ./hospital_bulk

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8000", "hospital_bulk:create_app()"]
