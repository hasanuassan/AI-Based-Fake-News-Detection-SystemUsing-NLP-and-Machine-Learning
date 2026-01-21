# 🚀 Complete CI/CD Deployment Guide
## Jenkins + Docker + GitHub + AWS EC2

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Jenkins Configuration](#jenkins-configuration)
5. [GitHub Webhook Setup](#github-webhook-setup)
6. [Troubleshooting](#troubleshooting)
7. [Interview Q&A](#interview-qa)

---

## Prerequisites

**On Your Local Machine:**
- Git installed
- GitHub account
- Code pushed to GitHub repo

**On Jenkins Server (Linux VM):**
- Jenkins installed
- Docker installed
- SSH key pair created
- Jenkins user has sudo access for Docker

**On AWS EC2 Instance:**
- Ubuntu 22.04 or later
- Docker installed
- SSH key pair configured
- Security group allows ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- EC2 has IAM role for ECR access (if using AWS ECR)

**Docker Hub Account:**
- Account created at https://hub.docker.com/
- Public repository created: `your-username/fake-news-detection`

---

## Architecture Overview

```
┌─────────────────┐
│   Developer     │
│  Pushes Code    │
│   to GitHub     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  GitHub Webhook Trigger │  (Automatic)
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Jenkins Pipeline Runs   │
│  1. Clone Repo           │
│  2. Build Docker Image   │
│  3. Test Image           │
│  4. Push to Docker Hub   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────┐
│   Docker Hub         │  (Registry)
│  (Image Repository)  │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────┐
│  EC2 Instance Pulls      │
│  Runs Container          │
│  App Live on Port 80     │
└──────────────────────────┘
```

---

## Step-by-Step Setup

### Step 1️⃣: Prepare GitHub Repository

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Verify files exist
ls -la
# Should show: app.py, Dockerfile, Jenkinsfile, requirements.txt, etc.

# Push to GitHub (if not already done)
git add .
git commit -m "Add Dockerfile and Jenkinsfile for CI/CD"
git push origin main
```

### Step 2️⃣: Create Docker Hub Repository

1. Go to https://hub.docker.com/
2. Sign in with your account
3. Click "Create Repository"
4. **Repository name:** `fake-news-detection`
5. **Visibility:** Public
6. Click "Create"

### Step 3️⃣: Configure Jenkins

#### 3A. Create Docker Hub Credentials

```bash
# SSH into Jenkins server
ssh -i your-key.pem ubuntu@JENKINS_IP

# Inside Jenkins server:
# Navigate to Jenkins Dashboard → Manage Jenkins → Manage Credentials
# → System → Global Credentials
# → Add Credentials
```

**In Jenkins UI:**
- Kind: Username with password
- Username: `your-docker-username`
- Password: (Docker Hub access token)
- ID: `dockerhub-creds`
- Description: `Docker Hub Credentials`
- Click Save

#### 3B. Generate Docker Hub Access Token

1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name: `Jenkins`
4. Permissions: Read, Write, Delete
5. Generate and copy the token
6. Use this token as the password in Jenkins credentials

#### 3C. Create EC2 SSH Key Credentials

**In Jenkins UI:**
- Navigate to: Manage Jenkins → Manage Credentials → System → Global Credentials
- Click "Add Credentials"
- Kind: SSH Username with private key
- Username: `ubuntu`
- Private Key: (Paste your EC2 PEM key)
- ID: `ec2-ssh-key`
- Click Save

**Or place PEM file on Jenkins server:**

```bash
# On Jenkins server:
sudo mkdir -p /var/lib/jenkins/.ssh
sudo cp /path/to/your-key.pem /var/lib/jenkins/.ssh/pemkey.pem
sudo chmod 600 /var/lib/jenkins/.ssh/pemkey.pem
sudo chown jenkins:jenkins /var/lib/jenkins/.ssh/pemkey.pem
```

### Step 4️⃣: Create Jenkins Pipeline Job

**In Jenkins Dashboard:**

1. Click "New Item"
2. Name: `fake-news-detection-pipeline`
3. Choose: "Pipeline"
4. Click OK

**In Pipeline Configuration:**

```
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/YOUR_USERNAME/YOUR_REPO.git
Branch: */main
Script Path: Jenkinsfile
```

**Save the job.**

### Step 5️⃣: Setup GitHub Webhook

**On GitHub Repository:**

1. Go to Settings → Webhooks
2. Click "Add webhook"
3. **Payload URL:** `http://YOUR_JENKINS_IP:8080/github-webhook/`
4. **Content type:** `application/json`
5. **Events:** Push events
6. **Active:** ✓ Checked
7. Click "Add webhook"

### Step 6️⃣: Configure EC2 Instance

```bash
# SSH into EC2
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker (if not already installed)
sudo apt-get install -y docker.io

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Verify Docker is running
sudo systemctl status docker
sudo systemctl enable docker

# Test Docker
sudo docker run hello-world

# Logout and login again for group changes to take effect
exit
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Verify docker works without sudo
docker --version
```

### Step 7️⃣: Update Jenkinsfile with Your Values

Edit `Jenkinsfile` and update these variables:

```groovy
GITHUB_REPO = 'https://github.com/YOUR_USERNAME/YOUR_REPO.git'
EC2_HOST = 'YOUR_EC2_PUBLIC_IP'
DOCKER_USERNAME = 'your-docker-username'
EC2_KEY = '/var/lib/jenkins/.ssh/pemkey.pem'
```

### Step 8️⃣: Trigger First Build

```bash
# Option 1: Manual Trigger in Jenkins Dashboard
# Go to your pipeline job → Click "Build Now"

# Option 2: Push code to GitHub (webhook will trigger automatically)
git add .
git commit -m "Trigger CI/CD pipeline"
git push origin main
```

### Step 9️⃣: Monitor Build

1. Open Jenkins Dashboard
2. Click on your pipeline job
3. Click on the build number
4. Click "Console Output"
5. Watch the pipeline stages execute:
   - ✅ Checkout Code
   - ✅ Validate
   - ✅ Build Docker Image
   - ✅ Test Docker Image
   - ✅ Push to Docker Hub
   - ✅ Deploy to EC2
   - ✅ Health Check

### Step 🔟: Verify Deployment

```bash
# Check if container is running on EC2
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# View running containers
docker ps

# View container logs
docker logs fake-news-app

# Test the application
curl http://localhost/

# From your local machine
curl http://EC2_PUBLIC_IP/
```

---

## Jenkins Configuration Details

### Environment Variables Explained

| Variable | Purpose |
|----------|---------|
| `GITHUB_REPO` | Source code location |
| `EC2_HOST` | EC2 public IP address |
| `EC2_USER` | SSH user (ubuntu) |
| `EC2_KEY` | Path to SSH private key |
| `DOCKER_USERNAME` | Docker Hub account |
| `IMAGE_NAME` | Container image name |
| `IMAGE_TAG` | Build number (auto-incremented) |
| `FULL_IMAGE` | Complete image path |
| `LATEST_IMAGE` | Latest tag for production |

### Pipeline Stages Explained

| Stage | What It Does |
|-------|------------|
| **Checkout Code** | Clones code from GitHub |
| **Validate** | Checks Docker & files exist |
| **Build Docker Image** | Creates Docker image from Dockerfile |
| **Test Docker Image** | Runs container and tests it |
| **Push to Docker Hub** | Uploads image to Docker registry |
| **Deploy to EC2** | Pulls image and runs on EC2 |
| **Health Check** | Verifies app is responding |

---

## GitHub Webhook Setup

### How Webhook Works

1. You push code to GitHub
2. GitHub sends HTTP POST to Jenkins webhook URL
3. Jenkins receives notification
4. Jenkins automatically triggers the pipeline
5. Pipeline builds and deploys your app

### Testing Webhook

In GitHub repository:

1. Go to Settings → Webhooks
2. Click on your webhook
3. Scroll to "Recent Deliveries"
4. Click on a delivery to see request/response
5. Should see HTTP 200 response

**Common Issues:**
- Jenkins URL unreachable from GitHub → Check firewall
- Incorrect webhook URL → Verify in Jenkins configuration
- No permissions → Check GitHub token permissions

---

## Troubleshooting

### Issue 1: Build Fails at "Checkout Code"

**Error:** `Repository not found`

**Solution:**
```bash
# Make sure Jenkinsfile has correct GitHub URL
# Edit Jenkinsfile:
GITHUB_REPO = 'https://github.com/YOUR_USERNAME/YOUR_REPO.git'

# For private repos, add SSH credentials
# In Jenkins: Credentials → SSH key for GitHub
```

---

### Issue 2: Docker Build Fails

**Error:** `Dockerfile not found`

**Solution:**
```bash
# Verify Dockerfile is in repo root
ls -la Dockerfile

# If in subdirectory, update Jenkinsfile:
docker build -t ${FULL_IMAGE} ./path/to/dockerfile
```

---

### Issue 3: Push to Docker Hub Fails

**Error:** `denied: requested access to the resource is denied`

**Solution:**
1. Check Docker Hub credentials in Jenkins
2. Verify access token is valid
3. Regenerate token if expired:
   - https://hub.docker.com/settings/security
4. Update Jenkins credentials

---

### Issue 4: Deploy to EC2 Fails

**Error:** `Permission denied (publickey)`

**Solution:**
```bash
# On Jenkins server, verify SSH key
cat /var/lib/jenkins/.ssh/pemkey.pem

# On EC2, verify security group allows port 22
# Check EC2 console → Security Groups

# Test SSH connection
ssh -i /var/lib/jenkins/.ssh/pemkey.pem -v ubuntu@EC2_IP

# If permissions issue:
sudo chmod 600 /var/lib/jenkins/.ssh/pemkey.pem
sudo chown jenkins:jenkins /var/lib/jenkins/.ssh/pemkey.pem
```

---

### Issue 5: Health Check Fails

**Error:** `curl: (7) Failed to connect`

**Solution:**
```bash
# On EC2, check if container is running
docker ps

# Check container logs
docker logs fake-news-app

# Check if port 80 is listening
sudo netstat -tulpn | grep 80

# Check security group allows port 80
# EC2 Console → Security Groups → Edit inbound rules
# Add: HTTP (80) from 0.0.0.0/0
```

---

## Interview Q&A

### Q1: What happens when I push code to GitHub?

**Answer:**
GitHub sends a webhook notification to Jenkins. The webhook is an HTTP POST request that contains information about the commit. Jenkins receives this notification and automatically triggers the pipeline defined in the Jenkinsfile. This removes the need for manual builds and is the foundation of CI/CD automation.

---

### Q2: How does GitHub trigger Jenkins?

**Answer:**
1. You configure a webhook in GitHub settings (Settings → Webhooks)
2. Webhook URL points to Jenkins: `http://jenkins-server:8080/github-webhook/`
3. When you push code, GitHub sends POST request to this URL
4. Jenkins webhook plugin receives the request
5. Jenkins automatically starts the pipeline
6. Git plugin in Jenkins clones the code
7. Pipeline defined in Jenkinsfile executes

---

### Q3: How does Jenkins build a Docker image?

**Answer:**
1. Jenkins checks out your code from GitHub
2. Jenkins reads the `Dockerfile` in the repo
3. Runs `docker build` command:
```bash
docker build -t username/app-name:tag-number .
```
4. Docker creates layers for each instruction:
   - Base image layer (Python 3.11)
   - Dependencies layer (pip install)
   - Application code layer
5. Final image is created with all layers combined
6. Image is tagged with version number and "latest"

---

### Q4: What is a Docker registry?

**Answer:**
A Docker registry is a centralized repository where Docker images are stored and accessed. Think of it like GitHub for images. You can push images to store them and pull images to use them on different servers. Popular registries:
- **Docker Hub** (public, free)
- **Amazon ECR** (AWS)
- **Google Container Registry** (GCP)
- **Azure Container Registry** (Azure)

---

### Q5: What's the difference between public and private registries?

**Answer:**

| Aspect | Public | Private |
|--------|--------|---------|
| Access | Anyone can pull | Only authorized users |
| Security | Source code visible | Proprietary code hidden |
| Use Case | Open source projects | Production apps, sensitive code |
| Cost | Free | Paid |
| Example | Docker Hub public images | Company internal registry |

---

### Q6: Why are images pushed to a registry?

**Answer:**
1. **Centralized storage** - All images in one place
2. **Version control** - Different tags for different versions
3. **Distribution** - Pull on any server (Jenkins, EC2, Kubernetes)
4. **Backup** - If local image is deleted, can pull from registry
5. **Sharing** - Team members can use same image
6. **CI/CD automation** - Jenkins can push, EC2 can pull automatically

---

### Q7: How does Jenkins push images to a registry?

**Answer:**
```bash
# Step 1: Login to Docker Hub
docker login -u username -p password

# Step 2: Tag image for registry
docker tag local-image:tag username/image-name:tag

# Step 3: Push to registry
docker push username/image-name:tag

# Step 4: Logout for security
docker logout
```

**In Jenkinsfile:**
```groovy
withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', ...)]) {
    sh 'echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin'
    sh 'docker push ${FULL_IMAGE}'
    sh 'docker logout'
}
```

---

### Q8: How does EC2 pull the image and run the container?

**Answer:**
```bash
# Step 1: Login to Docker Hub
docker login -u username -p password

# Step 2: Pull image
docker pull username/image-name:latest

# Step 3: Run container
docker run -d \
  --name app-container \
  --restart always \
  -p 80:5000 \
  username/image-name:latest

# Step 4: Verify
docker ps
```

**What this does:**
- `-d` - Run in background
- `--name` - Container name
- `--restart always` - Auto-restart if crashes
- `-p 80:5000` - Map port 80 (external) to 5000 (Flask)

---

### Q9: Why must Docker be installed on EC2?

**Answer:**
Docker must be installed because:
1. **Docker daemon** - The Docker service that runs containers
2. **Docker CLI** - Command-line tool to manage containers
3. **Container runtime** - Needed to execute containerized applications
4. **Image management** - Pull, store, run images
5. **Process isolation** - Docker provides process isolation for containers

Without Docker, the EC2 instance cannot:
- Pull Docker images
- Run containers
- Manage container lifecycle

---

### Q10: Complete end-to-end CI/CD flow

**Answer:**

```
PHASE 1: DEVELOPMENT (Local Machine)
├─ Write code
├─ Test locally
└─ git push to GitHub

PHASE 2: GITHUB WEBHOOK TRIGGER
├─ GitHub detects push
└─ Sends webhook to Jenkins

PHASE 3: JENKINS PIPELINE
├─ Stage 1: Checkout
│  └─ git clone from GitHub
├─ Stage 2: Build
│  └─ docker build -t image:tag .
├─ Stage 3: Test
│  └─ docker run and curl test
├─ Stage 4: Push
│  ├─ docker login to Docker Hub
│  └─ docker push image:tag
└─ Stage 5: Deploy
   ├─ SSH to EC2
   ├─ docker pull image:latest
   └─ docker run -d --name app image:latest

PHASE 4: APPLICATION LIVE
├─ Container running on EC2
├─ Accessible at http://ec2-public-ip/
└─ Health check passes
```

---

### Q11: What if the deployment fails?

**Answer:**
1. Check Jenkins console output
2. Identify failed stage (Build, Push, Deploy)
3. Review error message
4. Fix issue in code/Dockerfile/Jenkinsfile
5. Push fix to GitHub
6. Webhook automatically retriggers pipeline
7. Pipeline runs again with fix
8. If deployment fails, old container stays running (no downtime)

---

### Q12: How do you handle multiple environments (Dev, Staging, Prod)?

**Answer:**
```groovy
// Environment-specific configuration
environment {
    ENVIRONMENT = "${BRANCH_NAME == 'main' ? 'production' : 'staging'}"
    EC2_HOST = "${BRANCH_NAME == 'main' ? PROD_IP : STAGING_IP}"
}

// Conditional deployment
stage('Deploy') {
    when {
        branch 'main'  // Only deploy to prod on main branch
    }
    steps {
        // Deploy to production
    }
}
```

---

### Q13: How do you do zero-downtime deployments?

**Answer:**
1. **Blue-Green Deployment:**
   - Blue container (old version) running
   - Start Green container (new version)
   - Run health checks on Green
   - Switch traffic to Green
   - Keep Blue as fallback

2. **Rolling Update:**
   - Gradually replace containers
   - One at a time to maintain availability

3. **In Jenkinsfile:**
```bash
# Stop old container after new one is healthy
docker stop fake-news-app
docker rm fake-news-app

# Run new container
docker run -d --name fake-news-app image:latest

# Verify health before considering deployment successful
```

---

### Q14: How do you secure credentials in Jenkins?

**Answer:**
1. **Never hardcode passwords:**
   ```groovy
   // ❌ WRONG
   docker login -u admin -p password123
   
   // ✅ CORRECT
   withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', ...)]) {
       docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}
   }
   ```

2. **Use Jenkins Credentials Store:**
   - Manage Jenkins → Manage Credentials
   - Store sensitive data encrypted

3. **Use SSH keys instead of passwords:**
   - EC2: SSH keys instead of username/password
   - GitHub: Personal access token

---

### Q15: How do you monitor deployments?

**Answer:**
1. **Health checks:**
```bash
curl -f http://ec2-public-ip/ || exit 1
```

2. **Container logs:**
```bash
docker logs -f fake-news-app
```

3. **Metrics:**
   - CPU usage
   - Memory usage
   - Network I/O

4. **Alerts:**
   - Slack notifications on failure
   - Email alerts
   - PagerDuty for critical issues

---

## Quick Reference Commands

### Jenkins
```bash
# View Jenkins logs
tail -f /var/log/jenkins/jenkins.log

# Restart Jenkins
sudo systemctl restart jenkins

# Check Jenkins status
systemctl status jenkins
```

### Docker
```bash
# View images
docker images

# View running containers
docker ps

# View all containers
docker ps -a

# View container logs
docker logs container-name

# Stop container
docker stop container-name

# Remove container
docker rm container-name

# Remove image
docker rmi image-name:tag
```

### EC2
```bash
# SSH into EC2
ssh -i key.pem ubuntu@ec2-ip

# View docker status
systemctl status docker

# View running containers
docker ps

# View container logs
docker logs -f container-name

# Check port 80 is listening
sudo netstat -tulpn | grep 80
```

---

## Checklist Before Going to Production

- [ ] GitHub repository contains all code
- [ ] Dockerfile tested locally
- [ ] Jenkinsfile syntax is valid
- [ ] Docker Hub account created and repo public/private
- [ ] Jenkins credentials configured securely
- [ ] EC2 security group allows ports 22, 80, 443
- [ ] EC2 has Docker installed
- [ ] GitHub webhook configured correctly
- [ ] Test build triggers manually in Jenkins
- [ ] Test deployment by pushing code to GitHub
- [ ] Health check passes on EC2
- [ ] Application accessible at http://ec2-public-ip/
- [ ] Logs are viewable on EC2
- [ ] Rollback procedure documented

---

## Next Steps (Advanced Topics)

1. **Use AWS ECR instead of Docker Hub** (private registry)
2. **Add unit tests** to pipeline
3. **Add code quality checks** (SonarQube)
4. **Use Kubernetes** for container orchestration
5. **Implement auto-scaling** based on load
6. **Add monitoring** with Prometheus/Grafana
7. **Use blue-green deployments** for zero downtime
8. **Implement database migrations** in pipeline

---

**You're now ready to deploy production applications using Jenkins, Docker, and AWS EC2!** 🚀

