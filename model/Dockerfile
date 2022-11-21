FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY data/ /app/data/

COPY main.py /app

ENTRYPOINT ["python","/app/main.py"]