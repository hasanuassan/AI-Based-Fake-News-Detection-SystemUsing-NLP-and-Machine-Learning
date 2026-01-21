# 🔧 Troubleshooting & Debugging Guide

## Problem 1: Jenkins Won't Build

### Error: "Repository not found"

```
ERROR: Repository not found
fatal: could not read Username for 'https://github.com':
```

**Cause:** GitHub repo URL incorrect or repo is private

**Solution:**
```bash
# 1. Verify repo URL
git remote -v

# 2. In Jenkinsfile, use correct URL:
GITHUB_REPO = 'https://github.com/YOUR_USERNAME/YOUR_REPO.git'

# 3. For private repos, add SSH credentials in Jenkins
# Manage Jenkins → Manage Credentials → Add SSH key
```

---

### Error: "Cannot find Jenkinsfile"

```
ERROR: Scripted Pipeline script not found in workspace
```

**Cause:** Jenkinsfile not in repo root or not pushed to GitHub

**Solution:**
```bash
# 1. Verify Jenkinsfile exists locally
ls -la Jenkinsfile

# 2. Commit and push
git add Jenkinsfile
git commit -m "Add Jenkinsfile"
git push origin main

# 3. In Jenkins job configuration:
# Pipeline → Definition → Script Path
# Must be: Jenkinsfile (no path prefix if in root)
```

---

### Error: "Invalid Jenkinsfile syntax"

```
ERROR: Expected string as argument
```

**Cause:** Groovy syntax error in Jenkinsfile

**Solution:**
```groovy
// Common mistakes:

// ❌ WRONG: Missing quotes
DOCKER_USERNAME = 'username

// ✅ CORRECT: Matching quotes
DOCKER_USERNAME = 'username'

// ❌ WRONG: Missing curly braces
sh 'echo $DOCKER_USERNAME'

// ✅ CORRECT: Use single quotes for variable substitution
sh '''
    echo ${DOCKER_USERNAME}
'''

// ❌ WRONG: Missing semicolon
sh 'docker build -t image .'
    sh 'docker push image'

// ✅ CORRECT: Either separate sh blocks or chain with &&
sh '''
    docker build -t image .
    docker push image
'''
```

**Debug:**
```bash
# Check Jenkinsfile syntax online at:
# https://www.jenkins.io/doc/book/pipeline/syntax/

# Or validate locally:
# Most IDEs will highlight Groovy syntax errors
```

---

## Problem 2: Docker Build Fails

### Error: "Dockerfile not found"

```
ERROR: Dockerfile not found
```

**Cause:** Dockerfile not in directory where docker build is run

**Solution:**
```bash
# 1. Verify Dockerfile exists locally
ls -la Dockerfile

# 2. Dockerfile must be in repo root
# Or specify path in Jenkinsfile:
docker build -t ${FULL_IMAGE} --file Dockerfile .

# 3. Commit Dockerfile
git add Dockerfile
git commit -m "Add Dockerfile"
git push origin main
```

---

### Error: "Requirements file not found"

```
ERROR: COPY requirements.txt . : no source files were specified
```

**Cause:** requirements.txt not in repo or not at root level

**Solution:**
```bash
# 1. Verify file exists
ls -la requirements.txt

# 2. Dockerfile COPY command:
# ❌ WRONG if file in subdirectory
COPY requirements.txt .

# ✅ CORRECT if in subdirectory
COPY config/requirements.txt .

# 3. Commit file
git add requirements.txt
git commit -m "Add requirements"
git push origin main
```

---

### Error: "pip install fails"

```
ERROR: Could not find a version that satisfies the requirement
ERROR: No matching distribution found for flask==3.0.0
```

**Cause:** Package version doesn't exist or pip can't reach PyPI

**Solution:**
```bash
# 1. Check internet connection in Docker
# Add to Dockerfile test:
RUN pip install --index-url https://pypi.org/simple/ flask==3.0.0

# 2. Verify package versions exist:
curl https://pypi.org/pypi/flask/json | grep "3.0.0"

# 3. Update requirements.txt with available versions:
pip index versions flask  # Shows available versions
pip install --upgrade-strategy only-if-needed -r requirements.txt
```

---

### Error: "NLTK data download fails"

```
ERROR: Error downloading punkt
ERROR: Failed to download required files
```

**Cause:** No internet access in Docker or NLTK server down

**Solution:**
```bash
# In Dockerfile, add retry logic:
RUN python -m nltk.downloader -d /usr/share/nltk_data punkt || \
    python -c "import nltk; nltk.download('punkt', download_dir='/usr/share/nltk_data')"

# Or download during local testing:
python -m nltk.downloader punkt
# This caches data locally before Docker build
```

