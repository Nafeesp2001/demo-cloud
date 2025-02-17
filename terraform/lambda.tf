resource "aws_lambda_function" "etl_lambda" {
  function_name    = "etl_lambda"
  role            = aws_iam_role.lambda_role.arn
  package_type    = "Zip"
  filename        = "/var/jenkins_home/workspace/domo-cloud-pipeline/lambda_function.zip"  # ✅ Correct file path
  handler         = "etl.lambda_handler"  # ✅ Correct handler for Python file
  runtime         = "python3.9"  # ✅ Required for ZIP-based Lambda

  memory_size     = 512
  timeout         = 60

  depends_on = [
    aws_s3_bucket.etl_bucket,
    aws_db_instance.etl_rds
  ]
}
