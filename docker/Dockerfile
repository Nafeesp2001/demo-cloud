FROM python:3.9-slim

WORKDIR /app

# Copy necessary files
COPY etl.py /app/
COPY env /app/
# Install required dependencies
RUN pip install --no-cache-dir boto3 psycopg2-binary python-dotenv

# Ensure environment variables are passed at runtime, not build time
CMD ["etl.lambda_handler"]