---

## Problem 3: Docker Image Push Fails

### Error: "Authentication required"

```
ERROR: denied: requested access to the resource is denied
```

**Cause:** Not logged in to Docker Hub or credentials wrong

**Solution:**
```bash
# 1. Check Jenkins credentials
# Manage Jenkins → Manage Credentials
# Verify dockerhub-creds exists with correct username/token

# 2. Generate new token:
# https://hub.docker.com/settings/security
# Click "New Access Token"
# Name: Jenkins
# Permissions: Read, Write, Delete

# 3. Update Jenkins credentials:
# Click on dockerhub-creds → Update
# Paste new token as password

# 4. Test locally:
docker login -u YOUR_USERNAME -p YOUR_TOKEN
docker push your-username/repo:latest
docker logout
```

---

### Error: "Repository not found"

```
ERROR: 404 Not Found
```

**Cause:** Docker Hub repo doesn't exist or different username

**Solution:**
```bash
# 1. Create repo on Docker Hub:
# Visit https://hub.docker.com/
# Click Repositories → Create Repository
# Name: fake-news-detection
# Visibility: Public
# Click Create

# 2. Verify repo name in Jenkinsfile:
DOCKER_USERNAME = 'your-actual-docker-username'
IMAGE_NAME = 'fake-news-detection'
FULL_IMAGE = "${DOCKER_USERNAME}/${IMAGE_NAME}:${BUILD_NUMBER}"

# 3. Verify by pushing manually:
docker login
docker tag test:latest your-username/fake-news-detection:latest
docker push your-username/fake-news-detection:latest
```

---

### Error: "Image size too large"

```
ERROR: Pushed image exceeds size limits
```

**Cause:** Dockerfile creating large image

**Solution:**
```dockerfile
# Use multi-stage build (already in your updated Dockerfile):
FROM python:3.11-slim as builder
# Install dependencies in builder

FROM python:3.11-slim
# Copy only what's needed to runtime stage
COPY --from=builder /opt/venv /opt/venv

# This reduces image size by 50-70%
```

**Check image size:**
```bash
docker images | grep fake-news
# Shows SIZE column

# Optimize Dockerfile:
# 1. Use .slim or .alpine base images
# 2. Use multi-stage builds
# 3. Remove unnecessary files after installation
# 4. Combine RUN commands to reduce layers

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*  # Remove apt cache
```

---

## Problem 4: EC2 Deployment Fails

### Error: "Permission denied (publickey)"

```
ERROR: Permission denied (publickey)
fatal: Could not read from remote repository
```

**Cause:** SSH key missing or permissions wrong

**Solution:**
```bash
# 1. On Jenkins server, verify SSH key exists:
ls -la /var/lib/jenkins/.ssh/pemkey.pem

# 2. Check permissions:
stat /var/lib/jenkins/.ssh/pemkey.pem
# Should show: -rw------- (600)

# 3. Fix permissions:
sudo chmod 600 /var/lib/jenkins/.ssh/pemkey.pem
sudo chown jenkins:jenkins /var/lib/jenkins/.ssh/pemkey.pem

# 4. Test SSH connection:
sudo -u jenkins ssh -i /var/lib/jenkins/.ssh/pemkey.pem \
  -o StrictHostKeyChecking=no \
  ubuntu@EC2_PUBLIC_IP \
  "docker ps"

# Should show running containers
```

---

### Error: "SSH connection timeout"

```
ERROR: Connection timed out
```

**Cause:** EC2 security group doesn't allow SSH from Jenkins

**Solution:**
```bash
# 1. In AWS Console:
# EC2 → Security Groups → Select your security group
# Inbound Rules → Edit Inbound Rules
# Add rule:
#   Type: SSH
#   Port: 22
#   Source: JENKINS_IP/32 (or 0.0.0.0/0 for anywhere)
# Save

# 2. Verify rule is applied:
aws ec2 describe-security-groups --group-ids sg-xxxxx

# 3. Test SSH connection:
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

---

### Error: "Docker not found on EC2"

```
ERROR: docker: command not found
```

**Cause:** Docker not installed on EC2

**Solution:**
```bash
# SSH to EC2 and install Docker:
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Inside EC2:
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add ubuntu user to docker group:
sudo usermod -aG docker ubuntu

