# 1) Build do frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend/react-app
COPY frontend/react-app/package.json frontend/react-app/package-lock.json* ./
RUN npm install
RUN npm install axios
COPY frontend/react-app/ ./
RUN npm run build

# 2) Backend
FROM python:3.12-slim AS backend
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

# O backend não precisa mais do frontend buildado, o Nginx vai lidar com isso.

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 3) Nginx - Novo Estágio
FROM nginx:alpine AS nginx-server
COPY --from=frontend-builder /app/frontend/react-app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf