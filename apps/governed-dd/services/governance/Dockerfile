FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY services/governance/requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY services/governance/ /app/
COPY schemas /app/schemas
COPY tests /app/tests
RUN useradd --uid 1101 --create-home dd && mkdir /artifacts /ontology && chown dd /artifacts /ontology
USER dd
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
