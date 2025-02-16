FROM python:3.9

WORKDIR /app

COPY etl.py /app/

RUN pip install boto3 psycopg2-binary python-dotenv

CMD ["python", "etl.py"]
