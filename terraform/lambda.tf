resource "aws_lambda_function" "etl_lambda" {
  function_name    = "etl_lambda"
  role            = aws_iam_role.lambda_role.arn
  package_type    = "Image"
  image_uri       = "${aws_ecr_repository.etl_repo.repository_url}:latest"  # 👈 Accessing ECR repo from main.tf

  memory_size     = 512
  timeout        = 60

  depends_on = [
    aws_ecr_repository.etl_repo,  # 👈 Ensures Lambda runs only after ECR is ready
    aws_s3_bucket.etl_bucket,
    aws_db_instance.etl_rds
  ]
}
