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
                    # Install venv if not installed
                    apt-get update && apt-get install -y python3-venv
                    
                    # Create a virtual environment
                    python3 -m venv venv

                    # Upgrade pip inside the virtual environment
                    venv/bin/pip install --upgrade pip

                    # Install required packages
                    venv/bin/pip install boto3 psycopg2-binary dotenv
                    '''
                }
            }
}



        stage('Deploy Infrastructure with Terraform') {
            steps {
                script {
                    sh '''
                    # Install Terraform if not installed
                    if ! command -v terraform &> /dev/null; then
                        echo "Terraform not found. Installing..."
                        apt-get update && apt-get install -y unzip curl
                        
                        # Download Terraform
                        curl -o terraform.zip https://releases.hashicorp.com/terraform/1.5.5/terraform_1.5.5_linux_amd64.zip
                        
                        # Force unzip without prompt
                        unzip -o terraform.zip -d /usr/local/bin/
                        
                        # Verify Terraform installation
                        terraform version
                    fi
                    # Initialize and apply Terraform
                    cd terraform
                    terraform destroy -auto-approve
                    terraform init
                    terraform apply -auto-approve
                    terraform output -raw s3_bucket_name
                    '''
                }
            }
}


        stage('Get ECR URL and S3 Bucket name') {
            steps {
                script {
                     env.S3_BUCKET = sh(script: "terraform output -raw s3_bucket_name", returnStdout: true).trim()
                     env.ECR_URL = sh(script: "terraform output -raw ecr_repository_url", returnStdout: true).trim()
                    echo "ECR Repository URL: ${ECR_URL}"
                    echo "S3 Bucket Name: ${S3_BUCKET}"

                }
            }
        }

        stage('Build and Push Docker Image to ECR') {
            steps {
                script {
                    sh '''
                    # Install AWS CLI if not installed
                   # if ! command -v aws &> /dev/null; then
                    #    echo "AWS CLI not found. Installing..."
                   #     apt-get update && apt-get install -y unzip curl
                    #    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                     #   rm -rf aws/
                      #  unzip -o awscliv2.zip
                       # ./aws/install
                   # fi

                    # Verify AWS CLI installation
                    aws --version
                    
                    # Authenticate Docker with AWS ECR
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${ECR_URL}

                    # Build and push Docker image
                    docker build -t $ECR_URL:$IMAGE_TAG .
                    docker push $ECR_URL:$IMAGE_TAG
                    '''
                }
            }
}


        stage('Upload Sample Data to S3') {
            steps {
                script {
                    sh "aws s3 cp sample_data.json s3://${S3_BUCKET}/"
                }
            }
        }

        stage('Update and Deploy AWS Lambda with ECR Image') {
            steps {
                script {
                    sh '''
                    aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --image-uri $ECR_URL:$IMAGE_TAG
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

