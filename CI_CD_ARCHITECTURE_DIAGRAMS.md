# 🎯 CI/CD Pipeline Architecture & Flow Diagrams

## Complete End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER'S LOCAL MACHINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Write Code → Test Locally → Commit → git push origin main                │
│                                                                             │
│                                                                             │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ (Code pushed)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GITHUB REPOSITORY                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Stores: app.py, Dockerfile, Jenkinsfile, requirements.txt, etc.         │
│                                                                             │
│  On Push → Sends webhook notification to Jenkins                           │
│                                                                             │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ (Webhook HTTP POST)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        JENKINS SERVER (CI/CD)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Stage 1: Checkout Code                                                    │
│  ├─ git clone https://github.com/...                                      │
│  └─ Files available for processing                                         │
│                                                                             │
│  Stage 2: Validate                                                         │
│  ├─ Check Docker available                                                │
│  ├─ Check Python files exist                                              │
│  └─ Check dependencies                                                    │
│                                                                             │
│  Stage 3: Build Docker Image                                              │
│  ├─ docker build -t image:123 .                                           │
│  ├─ Reads Dockerfile                                                       │
│  ├─ Creates layers                                                        │
│  └─ Final image ready                                                     │
│                                                                             │
│  Stage 4: Test Docker Image                                               │
│  ├─ docker run -d -p 5001:5000 image:123                                 │
│  ├─ Sleep 5 seconds                                                      │
│  ├─ curl http://localhost:5001/                                          │
│  └─ Stop test container                                                  │
│                                                                             │
│  Stage 5: Push to Docker Hub                                              │
│  ├─ docker login (using credentials)                                      │
│  ├─ docker push image:123                                                │
│  ├─ docker push image:latest                                             │
│  └─ docker logout                                                         │
│                                                                             │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ (Docker image pushed)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DOCKER HUB (Registry)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Repository: your-username/fake-news-detection                            │
│                                                                             │
│  Tags stored:                                                              │
│  ├─ your-username/fake-news-detection:123 (build number)                 │
│  └─ your-username/fake-news-detection:latest                             │
│                                                                             │
│  Image layers:                                                             │
│  ├─ Layer 1: Python 3.11-slim base image                                 │
│  ├─ Layer 2: System dependencies                                         │
│  ├─ Layer 3: Python packages                                             │
│  ├─ Layer 4: NLTK data                                                   │
│  └─ Layer 5: Application code                                            │
│                                                                             │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ (Jenkins pulls image)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS EC2 INSTANCE (Production)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Jenkins SSH Connection: ssh -i key.pem ubuntu@ec2-public-ip              │
│                                                                             │
│  On EC2:                                                                   │
│  ├─ Stop old container (fake-news-app)                                   │
│  ├─ docker pull your-username/fake-news-detection:latest                 │
│  └─ docker run -d \                                                      │
│      --name fake-news-app \                                              │
│      --restart always \                                                  │
│      -p 80:5000 \                                                        │
│      your-username/fake-news-detection:latest                            │
│                                                                             │
│  Container Details:                                                        │
│  ├─ Name: fake-news-app                                                 │
│  ├─ Status: Running                                                      │
│  ├─ Port: 80:5000 (HTTP traffic → Flask on 5000)                        │
│  ├─ Restart: Always (auto-restart if crashes)                           │
│  └─ Health: Monitored by health check                                   │
│                                                                             │
│  Health Check:                                                            │
│  ├─ Every 30 seconds                                                    │
│  ├─ curl http://localhost:5000/                                        │
│  ├─ Expected: HTTP 200 (healthy)                                       │
│  └─ If unhealthy 3 times: Container restarts                           │
│                                                                             │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ (Application running)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LIVE APPLICATION                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Accessible at: http://ec2-public-ip/                                     │
│  or: http://your-domain.com/                                              │
│                                                                             │
│  Flask Routes:                                                             │
│  ├─ GET  /           → Home page                                         │
│  ├─ POST /predict    → Analyze news                                      │
│  ├─ POST /analyze-url → Extract & analyze URL                            │
│  └─ GET  /health     → Health check                                      │
│                                                                             │
│  Users/Clients:                                                            │
│  ├─ Web browsers                                                          │
│  ├─ Mobile apps                                                           │
│  ├─ External APIs                                                         │
│  └─ Jenkins health checks                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Deployment Time: ~50 seconds from git push to live application ⚡
```

---

## Jenkins Pipeline Stages

```
BUILD PIPELINE EXECUTION TIMELINE

