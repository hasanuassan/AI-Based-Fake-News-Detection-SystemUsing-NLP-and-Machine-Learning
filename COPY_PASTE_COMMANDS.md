# 🚀 Copy-Paste Commands for Deployment

Use these commands exactly as shown. Replace placeholders in `CAPS` with your values.

---

## Phase 1: Local Setup (Your Computer)

### 1. Clone and Setup Repository
```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Verify files exist
ls -la
# Should show: app.py, Dockerfile, Jenkinsfile, requirements.txt

# Create .gitignore if not exists
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
.env
.DS_Store
*.log
EOF

# Commit and push
git add .
git commit -m "Add Docker and Jenkins CI/CD configuration"
git push origin main
```

### 2. Test Docker Locally
```bash
# Build image
docker build -t fake-news-detection:latest .

# Run container
docker run -d -p 5000:5000 --name test-app fake-news-detection:latest

# Test app
curl http://localhost:5000

# View logs
docker logs test-app

# Stop and remove
docker stop test-app
docker rm test-app

# Cleanup
docker system prune -f
```

---

## Phase 2: Docker Hub Setup

### 3. Create Docker Hub Repository
```bash
# Visit https://hub.docker.com/ in your browser

# 1. Sign in with your account
# 2. Click profile icon → My Account
# 3. Go to "Security" → "Access Tokens"
# 4. Click "New Access Token"
# 5. Name: "Jenkins"
# 6. Select: Read, Write, Delete
# 7. Copy the token (you'll need this)

# Then create repository:
# 1. Click "Repositories" → "Create repository"
# 2. Name: "fake-news-detection"
# 3. Visibility: "Public"
# 4. Click "Create"
```

---

## Phase 3: AWS EC2 Setup

### 4. Launch EC2 Instance (if not already done)
```bash
# Use AWS Console or CLI
# Instance type: t3.medium or larger
# OS: Ubuntu 22.04
# Storage: 20GB minimum
# Security group: Allow SSH (22), HTTP (80), HTTPS (443)

# Download your key pair as: your-ec2-key.pem
chmod 600 your-ec2-key.pem
```

### 5. Setup Docker on EC2
```bash
# SSH to EC2
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Inside EC2:
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add ubuntu to docker group
sudo usermod -aG docker ubuntu

# Log out and log back in
exit
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Verify Docker
docker --version
docker run hello-world

# Exit EC2
exit
```

---

## Phase 4: Jenkins Server Setup

### 6. Setup Jenkins (on separate Linux server)
```bash
# SSH to Jenkins server
ssh -i jenkins-key.pem ubuntu@JENKINS_IP

# Inside Jenkins server:
# Install Java
sudo apt-get update
sudo apt-get install -y openjdk-11-jdk-headless

# Install Jenkins
sudo wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# Install Docker on Jenkins server
sudo apt-get install -y docker.io
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Setup SSH key for EC2
sudo mkdir -p /var/lib/jenkins/.ssh
sudo chmod 700 /var/lib/jenkins/.ssh

# Copy your EC2 PEM key
sudo cp your-ec2-key.pem /var/lib/jenkins/.ssh/pemkey.pem
sudo chmod 600 /var/lib/jenkins/.ssh/pemkey.pem
sudo chown jenkins:jenkins /var/lib/jenkins/.ssh/pemkey.pem

# Test SSH access
sudo -u jenkins ssh -i /var/lib/jenkins/.ssh/pemkey.pem -o StrictHostKeyChecking=no ubuntu@EC2_PUBLIC_IP "docker --version"
```

### 7. Configure Jenkins UI

Open Jenkins in browser: `http://JENKINS_IP:8080`

**Step 1: Initial Setup**
```
1. Paste the admin password from above
2. Click "Install suggested plugins"
3. Wait for plugins to install
4. Create admin user
   - Username: admin
   - Password: CHOOSE_STRONG_PASSWORD
```

