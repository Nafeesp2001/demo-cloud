# Use official Python 3.9 image
FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy required files
COPY etl.py /app/
COPY .env /app/  # If you are using environment variables

# Install required dependencies
RUN pip install boto3 psycopg2-binary python-dotenv

# Set environment variables (override these in Lambda)
ENV S3_BUCKET=my-bucket
ENV S3_KEY=sample_data.json
ENV RDS_HOST=my-db-host
ENV RDS_PORT=5432
ENV RDS_DB=mydb
ENV RDS_USER=myuser
ENV RDS_PASS=mypassword
ENV GLUE_DATABASE=my_glue_db
ENV GLUE_TABLE=my_glue_table

# Ensure the script is executable
RUN chmod +x /app/etl.py

# Set the entry point for the container
CMD ["python", "/app/etl.py"]
