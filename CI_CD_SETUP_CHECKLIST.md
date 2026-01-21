# ✅ CI/CD Setup Checklist

## Local Machine (Your Computer)

- [ ] Git installed (`git --version`)
- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] `Dockerfile` in repository root
- [ ] `Jenkinsfile` in repository root
- [ ] `requirements.txt` with all dependencies
- [ ] `app.py` running locally without errors

## Docker Hub Account Setup

- [ ] Docker Hub account created at https://hub.docker.com/
- [ ] Public repository created: `your-username/fake-news-detection`
- [ ] Access token generated (Settings → Security)
- [ ] Docker token saved securely

## Jenkins Server Setup

### Installation & Access
- [ ] Jenkins installed on Linux server
- [ ] Jenkins is running (`systemctl status jenkins`)
- [ ] Can access Jenkins dashboard: `http://jenkins-ip:8080`
- [ ] Jenkins user can use Docker (`sudo usermod -aG docker jenkins`)
- [ ] SSH key created for EC2: `/var/lib/jenkins/.ssh/pemkey.pem`
- [ ] SSH key permissions correct (`chmod 600 /var/lib/jenkins/.ssh/pemkey.pem`)

### Jenkins Credentials
- [ ] Docker Hub credentials added (Manage Jenkins → Manage Credentials)
  - [ ] Credential ID: `dockerhub-creds`
  - [ ] Username: Docker Hub username
  - [ ] Password: Docker Hub access token
- [ ] EC2 SSH key configured
  - [ ] Credential ID: `ec2-ssh-key`
  - [ ] SSH key pasted correctly

### Jenkins Pipeline Job
- [ ] New Pipeline job created
- [ ] Job name: `fake-news-detection-pipeline`
- [ ] Repository URL: `https://github.com/your-username/your-repo.git`
- [ ] Branch: `*/main` or `*/master`
- [ ] Script path: `Jenkinsfile`
- [ ] Build trigger: GitHub push (webhook)

## GitHub Configuration

### Webhook Setup
- [ ] Go to repository Settings → Webhooks
- [ ] Webhook URL: `http://jenkins-ip:8080/github-webhook/`
- [ ] Content type: `application/json`
- [ ] Events: Push events only
- [ ] Active: ✓ Checked
- [ ] Webhook test shows green checkmark (Recent Deliveries)

### Repository Settings
- [ ] Dockerfile is committed and pushed
- [ ] Jenkinsfile is committed and pushed
- [ ] requirements.txt is committed and pushed
- [ ] .gitignore excludes `__pycache__/`, `.venv/`, `*.pyc`
- [ ] README.md explains how to run the app

## AWS EC2 Instance Setup

### Instance Configuration
- [ ] Ubuntu 22.04 or later
- [ ] Instance is running
- [ ] Security group allows:
  - [ ] Port 22 (SSH) from your IP or Jenkins IP
  - [ ] Port 80 (HTTP) from 0.0.0.0/0
  - [ ] Port 443 (HTTPS) from 0.0.0.0/0
- [ ] Public IP address assigned
- [ ] EC2 key pair downloaded (.pem file)

### Docker Installation
- [ ] Docker installed on EC2: `docker --version`
- [ ] Docker running: `sudo systemctl status docker`
- [ ] Docker starts on boot: `sudo systemctl enable docker`
- [ ] Ubuntu user can use Docker: `sudo usermod -aG docker ubuntu`
- [ ] Verify: `docker run hello-world` (without sudo)

### SSH Configuration
- [ ] SSH key permissions correct: `chmod 600 your-key.pem`
- [ ] Can SSH to EC2: `ssh -i your-key.pem ubuntu@ec2-public-ip`
- [ ] SSH key copied to Jenkins server
- [ ] SSH works from Jenkins: `ssh -i /var/lib/jenkins/.ssh/pemkey.pem ubuntu@ec2-ip`

## Jenkinsfile Configuration

Update these values in your `Jenkinsfile`:

