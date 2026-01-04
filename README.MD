

# 🌩 Helm Storm – Secure Full-Stack Authentication System

## 1. Project Overview

**Helm Storm** is a full-stack authentication system that provides secure **Sign-up** and **Sign-in** functionality.
The project is built using a **DevSecOps** and **Cloud-Native** approach, combining application development, automated security checks, and Kubernetes deployment.

The goal of this project is to demonstrate how a modern authentication system can be designed, deployed, scaled, and secured using industry-standard tools.



## 2. Key Features

* 🔐 Secure Sign-up / Sign-in flow
* ⚡ Redis caching for fast authentication
* 🗄 PostgreSQL with connection pooling
* 📦 Dockerized backend and frontend
* ☸ Kubernetes deployment using Helm
* 📈 Horizontal Pod Autoscaling (CPU & Memory)
* 🔎 SonarQube code quality & security scanning
* 🔏 Container image verification using Cosign



## 3. Technology Stack

| Layer         | Technology                |
| ------------- | ------------------------- |
| Backend       | Python (Flask)            |
| Frontend      | HTML / JavaScript (Nginx) |
| Database      | PostgreSQL                |
| Cache         | Redis                     |
| CI/CD         | GitLab CI                 |
| Security      | SonarQube, Cosign         |
| Orchestration | Kubernetes + Helm         |
| Scaling       | HPA (CPU & Memory)        |



## 4. Project Architecture

<img src="project architecture.jpg" alt="Description" width="1000">

## 5. Directory Structure & File Description

```text
helm-storm/
├── app/
│   ├── backend/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/
│       ├── index.html
│       └── Dockerfile
│
├── helm/
│   ├── helm-backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       └── service.yaml
│   │
│   ├── helm-db/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── statefulset.yaml
│   │       ├── pvc.yaml
│   │       └── secret.yaml
│   │
│   ├── helm-frontend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── hpa.yaml
│   │
│   └── helm-redis/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── statefulset.yaml
│           └── networkpolicy.yaml
│
├── cosign.pub
├── install.yaml
├── test_suite.py
├── docker-compose-sonar.yml
└── README.md


---



### Root Directory

| Path                       | Description                           |
| -------------------------- | ------------------------------------- |
| `/app`                     | Application source code               |
| `/helm`                    | Helm charts for Kubernetes deployment |
| `.gitlab-ci.yml`           | CI/CD pipeline configuration          |
| `docker-compose-sonar.yml` | Local SonarQube setup                 |
| `test_suite.py`            | Automated quality & security tests    |
| `security-policy.yaml`     | Kubernetes Pod Security rules         |
| `cosign.pub`               | Public key for image verification     |



### Application Layer (`/app`)

#### Backend (`/app/backend`)

| File               | Function                          |
| ------------------ | --------------------------------- |
| `app.py`           | Flask API handling authentication |
| `Dockerfile`       | Backend container image           |
| `requirements.txt` | Python dependencies               |

**Backend Responsibilities**

* Validate input data
* Check Redis cache first
* Query PostgreSQL securely
* Register new users
* Manage database connections using pooling



#### Frontend (`/app/frontend`)

| File         | Function                         |
| ------------ | -------------------------------- |
| `index.html` | Sign-up / Sign-in user interface |
| `Dockerfile` | Nginx container for frontend     |



### Infrastructure Layer (`/helm`)

| File                  | Function                          |
| --------------------- | --------------------------------- |
| `values.yaml`         | Global deployment configuration   |
| `deployment.yaml`     | Backend deployment definition     |
| `hpa.yaml`            | Horizontal Pod Autoscaler         |
| `namespace.yaml`      | Dedicated Kubernetes namespace    |
| `resource-quota.yaml` | Resource limits for the namespace |



## 6. Backend Logic Overview

The backend exposes a single authentication endpoint:

### `POST /check-user`

**Flow**

1. Receive username and phone number
2. Check Redis cache
3. If cache miss → query PostgreSQL
4. If user exists → return success
5. If user does not exist → create user

**Security Measures**

* Parameterized SQL queries (prevents SQL Injection)
* Input validation
* Connection pooling
* Centralized logging



## 7. Helm Configuration Overview

### Scaling

* Minimum replicas: **2**
* Maximum replicas: **10**
* CPU threshold: **60%**
* Memory threshold: **80%**

### Resource Limits (per pod)

* Requests: `100m CPU / 128Mi RAM`
* Limits: `200m CPU / 256Mi RAM`



## 8. Getting Started (How to Run the Project)

### Prerequisites

* Docker & Docker Compose
* Kubernetes Cluster (Minikube / EKS / AKS)
* Helm CLI
* Python 3.9+
* Metrics Server (for HPA)



### Step 1: Clone the Repository

```bash
git clone https://github.com/nabilaebrahim/project1.git
cd project1
```



### Step 2: Run Quality & Security Checks

```bash
docker-compose -f docker-compose-sonar.yml up -d
python test_suite.py
```



### Step 3: Deploy Using Helm

```bash
helm install helm-storm ./helm/helm-backend
```



### Step 4: Verify Deployment

```bash
kubectl get pods -n backend-ns
kubectl get hpa -n backend-ns
```



## 9. Development Guide

### Adding New Features

1. Create a new branch

```bash
git checkout -b feature/new-feature
```

2. Update backend logic in `app.py`
3. Update `requirements.txt` if needed
4. Run `test_suite.py`
5. Push changes and ensure CI pipeline passes



### Modifying Infrastructure

* Scaling → edit `values.yaml`
* Database schema → update `deployment.yaml` init container
* Security rules → update `security-policy.yaml`



## 10. CI/CD & Security

* Every push triggers GitLab CI
* SonarQube scans for bugs and vulnerabilities
* Pipeline fails if Quality Gate is not **GREEN**
* Images are verified using **Cosign** before deployment



## 11. Team

**Project Team:** Helm Storm 🌩
Built with a focus on **security, scalability, and maintainability**.