**Step 2: Add Docker Hub Credentials**
```
1. Go to Manage Jenkins → Manage Credentials
2. Click System → Global Credentials
3. Click "Add Credentials"
4. Fill in:
   - Kind: Username with password
   - Username: YOUR_DOCKER_USERNAME
   - Password: YOUR_DOCKER_HUB_TOKEN (from step 3)
   - ID: dockerhub-creds
   - Description: Docker Hub Credentials
5. Click Create
```

**Step 3: Create Pipeline Job**
```
1. Go to Jenkins Dashboard
2. Click "New Item"
3. Name: fake-news-detection-pipeline
4. Choose: Pipeline
5. Click OK
6. In Pipeline section:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   - Branch: */main
   - Script Path: Jenkinsfile
7. Click Save
```

---

## Phase 5: Update Jenkinsfile

### 8. Update Your Jenkinsfile

Edit file: `d:\AI Based Fake News Detection Systems Using NLP\Jenkinsfile`

Find and replace these values:

```groovy
// BEFORE:
GITHUB_REPO = 'https://github.com/YOUR_USERNAME/YOUR_REPO.git'
GITHUB_BRANCH = 'main'
EC2_USER = 'ubuntu'
EC2_HOST = '35.154.193.96'  // ← CHANGE TO YOUR EC2 IP
EC2_KEY = '/var/lib/jenkins/.ssh/pemkey.pem'
DOCKER_USERNAME = credentials('dockerhub-username')
IMAGE_NAME = 'fake-news-detection'

// AFTER (example):
GITHUB_REPO = 'https://github.com/myusername/fake-news-detection.git'
GITHUB_BRANCH = 'main'
EC2_USER = 'ubuntu'
EC2_HOST = '54.123.45.678'  // ← YOUR ACTUAL EC2 IP
EC2_KEY = '/var/lib/jenkins/.ssh/pemkey.pem'
DOCKER_USERNAME = credentials('dockerhub-creds')
IMAGE_NAME = 'fake-news-detection'
```

Push changes:
```bash
git add Jenkinsfile
git commit -m "Update Jenkinsfile with production values"
git push origin main
```

---

## Phase 6: GitHub Webhook Setup

### 9. Configure GitHub Webhook

Go to your repository on GitHub:

```
1. Go to Settings → Webhooks
2. Click "Add webhook"
3. Fill in:
   - Payload URL: http://JENKINS_IP:8080/github-webhook/
   - Content type: application/json
   - Events: Push events
   - Active: ✓ Checked
4. Click "Add webhook"

Wait for green checkmark in "Recent Deliveries"
```

---

## Phase 7: Test Deployment

### 10. Manual Trigger First Build

In Jenkins dashboard:
```
1. Click on job: fake-news-detection-pipeline
2. Click "Build Now"
3. Click on build number (e.g., #1)
4. Click "Console Output"
5. Watch stages execute:
   ✓ Checkout Code
   ✓ Validate
   ✓ Build Docker Image
   ✓ Test Docker Image
   ✓ Push to Docker Hub
   ✓ Deploy to EC2
   ✓ Health Check
```

### 11. Verify Deployment on EC2

```bash
# SSH to EC2
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Check container running
docker ps

# Should see: fake-news-app container running

# Check logs
docker logs -f fake-news-app

# Test app locally
curl http://localhost/

# Exit
exit

# Test from your computer
curl http://EC2_PUBLIC_IP/
```

---

## Phase 8: Automatic Deployment

### 12. Trigger Automatic Build via Webhook

```bash
# Make any change to your code
echo "# Updated readme" >> README.md

# Commit and push
git add README.md
git commit -m "Trigger automatic deployment"
git push origin main

# Jenkins automatically builds and deploys!
# Watch in Jenkins dashboard

# After ~50 seconds, new version is live on EC2
curl http://EC2_PUBLIC_IP/
```

---

## Useful Commands for Later

