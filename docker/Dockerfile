FROM python:3.9

WORKDIR /app

# Copy necessary files
COPY etl.py /app/

# Install required dependencies
RUN pip install boto3 psycopg2-binary python-dotenv

# Ensure environment variables are passed at runtime, not build time
CMD ["python", "etl.py"]
