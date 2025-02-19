FROM python:3.7-slim

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "main.py"]