Stage 1: Checkout Code
├─ Duration: 5-10 seconds
├─ Action: git clone from GitHub
└─ Status: Code available on Jenkins server

  ▼

Stage 2: Validate
├─ Duration: 2-5 seconds
├─ Action: Verify Docker, Python, files exist
└─ Status: Environment ready

  ▼

Stage 3: Build Docker Image
├─ Duration: 30-60 seconds
├─ Action: Read Dockerfile, build image
├─ Steps:
│  ├─ Pull base image (python:3.11-slim)
│  ├─ Install system dependencies
│  ├─ Install Python packages
│  ├─ Download NLTK data
│  ├─ Copy application code
│  └─ Tag image
└─ Status: Image ready

  ▼

Stage 4: Test Docker Image
├─ Duration: 10-20 seconds
├─ Action: Run container, verify it works
├─ Steps:
│  ├─ Start container in background
│  ├─ Wait 5 seconds for app startup
│  ├─ curl http://localhost:5001/
│  └─ Stop test container
└─ Status: Image verified

  ▼

Stage 5: Push to Docker Hub
├─ Duration: 30-60 seconds
├─ Action: Upload image to registry
├─ Steps:
│  ├─ Login to Docker Hub
│  ├─ Push image:123 (build number)
│  ├─ Push image:latest
│  └─ Logout
└─ Status: Image in Docker Hub

  ▼

Stage 6: Deploy to EC2
├─ Duration: 10-20 seconds
├─ Action: SSH to EC2, stop old, run new
├─ Steps:
│  ├─ SSH connection established
│  ├─ Stop old container
│  ├─ Pull new image
│  ├─ Start new container
│  └─ Verify container running
└─ Status: New container running

  ▼

Stage 7: Health Check
├─ Duration: 5-10 seconds
├─ Action: Verify app is responding
├─ Steps:
│  ├─ Wait 10 seconds for startup
│  ├─ curl http://ec2-public-ip/
│  └─ Check HTTP 200 response
└─ Status: App is healthy ✅

TOTAL TIME: 45-60 seconds
```

---

## Docker Image Structure

```
Docker Image: your-username/fake-news-detection:123

┌─────────────────────────────────────────┐
│ Layer 7: Application Code               │
│ COPY . /app                             │
│ Size: ~500MB                            │
├─────────────────────────────────────────┤
│ Layer 6: NLTK Data                      │
│ RUN python -m nltk.downloader ...      │
│ Size: ~500MB                            │
├─────────────────────────────────────────┤
│ Layer 5: Python Packages                │
│ RUN pip install -r requirements.txt     │
│ Size: ~200MB                            │
├─────────────────────────────────────────┤
│ Layer 4: System Dependencies            │
│ RUN apt-get install gcc                │
│ Size: ~50MB                             │
├─────────────────────────────────────────┤
│ Layer 3: Environment Setup              │
│ ENV PYTHONUNBUFFERED=1                  │
│ Size: ~1KB                              │
├─────────────────────────────────────────┤
│ Layer 2: Working Directory              │
│ WORKDIR /app                            │
│ Size: ~1KB                              │
├─────────────────────────────────────────┤
│ Layer 1: Base Image (Python 3.11-slim)  │
│ FROM python:3.11-slim                   │
│ Size: ~100MB                            │
└─────────────────────────────────────────┘

Total Image Size: ~1.3GB
Multi-stage build reduces to: ~700MB

