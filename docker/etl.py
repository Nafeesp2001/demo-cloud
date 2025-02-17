import boto3
import psycopg2
import json
import os
from dotenv import load_dotenv

# Load .env variables
# load_dotenv('/var/jenkins_home/workspace/domo-cloud-pipeline/docker/env')

env_path = os.path.join(os.path.dirname(__file__), "env")
print(f"Loading environment variables from: {env_path}")
load_dotenv(env_path)

S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = "sample_data.json"
RDS_HOST = os.getenv("RDS_HOST")
RDS_DB = os.getenv("RDS_DB")
RDS_USER = os.getenv("RDS_USER")
RDS_PASS = os.getenv("RDS_PASS")
GLUE_DATABASE = os.getenv("GLUE_DATABASE")
GLUE_TABLE = os.getenv("GLUE_TABLE")
RDS_PORT = int(os.getenv("RDS_PORT", 5432))
# Initialize AWS Clients
s3 = boto3.client("s3")
glue = boto3.client("glue")


def fetch_s3_data():
    """
    Fetch JSON data from an S3 bucket.
    """
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        data = json.loads(response['Body'].read().decode('utf-8'))
        print(f"✅ Data fetched from S3: {data}")
        return data
    except Exception as e:
        print(f"❌ Error fetching data from S3: {e}")
        raise

def push_to_rds(data):
    """
    Push structured data to an RDS PostgreSQL database.
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

        # Ensure table exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_data (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            purchase_date DATE NOT NULL,
            amount NUMERIC(10,2) NOT NULL
        );
        """)

        # Insert each record into the database
        for record in data:
            cursor.execute("""
            INSERT INTO purchase_data (id, name, email, purchase_date, amount)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE 
            SET name = EXCLUDED.name, email = EXCLUDED.email, 
                purchase_date = EXCLUDED.purchase_date, amount = EXCLUDED.amount;
            """, (record["id"], record["name"], record["email"], record["purchase_date"], record["amount"]))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data inserted into RDS successfully")
    except Exception as e:
        print(f"❌ Failed to insert data into RDS: {e}")
        push_to_glue(data)

def push_to_glue(data):
    """
    Insert data into an existing AWS Glue table.
    """
    try:
        glue_client = boto3.client("glue")

        # Define partitions based on existing schema
        partitions = [
            {
                "Values": [str(record["id"])],  # Partition key (modify if needed)
                "StorageDescriptor": {
                    "Columns": [
                        {"Name": "id", "Type": "int"},
                        {"Name": "name", "Type": "string"},
                        {"Name": "email", "Type": "string"},
                        {"Name": "purchase_date", "Type": "string"},
                        {"Name": "amount", "Type": "double"},
                    ],
                    "Location": f"s3://{S3_BUCKET}/glue/",
                    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                    },
                },
            }
            for record in data
        ]

        response = glue_client.batch_create_partition(
            DatabaseName=GLUE_DATABASE,
            TableName=GLUE_TABLE,
            PartitionInputList=partitions,
        )

        print("✅ Data inserted into AWS Glue successfully:", response)

    except Exception as e:
        print(f"❌ Error inserting data into AWS Glue: {e}")


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    try:
        data = fetch_s3_data()
        push_to_rds(data)
    except Exception as e:
        print(f"❌ Error in lambda_handler: {e}")

# Local testing (if needed)
if __name__ == "__main__":
    lambda_handler({}, {})
