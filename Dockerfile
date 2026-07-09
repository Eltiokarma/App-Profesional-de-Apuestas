# Backend SAD (FastAPI de solo lectura + ingesta programada opcional).
# El frontend NO va aquí: se despliega estático en Vercel (ver docs/DESPLIEGUE.md).
FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ backend/

# /data = volumen con las 4 SQLite (sad, levels, constants, discreto)
ENV SAD_DATA_DIR=/data PYTHONUTF8=1

CMD ["sh", "-c", "python -m backend.bootstrap_datos && exec python -m uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
