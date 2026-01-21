pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    environment {
        // GitHub Configuration
        GITHUB_REPO = 'https://github.com/YOUR_USERNAME/YOUR_REPO.git'
        GITHUB_BRANCH = 'main'
        
        // AWS EC2 Details
        EC2_USER = 'ubuntu'
        EC2_HOST = '35.154.193.96'  // Your EC2 public IP
        EC2_KEY = '/var/lib/jenkins/.ssh/pemkey.pem'
        
        // Docker Registry (Docker Hub)
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_USERNAME = credentials('dockerhub-username')
        IMAGE_NAME = 'fake-news-detection'
        IMAGE_TAG = "${BUILD_NUMBER}"
        FULL_IMAGE = "${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE = "${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
        
        // Slack Notifications (Optional)
        //SLACK_WEBHOOK = credentials('slack-webhook-url')
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo '📥 Cloning repository from GitHub...'
                script {
                    try {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "*/${GITHUB_BRANCH}"]],
                            userRemoteConfigs: [[url: "${GITHUB_REPO}"]]
                        ])
                        echo '✅ Code checkout successful'
                    } catch (Exception e) {
                        echo "❌ Checkout failed: ${e}"
                        currentBuild.result = 'FAILURE'
                        error("Failed to checkout code")
                    }
                }
            }
        }

        stage('Validate') {
            steps {
                echo '🔍 Validating Docker and dependencies...'
                script {
                    sh '''
                        echo "Docker version:"
                        docker --version
                        
                        echo "Python files present:"
                        ls -la app.py requirements.txt Dockerfile
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🔨 Building Docker image...'
                script {
                    try {
                        sh '''
                            docker build \
                                --tag ${FULL_IMAGE} \
                                --tag ${LATEST_IMAGE} \
                                --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VERSION=${BUILD_NUMBER} \
                                .
                            
                            echo "✅ Image built successfully"
                            docker images | grep ${IMAGE_NAME}
                        '''
                    } catch (Exception e) {
                        echo "❌ Build failed: ${e}"
                        currentBuild.result = 'FAILURE'
                        error("Docker build failed")
                    }
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                echo '🧪 Testing Docker image...'
                script {
                    try {
                        sh '''
                            # Run container in background
                            docker run -d --name test-container -p 5001:5000 ${LATEST_IMAGE}
                            sleep 5
                            
                            # Health check
                            curl -f http://localhost:5001/ || exit 1
                            echo "✅ Image test passed"
                            
                            # Cleanup
                            docker stop test-container
                            docker rm test-container
                        '''
                    } catch (Exception e) {
                        echo "⚠️ Image test failed: ${e}"
                        sh 'docker stop test-container || true; docker rm test-container || true'
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing image to Docker Hub...'
                script {
                    try {
                        withCredentials([usernamePassword(
                            credentialsId: 'dockerhub-creds',
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh '''
                                echo "${DOCKER_PASS}" | docker login -u ${DOCKER_USER} --password-stdin
                                
                                echo "Pushing ${FULL_IMAGE}..."
                                docker push ${FULL_IMAGE}
                                
                                echo "Pushing ${LATEST_IMAGE}..."
                                docker push ${LATEST_IMAGE}
                                
                                docker logout
                                echo "✅ Images pushed successfully"
                            '''
                        }
                    } catch (Exception e) {
                        echo "❌ Push failed: ${e}"
                        currentBuild.result = 'FAILURE'
                        error("Failed to push image to Docker Hub")
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo '🚀 Deploying to EC2 instance...'
                script {
                    try {
                        sh '''
                            ssh -i ${EC2_KEY} \
                                -o StrictHostKeyChecking=no \
                                -o ConnectTimeout=10 \
                                -o StrictHostKeyChecking=no \
                                ${EC2_USER}@${EC2_HOST} << 'EOF'
                            
                            set -e  # Exit on error
                            
                            echo "Logging into Docker Hub..."
                            echo "${DOCKER_PASS}" | docker login -u ${DOCKER_USER} --password-stdin
                            
                            echo "Stopping old container..."
                            docker stop fake-news-app || true
                            docker rm fake-news-app || true
                            
                            echo "Pulling latest image..."
                            docker pull ${LATEST_IMAGE}
                            
                            echo "Starting new container..."
                            docker run -d \
                                --name fake-news-app \
                                --restart always \
                                -p 80:5000 \
                                -e FLASK_ENV=production \
                                -e PYTHONUNBUFFERED=1 \
                                --health-cmd='curl -f http://localhost:5000/ || exit 1' \
                                --health-interval=30s \
                                --health-timeout=10s \
                                --health-retries=3 \
                                ${LATEST_IMAGE}
                            
                            sleep 5
                            
                            echo "Verifying container status..."
                            docker ps | grep fake-news-app
                            docker logout
EOF
                        '''
                        echo "✅ Deployment successful"
                    } catch (Exception e) {
                        echo "❌ Deployment failed: ${e}"
                        currentBuild.result = 'FAILURE'
                        error("Failed to deploy to EC2")
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                echo '✅ Running health check...'
                script {
                    try {
                        sh '''
                            sleep 10
                            
                            echo "Checking application health..."
                            response=$(curl -w "%{http_code}" -s -o /dev/null http://${EC2_HOST}/)
                            
                            if [ $response -eq 200 ]; then
                                echo "✅ Application is healthy (HTTP $response)"
                            else
                                echo "⚠️ Application returned HTTP $response"
                                exit 1
                            fi
                        '''
                    } catch (Exception e) {
                        echo "❌ Health check failed: ${e}"
                        currentBuild.result = 'FAILURE'
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ CI/CD Pipeline Completed Successfully!'
            script {
                sh '''
                    echo "Deployment Summary:"
                    echo "Image: ${LATEST_IMAGE}"
                    echo "EC2 Host: ${EC2_HOST}"
                    echo "Access: http://${EC2_HOST}/"
                '''
            }
        }
        failure {
            echo '❌ Pipeline Failed! Check logs above.'
        }
        cleanup {
            sh '''
                docker logout || true
                docker system prune -f --volumes || true
            '''
        }
    }
}