When Container Starts:
├─ Docker loads all layers
├─ Creates writable container layer
├─ Sets up networking (port 80→5000)
├─ Starts Flask application
└─ Application listening on port 5000
```

---

## Network Communication

```
┌──────────────┐
│   Developer  │
│   Machine    │
└──────┬───────┘
       │
       │ git push origin main
       │ (HTTPS)
       │
       ▼
┌──────────────────┐
│   GitHub.com     │
│   Webhook Sent   │
└──────┬───────────┘
       │
       │ POST http://jenkins-ip:8080/github-webhook/
       │ (HTTPS or HTTP)
       │
       ▼
┌────────────────────┐
│   Jenkins Server   │
│   (TCP:8080)       │
└──────┬─────────────┘
       │
       │ git clone
       │ (HTTPS)
       │
       ▼
┌────────────────────┐
│   GitHub (again)   │
│   Code Download    │
└──────┬─────────────┘
       │
       │ docker push
       │ (HTTPS)
       │
       ▼
┌────────────────────┐
│   Docker Hub       │
│   Image Stored     │
└──────┬─────────────┘
       │
       │ SSH Connection
       │ (TCP:22)
       │
       ▼
┌────────────────────┐
│   EC2 Instance     │
│                    │
│ docker pull        │
│ ↓                  │
│ docker run         │
│ ↓                  │
│ Flask App Running  │
│ (TCP:5000)         │
└──────┬─────────────┘
       │
       │ HTTP/HTTPS
       │ (TCP:80)
       │
       ▼
┌────────────────────┐
│   User Browsers    │
│   Mobile Apps      │
│   API Clients      │
└────────────────────┘
```

---

## GitHub Webhook Payload

```json
{
  "ref": "refs/heads/main",
  "before": "abc123def456",
  "after": "def456abc123",
  "repository": {
    "id": 12345678,
    "name": "fake-news-detection",
    "full_name": "your-username/fake-news-detection",
    "owner": {
      "name": "your-username",
      "email": "your-email@example.com"
    },
    "html_url": "https://github.com/your-username/fake-news-detection",
    "clone_url": "https://github.com/your-username/fake-news-detection.git"
  },
  "pusher": {
    "name": "your-username",
    "email": "your-email@example.com"
  },
  "commits": [
    {
      "id": "def456abc123",
      "message": "Update Jenkinsfile with production config",
      "timestamp": "2026-01-05T10:30:00Z",
      "author": {
        "name": "Your Name",
        "email": "your-email@example.com"
      }
    }
  ]
}

Jenkins receives this JSON and:
├─ Extracts repository URL
├─ Extracts branch (main)
├─ Triggers pipeline
└─ Starts build process
```

---

## EC2 Container Networking

```
EC2 Instance (Public IP: 54.123.45.678)
┌────────────────────────────────────────────────────┐
│                                                    │
│  Security Group (Firewall Rules)                  │
│  ├─ Inbound SSH: :22 (from Jenkins IP)           │
│  ├─ Inbound HTTP: :80 (from 0.0.0.0/0)          │
│  └─ Outbound: All allowed (for docker pull)      │
│                                                    │
│  Docker Daemon (listens on unix socket)           │
│  ├─ Can access Docker Hub for pulls              │
│  └─ Manages containers                            │
│                                                    │
│  Container: fake-news-app                        │
│  ├─ IP: 172.17.0.2 (internal Docker network)    │
│  ├─ Port inside: 5000 (Flask app listening)      │
│  ├─ Port mapping: 80 → 5000 (port forwarding)    │
│  ├─ Name: fake-news-app                          │
│  ├─ Status: running                              │
│  └─ Health: healthy                              │
│                                                    │
│  Network Path:                                     │
│  ┌─────────────────────────────────────────┐     │
│  │ User Request: http://54.123.45.678/    │     │
│  │ ↓                                        │     │
│  │ Incoming port 80 (HTTP)                 │     │
│  │ ↓                                        │     │
│  │ Docker port mapping 80 → 5000           │     │
│  │ ↓                                        │     │
│  │ Container receives on localhost:5000    │     │
│  │ ↓                                        │     │
│  │ Flask app handles request               │     │
│  │ ↓                                        │     │
│  │ Response sent back through 5000 → 80    │     │
│  │ ↓                                        │     │
│  │ User receives HTTP response             │     │
│  └─────────────────────────────────────────┘     │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Deployment Comparison