# Exit and login again:
exit
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Verify:
docker --version
```

---

### Error: "Docker pull fails on EC2"

```
ERROR: Error response from daemon: failed to register layer
```

**Cause:** Out of disk space or networking issue

**Solution:**
```bash
# SSH to EC2:
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# 1. Check disk space:
df -h
# Should have at least 5GB free

# 2. If full, remove old images:
docker image prune -a  # Remove unused images
docker container prune  # Remove stopped containers

# 3. Check internet connectivity:
curl -I https://hub.docker.com

# 4. Manually test pull:
docker pull your-username/fake-news-detection:latest

# 5. View pull progress:
docker pull -v your-username/fake-news-detection:latest
```

---

## Problem 5: Container Won't Start

### Error: "Container exits immediately"

```
docker ps -a shows fake-news-app exited
docker logs fake-news-app shows error
```

**Cause:** App crashes on startup

**Solution:**
```bash
# SSH to EC2 and check logs:
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# View container logs:
docker logs fake-news-app
# Shows the error message

# Common issues:
# 1. Missing dependencies
#    → Verify all packages in requirements.txt

# 2. Port already in use
#    → netstat -tulpn | grep 5000
#    → Kill process: kill -9 PID

# 3. Flask app not configured correctly
#    → Verify app.py has: if __name__ == '__main__': app.run()

# 4. App crashes on import
#    → Test locally: python app.py

# 5. Working directory issue
#    → Verify files in /app: docker run -it image:tag ls -la /app
```

---

### Error: "Port 80 already in use"

```
ERROR: Bind for 0.0.0.0:80 failed
```

**Cause:** Another process using port 80

**Solution:**
```bash
# SSH to EC2:
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

# Find process using port 80:
sudo lsof -i :80
# or
sudo netstat -tulpn | grep :80

# Stop the process:
sudo kill -9 PID

# Or use different port in Jenkinsfile:
docker run -d -p 8000:5000 fake-news-app
# Then access at: http://ec2-ip:8000/
```

---

## Problem 6: Application Not Responding

### Error: "curl: (7) Failed to connect"

```
curl http://EC2_PUBLIC_IP/
curl: (7) Failed to connect to EC2_PUBLIC_IP port 80: Connection refused
```

**Cause:** Container not running, port not mapped, or security group issue

**Solution:**
```bash
# 1. SSH to EC2 and check container:
ssh -i your-ec2-key.pem ubuntu@EC2_PUBLIC_IP

docker ps
# Should see fake-news-app running

# If not running:
docker start fake-news-app
docker logs fake-news-app  # Check for errors

# 2. Check port mapping:
docker port fake-news-app
# Should show: 5000/tcp → 0.0.0.0:80

# 3. Test inside container:
docker exec fake-news-app curl http://localhost:5000/

# 4. Check security group allows port 80:
# AWS Console → EC2 → Security Groups
# Inbound Rules → Should have HTTP (80) from 0.0.0.0/0

# 5. Test from EC2 locally:
curl http://localhost/

# 6. If works locally but not from outside:
# Security group issue - add rule:
#   Type: HTTP
#   Port: 80
#   Source: 0.0.0.0/0
```

---

## Problem 7: Health Check Fails

### Error: "Health check failing repeatedly"

```
WARNING: Container restarting due to failed health checks
```

**Cause:** Flask app not responding to health check endpoint

**Solution:**
```bash
# 1. Verify Flask app has root endpoint:
# In app.py:
@app.route('/')
def home():
    return jsonify({'status': 'ok'}), 200

# 2. Test inside container:
docker exec fake-news-app curl -f http://localhost:5000/

# 3. View health status:
docker inspect fake-news-app | grep -A 10 '"Health"'

# 4. Check container logs for startup errors:
docker logs -f fake-news-app

# 5. Increase health check timeout in Jenkinsfile:
# From: --health-timeout=10s
# To: --health-timeout=15s

# 6. Rebuild and redeploy:
git add Jenkinsfile
git commit -m "Increase health check timeout"
git push origin main
```

---

## Problem 8: GitHub Webhook Not Triggering Build

### Error: "Webhook delivery fails"

```
GitHub webhook shows red X in "Recent Deliveries"
HTTP 404 or 500 response
```

**Cause:** Jenkins webhook URL incorrect or Jenkins unreachable

**Solution:**
```bash
# 1. Verify webhook URL in GitHub:
# Repository → Settings → Webhooks
# Payload URL should be:
# http://JENKINS_IP:8080/github-webhook/

# 2. Check Jenkins is running:
# Try to access: http://JENKINS_IP:8080
# Should show Jenkins dashboard

# 3. Test webhook manually:
curl -X POST http://JENKINS_IP:8080/github-webhook/ \
  -H "Content-Type: application/json" \
  -d '{"action":"push"}'

