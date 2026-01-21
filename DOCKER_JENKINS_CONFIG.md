# 🔧 Docker & Jenkins Configuration Reference

## Environment Variables for Production

Add these to your Flask application or Docker container:

```python
# In app.py
import os

FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', 5000))

# Run app
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
```

## Required pip Packages (if not already in requirements.txt)

```bash
# For production-grade Flask server
pip install gunicorn
pip install python-dotenv  # For environment variables
pip install flask-limiter  # For rate limiting
```

Add to `requirements.txt`:
```
Flask==3.0.0
flask-cors==4.0.0
scikit-learn==1.3.2
nltk==3.8.1
numpy>=1.26.0
pandas==2.0.3
joblib==1.3.2
langdetect==1.0.9
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
gunicorn==21.2.0
python-dotenv==1.0.0
```

## Docker Build Arguments

The Jenkinsfile passes build arguments:

```dockerfile
ARG BUILD_DATE
ARG VERSION

LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.version=$VERSION
```

This allows tracking image build dates and versions.

## Quick Docker Commands Reference

```bash
# Build image locally
docker build -t fake-news-detection:latest .

# Run container
docker run -d \
  --name fake-news-app \
  -p 5000:5000 \
  fake-news-detection:latest

# View logs
docker logs -f fake-news-app

# Stop and remove
docker stop fake-news-app
docker rm fake-news-app

# Push to Docker Hub
docker tag fake-news-detection:latest your-username/fake-news-detection:latest
docker push your-username/fake-news-detection:latest

# Pull from Docker Hub
docker pull your-username/fake-news-detection:latest
```

## Jenkinsfile Credentials Setup

### Creating Credentials via Jenkins CLI

```bash
# SSH to Jenkins server
ssh -i jenkins-key.pem jenkins-user@jenkins-ip

# Create Docker Hub credentials
cat > /tmp/docker-creds.xml << 'EOF'
<com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
  <id>dockerhub-creds</id>
  <description>Docker Hub Credentials</description>
  <username>your-username</username>
  <password>YOUR_DOCKER_HUB_TOKEN</password>
</com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl>
EOF
```

### Or via Jenkins Web UI

1. Jenkins Dashboard → Manage Jenkins
2. → Manage Credentials
3. → System → Global Credentials
4. → Add Credentials
5. Fill in:
   - **Kind:** Username with password
   - **Username:** your-docker-username
   - **Password:** Docker Hub access token
   - **ID:** dockerhub-creds
   - **Description:** Docker Hub Credentials

## GitHub Webhook Payload Example

When you push code, GitHub sends this to Jenkins:

```json
{
  "ref": "refs/heads/main",
  "before": "abc123...",
  "after": "def456...",
  "repository": {
    "id": 12345,
    "name": "fake-news-detection",
    "url": "https://github.com/your-username/fake-news-detection"
  },
  "pusher": {
    "name": "your-username",
    "email": "your-email@example.com"
  },
  "commits": [
    {
      "id": "def456...",
      "message": "Update Dockerfile",
      "author": {
        "name": "Your Name"
      }
    }
  ]
}
```

Jenkins webhook plugin parses this and triggers the pipeline.

## Security Best Practices

### 1. SSH Key Management
```bash
# Generate secure SSH key for Jenkins
ssh-keygen -t rsa -b 4096 -f jenkins-ec2-key.pem -N ""

# Add to Jenkins
# Store in: /var/lib/jenkins/.ssh/
# Permissions: 600 (read-write for owner only)
chmod 600 /var/lib/jenkins/.ssh/jenkins-ec2-key.pem
```

### 2. Docker Registry Credentials
```groovy
// ✅ GOOD: Use Jenkins credentials
withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', ...)]) {
    sh 'docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} --password-stdin'
}

// ❌ BAD: Never hardcode credentials
// docker login -u myuser -p mypassword
```

### 3. EC2 Security Group Rules
```
Inbound Rules:
- SSH (22): Source = Jenkins server IP or 0.0.0.0/0
- HTTP (80): Source = 0.0.0.0/0
- HTTPS (443): Source = 0.0.0.0/0

Outbound Rules:
- All traffic allowed (for pulling Docker images)
```

