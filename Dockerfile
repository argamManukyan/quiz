FROM python:3.9-slim-buster

LABEL authors="argam"
#ENV PYTHONUNBUFERED 1
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

RUN chmod +x run.sh
#ENTRYPOINT ["sh", "run.sh"]
