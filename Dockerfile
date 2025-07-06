FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements/prod.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