# Should return 200 OK

# 4. If firewall blocks access:
# Open port 8080 on Jenkins server:
sudo ufw allow 8080

# 5. Check GitHub can reach Jenkins:
# From any internet-connected machine:
curl -X POST http://JENKINS_IP:8080/github-webhook/

# 6. In Jenkins, verify webhook plugin installed:
# Manage Jenkins → Manage Plugins
# Search: GitHub Integration
# Should be installed
```

---

## Quick Diagnostics Checklist

```bash
# Run this to diagnose all issues:

echo "=== LOCAL CHECKS ==="
echo "Git status:"
git status
echo "Docker version:"
docker --version
echo ""

echo "=== JENKINS CHECKS ==="
echo "Jenkins running:"
curl -I http://JENKINS_IP:8080 | head -1
echo ""

echo "=== EC2 CHECKS ==="
echo "SSH connectivity:"
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP "echo 'Connected'"
echo "Docker on EC2:"
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP "docker --version"
echo "Container running:"
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP "docker ps | grep fake-news"
echo ""

echo "=== APPLICATION CHECKS ==="
echo "App responding:"
curl -I http://EC2_PUBLIC_IP/ | head -1
echo ""

echo "=== DOCKER HUB CHECKS ==="
echo "Docker login test:"
docker login -u $DOCKER_USERNAME -p $DOCKER_TOKEN
docker push your-username/fake-news-detection:test
echo "Push successful"
```

---

## Common Error Messages & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `denied: requested access to the resource is denied` | Docker credentials wrong | Update Jenkins credentials |
| `Error response from daemon: cannot find image` | Image not built or wrong name | Rebuild image, check name in Jenkinsfile |
| `Address already in use` | Port conflict | Change port in docker run command |
| `fatal: could not read Username` | GitHub auth failed | Use SSH keys or personal access token |
| `Connection refused` | Service not running | Start Docker, Jenkins, or container |
| `Timeout` | Server not responding | Check security groups, check app logs |
| `Permission denied` | File/key permissions | chmod 600 for keys, check user groups |
| `Disk full` | Out of space | Remove old images, increase storage |
| `Image too large` | Docker image bloated | Use multi-stage build, reduce dependencies |
| `Health check failing` | App not healthy | Check logs, verify endpoint exists |

---

## Debug Commands

```bash
# Jenkins Debugging
tail -f /var/log/jenkins/jenkins.log          # Watch Jenkins logs
sudo systemctl status jenkins                  # Check Jenkins status
curl http://JENKINS_IP:8080/api/json         # Check Jenkins API

# Docker Debugging
docker ps -a                                   # Show all containers
docker logs -f container-name                  # Follow container logs
docker inspect container-name                  # Full container details
docker exec -it container /bin/bash            # Shell into container
docker stats                                   # Real-time resource usage
docker images                                  # List all images
docker system df                               # Show disk usage

# EC2 Debugging
ssh -v ubuntu@EC2_IP                          # Verbose SSH output
systemctl status docker                       # Docker service status
journalctl -u docker -f                       # Docker journal logs
curl -v http://localhost/                     # Verbose curl output
tcpdump -i any port 80                        # Capture port 80 traffic

# Network Debugging
nslookup docker.io                            # DNS resolution
curl -I https://hub.docker.com               # Check connectivity
telnet JENKINS_IP 8080                        # Test port connectivity
aws ec2 describe-security-groups --group-ids sg-xxx  # Check security group
```

---

## When All Else Fails

```
1. Check Jenkins console output first
   → Jenkins Dashboard → Build # → Console Output
   → Shows exactly where it failed

2. Check Docker logs
   → docker logs fake-news-app
   → Shows application errors

3. Check GitHub webhook delivery
   → Repository → Settings → Webhooks
   → Recent Deliveries → Click delivery
   → Shows request and response

4. Enable verbose logging
   → Jenkins: Manage Jenkins → System → Log Level
   → Set to DEBUG
   → Rebuild
   → More detailed logs

5. Test each component individually
   → Test Docker build locally
   → Test Docker push manually
   → Test EC2 SSH connectivity
   → Test app in container manually

6. Read error message carefully
   → Usually tells you exactly what's wrong
   → Google the exact error message

7. Ask for help
   → Jenkins community: https://www.jenkins.io/
   → Docker community: https://forums.docker.com/
   → Stack Overflow: tag questions appropriately
```

---

**Remember:** Every error message is helpful! 🔍 Read it carefully and work backwards.

