pipeline {
    agent any

    environment {
        AWS_REGION = "us-west-1"  // Change to your AWS region
        AWS_ACCOUNT_ID = credentials('AWS_ACCOUNT_ID')  
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        IMAGE_TAG = "latest"
        LAMBDA_FUNCTION_NAME = "etl_lambda"
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    git credentialsId: 'github-credentials', url: 'https://github.com/Nafeesp2001/demo-cloud.git', branch: 'main'
                }
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                    # Install pip3 if not installed
                    apt-get update && apt-get install -y python3-pip

                    # Verify Installation
                    python3 --version
                    pip3 --version
                    
                    # Install required Python packages
                    pip3 install boto3 psycopg2-binary
                    '''
                }
            }
        }

        stage('Deploy Infrastructure with Terraform') {
            steps {
                script {
                    dir('terraform') {
                        sh '''
                        terraform init
                        terraform apply -auto-approve
                        '''
                    }
                    // Capture Terraform Outputs and assign them to environment variables
                    script {
                        env.S3_BUCKET = sh(script: "terraform output -raw s3_bucket_name", returnStdout: true).trim()
                        env.ECR_REPO_URL = sh(script: "terraform output -raw ecr_repository_url", returnStdout: true).trim()
                    }
                }
            }
        }

        stage('Build and Push Docker Image to ECR') {
            steps {
                script {
                    sh '''
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL
                    docker build -t $ECR_REPO_URL:$IMAGE_TAG .
                    docker push $ECR_REPO_URL:$IMAGE_TAG
                    '''
                }
            }
        }

        stage('Upload Sample Data to S3') {
            steps {
                script {
                    sh "aws s3 cp sample_data.json s3://${env.S3_BUCKET}/"
                }
            }
        }

        stage('Update and Deploy AWS Lambda with ECR Image') {
            steps {
                script {
                    sh '''
                    aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --image-uri $ECR_REPO_URL:$IMAGE_TAG
                    aws lambda wait function-updated --function-name $LAMBDA_FUNCTION_NAME
                    aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --payload '{}' response.json
                    cat response.json
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "Pipeline execution completed."
            }
        }
    }
}

