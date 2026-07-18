Exit code: 0
Wall time: 3.1 seconds
Output:
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render overrides this command for its background worker service.
CMD ["python", "web_ordering_app.py"]