### 4. Dockerfile Security
```dockerfile
# Run as non-root user
RUN useradd -r appuser
USER appuser

# Don't run as root
# ❌ WRONG: CMD ["python", "app.py"]
# ✅ CORRECT: Already set USER appuser before

# Use specific version tags
# ❌ WRONG: FROM python:latest
# ✅ CORRECT: FROM python:3.11-slim

# Keep image small
# Use multi-stage builds
# Remove unnecessary files after installation
```

## Monitoring & Logging

### Container Logs
```bash
# View logs
docker logs fake-news-app

# Follow logs in real-time
docker logs -f fake-news-app

# Last 100 lines
docker logs --tail 100 fake-news-app

# With timestamps
docker logs -t fake-news-app
```

### Health Check
```bash
# Check container health status
docker inspect fake-news-app | grep -A 5 '"Health"'

# Manual health check
curl -f http://localhost:5000/ && echo "Healthy" || echo "Unhealthy"
```

### System Resources
```bash
# Monitor container resources
docker stats fake-news-app

# Check image size
docker images | grep fake-news

# Clean up unused images and containers
docker system prune -a
```

## Scaling Considerations

### For Multiple Containers
```bash
# Run multiple replicas on same host
docker run -d --name fake-news-app-1 -p 5001:5000 image:tag
docker run -d --name fake-news-app-2 -p 5002:5000 image:tag
docker run -d --name fake-news-app-3 -p 5003:5000 image:tag

# Use load balancer (nginx) to distribute traffic
```

### For Kubernetes (Future)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fake-news-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fake-news-app
  template:
    metadata:
      labels:
        app: fake-news-app
    spec:
      containers:
      - name: fake-news-app
        image: your-username/fake-news-detection:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Rollback Strategy

If a deployment fails:

```bash
# On EC2, keep previous versions:
docker pull your-username/fake-news-detection:v1.0  # Previous version
docker run -d --name fake-news-app-v1 -p 80:5000 your-username/fake-news-detection:v1.0

# Or manually revert in Jenkins:
# 1. Revert code commit: git revert
# 2. Push to GitHub
# 3. Jenkins auto-builds and deploys previous version
```

## Common Issues & Solutions

### Issue: Image size too large

**Solution:** Use multi-stage builds (already in your Dockerfile)
```dockerfile
FROM python:3.11-slim as builder
# ... install dependencies ...

FROM python:3.11-slim
COPY --from=builder /opt/venv /opt/venv
# ... smaller final image
```

### Issue: Dependencies take too long to install

**Solution:** Layer Docker image correctly
```dockerfile
# Bad: Changes to code rebuild entire layer
COPY . .
RUN pip install -r requirements.txt

# Good: requirements.txt cached until changed
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### Issue: Container exits immediately

**Solution:** Check logs
```bash
docker logs container-name
```

Ensure Flask app runs on `0.0.0.0`:
```python
app.run(host='0.0.0.0', port=5000)
```

### Issue: Health check always fails

**Solution:** Verify endpoint
```dockerfile
HEALTHCHECK CMD curl -f http://localhost:5000/ || exit 1
```

Ensure your Flask app has a working root endpoint:
```python
@app.route('/')
def home():
    return jsonify({'status': 'healthy'})
```

---

## Deployment Timeline

```
t=0s   : Code pushed to GitHub
t=1s   : GitHub webhook sent to Jenkins
t=2s   : Jenkins receives webhook, starts build
t=5s   : Code cloned
t=10s  : Docker image built
t=20s  : Image tested locally
t=25s  : Image pushed to Docker Hub
t=35s  : Jenkins SSHs to EC2
t=36s  : Old container stopped
t=37s  : New image pulled
t=45s  : New container started
t=50s  : Health check passes
t=51s  : Deployment complete

Total: ~50 seconds from git push to live deployment
```

---

This is production-ready configuration! 🚀

