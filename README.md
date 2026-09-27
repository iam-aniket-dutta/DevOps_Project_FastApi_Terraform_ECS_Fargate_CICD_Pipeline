# DevOps Project: ECS Fargate CI/CD Pipeline

This repository hosts a microservice project structured for containerization and automated deployment to **AWS ECS Fargate** via CI/CD.

## 📦 Directory Structure

- [`app/`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/app): Python FastAPI application with in-memory CRUD operations, interactive UI, and unit tests.
  - [`app/main.py`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/app/main.py): Application entrypoint and API routes.
  - [`app/models.py`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/app/models.py): Pydantic data validation schemas.
  - [`app/static/`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/app/static): Frontend single-page app (HTML/CSS/JS).
  - [`app/tests/`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/app/tests): Pytest suite with 14 automated tests.
  - [`app/requirements.txt`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/app/requirements.txt): Python dependencies.
  - [`app/README.md`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/app/README.md): Detailed application setup and usage guide.
- [`.github/workflows/ci-cd.yml`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/.github/workflows/ci-cd.yml): Automated CI/CD pipeline for PR validation and production deployment to AWS ECS Fargate.
- [`deploy/`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/deploy): Terraform configurations for AWS Base Infrastructure.
  - **VPC & Subnets**: Public & Private subnets across 2 AZs with IGW & NAT Gateway.
  - **Security Groups**: Public ALB ingress on port 80; ECS tasks ingress strictly from ALB only.
  - **Load Balancing**: Application Load Balancer (ALB) and IP-based Target Group (`/api/health`).
  - **Compute & Registry**: Amazon ECS Cluster (Fargate) & Amazon ECR repository with lifecycle rules.
  - [`deploy/README.md`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/deploy/README.md): Step-by-step infrastructure provisioning guide.

---

## ⚡ Quick Start

```powershell
# 1. Navigate to app directory
cd app

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Run the application
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- **Web UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Run Tests:** `pytest -v app/tests`
- **Run Lint:** `flake8 app --exclude=.venv,venv --max-line-length=127`

---

## 🚀 CI/CD Pipeline Architecture (`.github/workflows/ci-cd.yml`)

The repository features an automated GitHub Actions CI/CD workflow triggered on `pull_request` and `push` to the `main` branch.

### 1. Pull Request (PR) Pipeline
Ensures code quality, unit test coverage, and container security before merging into `main`.
```text
PR Created / Updated
       │
       ▼
 [ 1. Checkout ] ────────► actions/checkout@v4
       │
       ▼
 [ 2. Install deps ] ────► Python 3.12 with pip cache, flake8, pytest-cov
       │
       ▼
 [ 3. Lint ] ────────────► Flake8 static analysis & JS syntax validation
       │
       ▼
 [ 4. Tests & Cov ] ─────► Pytest test suite with code coverage report
       │
       ▼
 [ 5. Build Image ] ─────► Builds Docker image locally (NO PUSH to ECR)
       │
       ▼
 [ 6. Trivy Scan ] ──────► DevSecOps security vulnerability scanning (CRITICAL/HIGH)
```

### 2. Main Branch Pipeline (10-Step Automated Pipeline)
Builds, scans, deploys to AWS ECS Fargate, and runs smoke tests upon push or merge to `main`.
```text
Push / Merge to main
       │
       ▼
 1. Checkout ────────────► actions/checkout@v4
       │
       ▼
 2. Install deps/cache ──► Python 3.12 with pip cache & dependencies
       │
       ▼
 3. Lint (flake8/eslint) ► Flake8 python style & JS syntax verification
       │
       ▼
 4. Unit tests coverage ─► Pytest suite with coverage table in Step Summary
       │
       ▼
 5. Build Docker image ──► Compiles production container image
       │
       ▼
 6. Vulnerability scan ──► Aqua Security Trivy container CVE scanner (DevSecOps)
       │
       ▼
 7. Push to ECR ─────────► Pushes image with Git SHA tag and 'latest' tag
       │
       ▼
 8. Deploy to ECS ───────► Registers new Task Def revision & updates service
       │
       ▼
 9. Post-deploy smoke ───► Curls ALB `/api/health` with N retries (fails if not 200)
       │
       ▼
 10. Notify ─────────────► Publishes GitHub Step Summary & sends Slack notification
```

---

## 🔄 Rollback Workflow (`.github/workflows/rollback.yml`)

The repository includes a dedicated manual rollback workflow triggered via **GitHub Actions > "Rollback ECS Service" > Run workflow (`workflow_dispatch`)**.

### How Rollback Works:
1. **Historical Revision Preservation**: Each deployment in `ci-cd.yml` registers a distinct task definition revision containing the deployed Git SHA, keeping previous revisions intact in AWS ECS.
2. **Prior Revision Resolution**:
   - **Automatic**: If no revision number is entered, the workflow inspects the running ECS service and rolls back to `current_revision - 1`.
   - **Explicit**: Allows typing any specific historical revision number (e.g., `2`).
3. **Re-pointing Service**: Calls `aws ecs update-service --task-definition <family>:<target_revision>` and awaits service stabilization.
4. **Post-Rollback Smoke Test**: Curls the ALB `/api/health` endpoint to verify recovery.

---

## 🔑 Required GitHub Secrets & Variables

Configure secrets in your repository (**Settings > Secrets and variables > Actions > Secrets**):

| Secret / Variable | Type | Description | Default Fallback |
|---|---|---|---|
| `AWS_ACCESS_KEY_ID` | Secret | AWS IAM Access Key ID with ECR, ECS & ELB permissions | *Required* |
| `AWS_SECRET_ACCESS_KEY` | Secret | AWS IAM Secret Access Key | *Required* |
| `AWS_REGION` | Secret/Var | AWS Region where resources reside | `us-east-1` |
| `ECR_REPOSITORY` | Secret/Var | Amazon ECR repository name | `fastapi-ecs-dev-repo` |
| `ECS_CLUSTER` | Secret/Var | Amazon ECS cluster name | `fastapi-ecs-dev-cluster` |
| `ECS_SERVICE` | Secret/Var | Amazon ECS service name | `fastapi-ecs-dev-service` |
| `ECS_TASK_DEFINITION` | Secret/Var | Amazon ECS task definition family name | `fastapi-ecs-dev-task` |
| `CONTAINER_NAME` | Secret/Var | ECS container name | `fastapi-ecs-dev-container` |
| `ALB_NAME` | Secret/Var | Application Load Balancer name | `fastapi-ecs-dev-alb` |
| `ALB_DNS_NAME` | Secret/Var | Direct ALB DNS name (auto-discovered from AWS if blank) | Auto-discovered from AWS |
| `SLACK_WEBHOOK_URL` | Secret *(opt)* | Slack Incoming Webhook URL for deployment alerts | *Optional* |



