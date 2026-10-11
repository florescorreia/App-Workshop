FROM python:3.13.7-slim-bookworm
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY . .
RUN useradd --uid 10001 --create-home appuser
USER appuser
CMD ["sh", "-c", "python bootstrap.py && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