### Jenkins Server Management
```bash
# SSH to Jenkins
ssh -i jenkins-key.pem ubuntu@JENKINS_IP

# View Jenkins logs
tail -f /var/log/jenkins/jenkins.log

# Restart Jenkins
sudo systemctl restart jenkins

# Check Jenkins status
systemctl status jenkins

# Update Jenkins plugins
# Go to Manage Jenkins → Plugin Manager → Updates
```

### EC2 Management
```bash
# SSH to EC2
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# View running containers
docker ps

# View all containers
docker ps -a

# Stop container
docker stop fake-news-app

# Start container
docker start fake-news-app

# Remove container
docker rm fake-news-app

# View logs
docker logs fake-news-app
docker logs -f fake-news-app  # Follow logs
docker logs --tail 50 fake-news-app  # Last 50 lines

# View system resources
docker stats fake-news-app

# Remove old images
docker image prune -a

# Remove old containers
docker container prune

# Full system cleanup
docker system prune -a
```

### Docker Hub Management
```bash
# Login to Docker Hub
docker login

# List images
docker images

# Tag image
docker tag fake-news-detection:latest YOUR_USERNAME/fake-news-detection:v1.0

# Push image
docker push YOUR_USERNAME/fake-news-detection:v1.0

# Pull image
docker pull YOUR_USERNAME/fake-news-detection:latest

# Logout
docker logout
```

---

## Troubleshooting Commands

### If Build Fails
```bash
# SSH to Jenkins server
ssh -i jenkins-key.pem ubuntu@JENKINS_IP

# Check Jenkins logs
sudo tail -100 /var/log/jenkins/jenkins.log

# Check if Docker is running
docker ps

# Check Jenkins user permissions
id jenkins
groups jenkins
```

### If EC2 Deployment Fails
```bash
# SSH to EC2
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Check Docker is running
sudo systemctl status docker

# Check if container exists
docker ps -a | grep fake-news

# Check container logs
docker logs fake-news-app

# Check if port 80 is listening
sudo netstat -tulpn | grep 80

# Try manual pull and run
docker pull YOUR_USERNAME/fake-news-detection:latest
docker run -d -p 80:5000 YOUR_USERNAME/fake-news-detection:latest
```

### If SSH Connection Fails
```bash
# Test SSH connection with verbose output
ssh -i your-ec2-key.pem -v ubuntu@EC2_PUBLIC_IP

# Check key permissions
ls -la your-ec2-key.pem
# Should show: -rw------- (600)

# If wrong permissions:
chmod 600 your-ec2-key.pem

# Check EC2 security group allows port 22
# In AWS Console: EC2 → Security Groups → Edit inbound rules
# SSH (22) should allow your Jenkins IP or 0.0.0.0/0
```

---

## Quick Verification Checklist

Run these commands to verify everything:

```bash
# On your local machine
echo "✓ Code available" && ls app.py

# Test Docker locally
docker build -t test:latest . && echo "✓ Docker build works"
docker run -d -p 5001:5000 test:latest && sleep 5
curl -f http://localhost:5001/ && echo "✓ App runs in Docker"
docker stop $(docker ps -q)

# On Jenkins server
ssh -i jenkins-key.pem ubuntu@JENKINS_IP "docker --version && echo '✓ Jenkins has Docker'"

# On EC2
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP "docker ps && echo '✓ EC2 has Docker running'"

# Check webhook
curl -X POST http://JENKINS_IP:8080/github-webhook/ && echo "✓ Webhook endpoint works"
```

---

## One-Line Setup (If You Have Everything Ready)

```bash
# This assumes EC2 is running, Jenkins is running, Docker Hub account exists
git push origin main && \
echo "Pushed to GitHub" && \
echo "Jenkins should auto-build in 30 seconds..." && \
sleep 40 && \
curl http://EC2_PUBLIC_IP/ && \
echo "✓ Deployment successful!"
```

---

**You're all set!** Follow these commands in order and your CI/CD pipeline will be live. 🚀