```groovy
GITHUB_REPO = 'https://github.com/YOUR_USERNAME/YOUR_REPO.git'
GITHUB_BRANCH = 'main'
EC2_USER = 'ubuntu'
EC2_HOST = 'YOUR_EC2_PUBLIC_IP'
EC2_KEY = '/var/lib/jenkins/.ssh/pemkey.pem'
DOCKER_USERNAME = 'your-docker-username'
```

- [ ] All above values updated in Jenkinsfile
- [ ] Jenkinsfile pushed to GitHub

## Dockerfile Verification

Your `Dockerfile` should:

- [ ] Use Python 3.11 base image
- [ ] Install system dependencies
- [ ] Copy requirements.txt
- [ ] Run `pip install -r requirements.txt`
- [ ] Download NLTK data
- [ ] Copy application code
- [ ] Expose port 5000
- [ ] Set HEALTHCHECK
- [ ] Run Flask app on `0.0.0.0`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
COPY . .
EXPOSE 5000
HEALTHCHECK CMD curl -f http://localhost:5000/
CMD ["python", "app.py"]
```

- [ ] Dockerfile syntax valid
- [ ] Can build locally: `docker build -t test:latest .`
- [ ] Can run locally: `docker run -p 5000:5000 test:latest`
- [ ] App accessible at `http://localhost:5000`

## Testing Before Production

### Local Testing
- [ ] App runs without Docker errors
- [ ] All dependencies installed
- [ ] No Python import errors
- [ ] Health endpoint responds

### Jenkins Testing
- [ ] Manual build trigger works
- [ ] Build completes successfully
- [ ] All stages pass:
  - [ ] ✅ Checkout Code
  - [ ] ✅ Validate
  - [ ] ✅ Build Docker Image
  - [ ] ✅ Test Docker Image
  - [ ] ✅ Push to Docker Hub
  - [ ] ✅ Deploy to EC2
  - [ ] ✅ Health Check

### GitHub Webhook Testing
- [ ] Push code to GitHub
- [ ] Webhook automatically triggers Jenkins build
- [ ] Check GitHub webhook delivery status: Settings → Webhooks → Recent Deliveries
- [ ] Should see HTTP 200 status

### EC2 Deployment Testing
- [ ] SSH to EC2
- [ ] Check running containers: `docker ps`
- [ ] Container named `fake-news-app` is running
- [ ] Check logs: `docker logs fake-news-app`
- [ ] Test app locally: `curl http://localhost/`
- [ ] Test app externally: `curl http://ec2-public-ip/`
- [ ] App responds with HTTP 200

### Health Check Testing
- [ ] Jenkins health check passes
- [ ] Application endpoint responds
- [ ] No errors in container logs

## Production Readiness

- [ ] All checks above are marked ✓
- [ ] Can build manually: `docker build -t fake-news:v1.0 .`
- [ ] Can push manually: `docker push your-username/fake-news-detection:v1.0`
- [ ] Can pull on EC2: `docker pull your-username/fake-news-detection:latest`
- [ ] Rollback plan documented
- [ ] Monitoring set up
- [ ] Logging configured
- [ ] Backup strategy in place

## Troubleshooting Quick Links

If you encounter issues, check:

| Issue | Check |
|-------|-------|
| Jenkins won't build | Check Jenkinsfile syntax, Check GitHub webhook |
| Docker build fails | Check Dockerfile, Check dependencies, Check file paths |
| Docker push fails | Check Docker Hub credentials, Check token validity |
| EC2 deployment fails | Check SSH key, Check security groups, Check Docker on EC2 |
| App not accessible | Check port mappings, Check security groups, Check container logs |

---

## Once Everything is Checked ✅

You can confidently say:

> "I understand Jenkins CI/CD pipelines, Docker containerization, GitHub webhooks, and AWS EC2 deployments. I can set up an automated deployment process from code push to production in minutes."

---

**Status:** Ready for Production Deployment 🚀

