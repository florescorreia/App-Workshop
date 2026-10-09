FROM python:3.13.7-slim-bookworm
COPY requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock
WORKDIR /workspace
ENTRYPOINT ["python", "scripts/vps.py"]
