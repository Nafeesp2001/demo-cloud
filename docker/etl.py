import boto3
import psycopg2
import json
import os
from dotenv import load_dotenv
load_dotenv()
# # AWS Clients
# s3 = boto3.client("s3")
# glue = boto3.client("glue")

# S3_BUCKET = "nafeesposharkar-bucket"
# S3_BUCKET = "sample_data.json"
# RDS_HOST = ""
# RDS_PORT = 5432
# Environment Variables
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("sample_data.json")
RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = os.getenv("RDS_PORT", 5432)
RDS_DB = os.getenv("RDS_DB")
RDS_USER = os.getenv("RDS_USER")
RDS_PASS = os.getenv("RDS_PASS")
GLUE_DATABASE = os.getenv("GLUE_DATABASE")
GLUE_TABLE = os.getenv("GLUE_TABLE")

print("S3_BUCKET:", S3_BUCKET)
print("S3_KEY:", S3_KEY)
print("RDS_HOST:", RDS_HOST)
print("RDS_PORT:", RDS_PORT)
print("RDS_DB:", RDS_DB)
print("RDS_USER:", RDS_USER)
print("RDS_PASS:", RDS_PASS)
print("GLUE_DATABASE:", GLUE_DATABASE)
print("GLUE_TABLE:", GLUE_TABLE)

def fetch_s3_data():
    """
    Fetch JSON data from an S3 bucket.
    """
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"Data fetched from S3: {data}")
        return data
    except Exception as e:
        print(f"Error fetching data from S3: {e}")
        raise

def push_to_rds(data):
    """
    Push data to an RDS PostgreSQL database.
    If it fails, fallback to storing data in AWS Glue.
    """
    try:
        conn = psycopg2.connect(
            host=RDS_HOST, 
            port=RDS_PORT, 
            database=RDS_DB,
            user=RDS_USER, 
            password=RDS_PASS
        )
        cursor = conn.cursor()
        # Insert data into your_table (ensure your_table exists in the database schema)
        cursor.execute("INSERT INTO your_table (data) VALUES (%s)", (json.dumps(data),))
        conn.commit()
        cursor.close()
        conn.close()
        print("Data inserted into RDS successfully")
    except Exception as e:
        print(f"Failed to insert data into RDS: {e}")
        push_to_glue(data)

def push_to_glue(data):
    """
    Push data to AWS Glue by creating a table.
    """
    try:
        response = glue.create_table(
            DatabaseName=GLUE_DATABASE,
            TableInput={
                'Name': GLUE_TABLE,
                'StorageDescriptor': {
                    'Columns': [{'Name': 'data', 'Type': 'string'}],
                    'Location': f"s3://{S3_BUCKET}/glue/",
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
                }
            }
        )
        print("Data stored in AWS Glue successfully:", response)
    except Exception as e:
        print(f"Error storing data in AWS Glue: {e}")

def lambda_handler(event, context):
    """
    Main handler for Lambda or standalone execution.
    """
    try:
        data = fetch_s3_data()
        push_to_rds(data)
    except Exception as e:
        print(f"Error in lambda_handler: {e}")

if __name__ == "__main__":
    lambda_handler({}, {})
