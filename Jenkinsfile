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

        stage('Deploy Infrastructure with Terraform') {
            steps {
                script {
                    sh '''
                    # Install Terraform if not installed
                    mkdir -p $HOME/bin
                    curl -o terraform.zip https://releases.hashicorp.com/terraform/1.5.5/terraform_1.5.5_linux_amd64.zip
                    unzip -o terraform.zip -d /var/jenkins_home/bin
                    echo "export PATH=$HOME/bin:\$PATH" >> ~/.bashrc
                    export PATH=$HOME/bin:$PATH
                    terraform --version
                    # Initialize and apply Terraform
                    cd terraform
                    # chown -R jenkins:jenkins .
                    # chmod -R 777 .
                    terraform destroy -auto-approve
                    terraform init
                    terraform apply -auto-approve
                    terraform output -json > terraform_outputs.json
                    '''
                }
            }
}

        stage('Storing outputs'){
            steps{
                script {
                    sh '''

                    echo "Downloading jq manually..."
                    mkdir -p $HOME/bin
                    curl -Lo $HOME/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
                    chmod +x $HOME/bin/jq
                    export PATH=$HOME/bin:$PATH
                    jq --version
                ENV_FILE="/var/jenkins_home/workspace/domo-cloud-pipeline/docker/env"  
                

                echo "S3_BUCKET=$(jq -r '.s3_bucket_name.value' terraform/terraform_outputs.json)" > $ENV_FILE
                echo "RDS_HOST=$(jq -r '.rds_host.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                echo "RDS_PORT=$(jq -r '.rds_port.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                echo "RDS_DB=$(jq -r '.rds_db_name.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                echo "RDS_USER=$(jq -r '.rds_user.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                echo "RDS_PASS=$(jq -r '.rds_password.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                echo "ECR_URL=$(jq -r '.ecr_repository_url.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                echo "GLUE_DATABASE=$(jq -r '.glue_database.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                echo "GLUE_TABLE=$(jq -r '.glue_table.value' terraform/terraform_outputs.json)" >> $ENV_FILE
                 


                    '''
                }
            }
        }
        stage('Get ECR URL and S3 Bucket name') {
    steps {
        script {
            sh '''
            echo "Downloading jq manually..."
            mkdir -p $HOME/bin
            curl -Lo $HOME/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
            chmod +x $HOME/bin/jq
            export PATH=$HOME/bin:$PATH
            jq --version
            '''

            env.S3_BUCKET = sh(script: "$HOME/bin/jq -r '.s3_bucket_name.value' /var/jenkins_home/workspace/domo-cloud-pipeline/terraform/terraform_outputs.json", returnStdout: true).trim()
            env.ECR_URL = sh(script: "$HOME/bin/jq -r '.ecr_repository_url.value' /var/jenkins_home/workspace/domo-cloud-pipeline/terraform/terraform_outputs.json", returnStdout: true).trim()
            
            echo "ECR Repository URL: ${env.ECR_URL}"
            echo "S3 Bucket Name: ${env.S3_BUCKET}"
        }
    }
}


        stage('Build and Push Docker Image to ECR') {
            steps {
                script {
                    dir('docker') {

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
                    

                    python3 -m venv myvenv
                    . myvenv/bin/activate

                    # Build and push Docker image
                    docker build -t $ECR_URL:$IMAGE_TAG .
                    docker push $ECR_URL:$IMAGE_TAG --quiet

                    deactivate
                    '''
                    }
                }
            }
}


        stage('Upload Sample Data to S3') {
            steps {
                script {
                    dir('docker') {
                    sh "aws s3 cp sample_data.json s3://${S3_BUCKET}/"
                    }
                }
            }
        }

        stage('Update and Deploy AWS Lambda with ECR Image') {
            steps {
                script {
                    sh '''
                    AWS_PAGER="" aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --image-uri $ECR_URL:$IMAGE_TAG
                    aws lambda wait function-updated --function-name $LAMBDA_FUNCTION_NAME
                    AWS_PAGER="" aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --payload '{}' response.json
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