### Before (Without CI/CD)
```
Developer has code changes
    ↓
Must SSH to server manually
    ↓
Manually download code
    ↓
Manually stop application
    ↓
Manually install dependencies
    ↓
Manually start application
    ↓
Hope nothing breaks

⏱️ Time: 30-60 minutes
❌ Error-prone (manual steps)
❌ Not reproducible
❌ Difficult to rollback
```

### After (With CI/CD)
```
Developer pushes code
    ↓
Automatic build
    ↓
Automatic testing
    ↓
Automatic deployment
    ↓
Application live

⏱️ Time: 50 seconds
✅ Consistent
✅ Reproducible
✅ Easy to rollback
✅ Auditable (logs)
```

---

## Jenkins Stage Status Indicators

```
✅ SUCCESS: Stage completed without errors
   Example: Stage 'Checkout Code' completed successfully
   → Pipeline continues to next stage

⚠️ WARNING: Stage completed but with issues
   Example: Health check slow to respond
   → Pipeline may continue (depends on configuration)

❌ FAILURE: Stage failed, pipeline stops
   Example: Docker build failed
   → Pipeline stops, old version stays running
   → Error logged for debugging
   → Developer notified (email/Slack)
   → No deployment occurs

⏳ RUNNING: Stage currently executing
   Example: Building Docker image...
   → Jenkins shows real-time console output
   → User can watch progress

⊘ SKIPPED: Stage skipped (conditional)
   Example: Deploy only on main branch
   → Stage skipped on feature branches
   → Pipeline continues
```

---

## Error Handling & Rollback

```
Deployment Failure Scenario:
│
├─ Build fails
│  └─ Old application still running ✓
│     (No downtime)
│
├─ Docker push fails
│  └─ Old application still running ✓
│     (No downtime)
│
├─ EC2 deployment fails
│  └─ Old application still running ✓
│     (New container not started)
│
└─ Health check fails
   └─ Old application still running ✓
      (New container detected as unhealthy)

Rollback Process:
1. Revert code commit (git revert)
2. Push to GitHub
3. Webhook triggers new build
4. Jenkins builds, tests, deploys
5. Previous working version now deployed
   (Total time: ~50 seconds)

OR Manual Rollback:

SSH to EC2:
├─ docker stop fake-news-app
├─ docker pull your-username/fake-news-detection:v1.0
├─ docker run -d --name fake-news-app ... :v1.0
└─ curl http://localhost/ (verify)

Application restored to previous version ✓
```

---

## Key Advantages of This Setup

```
┌─────────────────────────────────────┐
│    WHAT YOU GET WITH CI/CD          │
├─────────────────────────────────────┤
│                                     │
│ 1. SPEED                            │
│    Code to production: 50 seconds   │
│                                     │
│ 2. RELIABILITY                      │
│    Same process every time          │
│    Automated testing                │
│                                     │
│ 3. SAFETY                           │
│    Old version always running       │
│    Easy rollback                    │
│                                     │
│ 4. TRANSPARENCY                     │
│    Full build logs                  │
│    Audit trail                      │
│                                     │
│ 5. SCALABILITY                      │
│    Deploy to multiple servers       │
│    Auto-scaling ready               │
│                                     │
│ 6. QUALITY                          │
│    Automated testing                │
│    Consistency checks               │
│                                     │
│ 7. MONITORING                       │
│    Health checks                    │
│    Logs available                   │
│                                     │
│ 8. FLEXIBILITY                      │
│    Easy to add more stages          │
│    Extensible                       │
│                                     │
└─────────────────────────────────────┘
```

---

This is your complete CI/CD architecture! 🚀

