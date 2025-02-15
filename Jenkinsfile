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
                    venv/bin/pip install boto3 psycopg2-binary
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
                        apt-get update && apt-get install -y wget unzip
                        wget https://releases.hashicorp.com/terraform/1.5.5/terraform_1.5.5_linux_amd64.zip
                        unzip terraform_1.5.5_linux_amd64.zip
                        mv terraform /usr/local/bin/
                    fi
                    
                    # Verify Terraform installation
                    terraform version

                    # Run Terraform commands
                    cd terraform
                    terraform init
                    terraform apply -auto-approve
                    '''
                }
            }
}


        stage('Build and Push Docker Image to ECR') {
            steps {
                script {
                    sh '''
                    # Install AWS CLI if not installed
                    if ! command -v aws &> /dev/null; then
                        echo "AWS CLI not found. Installing..."
                        apt-get update && apt-get install -y unzip curl
                        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                        unzip awscliv2.zip
                        ./aws/install
                    fi

                    # Verify AWS CLI installation
                    aws --version

                    # Authenticate Docker with AWS ECR
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL

                    # Build and push Docker image
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

