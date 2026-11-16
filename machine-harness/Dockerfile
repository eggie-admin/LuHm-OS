# Source-candidate only. Owner must pin base digest after approved supply-chain review.
FROM python:3.12-slim-bookworm
ARG SOURCE_REF=UNVERIFIED
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LUHM_SOURCE_REF=${SOURCE_REF} LUHM_BIND=0.0.0.0
WORKDIR /opt/luhm
COPY machine-harness/requirements.txt /opt/luhm/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && useradd --system --no-create-home --uid 10001 luhm
COPY host/machineHarness/app.py /opt/luhm/app.py
USER 10001:10001
EXPOSE 8765
CMD ["python", "/opt/luhm/app.py"]
