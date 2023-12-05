FROM python:latest

WORKDIR /app

COPY core/main.py /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["python", "/app/main.py"]