FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=200 -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "college_management_system.wsgi:application", "--bind", "0.0.0.0:8000"]