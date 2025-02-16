provider "aws" {
  region = "us-west-1" # Free Tier regions include us-east-1, us-west-2, etc.
}

# 1. Create S3 Bucket
resource "aws_s3_bucket" "etl_bucket" {
  bucket = "nafees-bucket"
}

# # New ACL Resource (Replaces deprecated acl argument)
# resource "aws_s3_bucket_acl" "etl_bucket_acl" {
#   bucket = aws_s3_bucket.etl_bucket.id
#   acl    = "private"
# }

# Correct Output Reference
output "s3_bucket_name" {
  value = aws_s3_bucket.etl_bucket.id  # Fix: Use correct resource name
}


# 2. Create an ECR Repository
resource "aws_ecr_repository" "etl_repo" {
  name = "etl-docker-repo"

  tags = {
    Name        = "ETL ECR Repository"
    Environment = "Experiment"
  }
}
output "ecr_repository_url" {
  value = aws_ecr_repository.etl_repo.repository_url
}
# 3. Create RDS PostgreSQL Instance (Free Tier Eligible)
resource "aws_db_instance" "etl_rds" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine              = "postgres"
  instance_class      = "db.t3.micro"  # db.t2.micro is unsupported for PG 16
  db_name             = "etl_database"
  username           = "nafsposh"
  password           = "Abcd#1234"
  publicly_accessible = false
  skip_final_snapshot = true
}




# 5. Create Glue Database (No cost for Glue Database creation)
resource "aws_glue_catalog_database" "etl_glue_db" {
  name = "etl_glue_db"

  tags = {
    Name        = "ETL Glue Database"
    Environment = "Experiment"
  }
}

# 6. Create Glue Table (optional, you can create it dynamically in your code)
resource "aws_glue_catalog_table" "etl_glue_table" {
  name          = "etl_table"
  database_name = aws_glue_catalog_database.etl_glue_db.name

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.etl_bucket.bucket}/glue-data/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"
    columns {
      name = "id"
      type = "int"
    }
    columns {
      name = "name"
      type = "string"
    }
    columns {
      name = "email"
      type = "string"
    }
    columns {
      name = "purchase_date"
      type = "string"
    }
    columns {
      name = "amount"
      type = "double"
    }
  }
}


# 7. Create IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "etl-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "Lambda IAM Role"
    Environment = "Experiment"
  }
}

# Attach Policies to Lambda Role
resource "aws_iam_role_policy_attachment" "lambda_s3_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_rds_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_glue_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# 8. Create Lambda Function
resource "aws_lambda_function" "etl_lambda" {
  filename = "/var/jenkins_home/workspace/demo-cloud-pipeline/lambda_function.zip"
  function_name    = "etl_lambda"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
 
  environment {
    variables = {
      RDS_HOST = aws_db_instance.etl_rds.address
      RDS_PORT = aws_db_instance.etl_rds.port
      RDS_DB   = aws_db_instance.etl_rds.db_name
      RDS_USER = aws_db_instance.etl_rds.username
      RDS_PASS = aws_db_instance.etl_rds.password
    }
  }
}


output "rds_host" {
  value = aws_db_instance.etl_rds.address
}

output "rds_db_name" {
  value = aws_db_instance.etl_rds.db_name
}

output "rds_user" {
  value = aws_db_instance.etl_rds.username
}

output "rds_password" {
  value = aws_db_instance.etl_rds.password
  sensitive = true
}

output "glue_database" {
  value = aws_glue_catalog_database.etl_glue_db.name
}

output "glue_table" {
  value = aws_glue_catalog_table.etl_glue_table.name
}
output "rds_port" {
  value = aws_db_instance.etl_rds.port
}
