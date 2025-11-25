# Multi-stage Dockerfile: build React frontend and then build python backend image

# 1) Build the frontend using node
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/react-app/package.json frontend/react-app/package-lock.json* ./
COPY frontend/react-app/ ./react-app/
WORKDIR /app/frontend/react-app
RUN npm install
RUN npm run build

# 2) Build the Python backend
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy backend + database + frontend build
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

# copy the frontend build into frontend/ (fastapi mounts /frontend)
COPY --from=frontend-builder /app/frontend/react-app/dist /app/frontend

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
