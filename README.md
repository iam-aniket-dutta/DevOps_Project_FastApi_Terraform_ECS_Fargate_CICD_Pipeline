# 🚀 DevOps Project: FastAPI Microservice on AWS ECS Fargate with Automated CI/CD & DevSecOps

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github-actions)](.github/workflows/ci-cd.yml)
[![AWS ECS Fargate](https://img.shields.io/badge/AWS-ECS%20Fargate-FF9900?logo=amazon-aws)](https://aws.amazon.com/fargate/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform%20v1.5+-7B42BC?logo=terraform)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Test Coverage](https://img.shields.io/badge/Coverage-99%25-success)](app/tests/)
[![Security](https://img.shields.io/badge/Security-Trivy%20DevSecOps-0052CC?logo=aquasecurity)](https://trivy.dev/)

An enterprise-ready, beginner-to-advanced DevOps project demonstrating how to build, containerize, provision, test, scan, and deploy a **FastAPI** web application with an interactive dashboard onto **AWS ECS Fargate (Serverless Containers)** using **Terraform (Infrastructure as Code)** and **GitHub Actions (10-Step DevSecOps CI/CD Pipeline)** with zero-downtime rolling updates, automated post-deploy smoke tests, and one-click rollback capabilities.

---

## 📑 Table of Contents

- [🏛️ System Architecture](#️-system-architecture)
- [📦 Repository Structure](#-repository-structure)
- [💻 Application Overview (`app/`)](#-application-overview-app)
- [🏗️ Infrastructure as Code with Terraform (`deploy/`)](#️-infrastructure-as-code-with-terraform-deploy)
  - [Networking & VPC Layout](#1-networking--vpc-layout)
  - [Security Group Architecture](#2-security-group-architecture)
  - [Application Load Balancer & Health Checks](#3-application-load-balancer--health-checks)
  - [Amazon ECR & Lifecycle Rules](#4-amazon-ecr--lifecycle-rules)
  - [ECS Fargate Cluster & High Availability](#5-ecs-fargate-cluster--high-availability)
  - [How to Provision Infrastructure](#6-how-to-provision-infrastructure)
- [🔁 CI/CD Pipeline Architecture (`.github/workflows/`)](#-cicd-pipeline-architecture-githubworkflows)
  - [10-Step Main Deployment Pipeline (`ci-cd.yml`)](#1-10-step-main-deployment-pipeline-ci-cdyml)
  - [Pull Request (PR) Validation Pipeline](#2-pull-request-pr-validation-pipeline)
  - [Manual Rollback Workflow (`rollback.yml`)](#3-manual-rollback-workflow-rollbackyml)
- [🔑 GitHub Secrets & Configuration](#-github-secrets--configuration)
- [⚡ Quick Start & Local Development](#-quick-start--local-development)
  - [Running the Application Locally](#1-running-the-application-locally)
  - [Running Tests & Code Coverage](#2-running-tests--code-coverage)
  - [Running Flake8 Linter](#3-running-flake8-linter)
  - [Running with Docker](#4-running-with-docker)
- [🛡️ DevSecOps & Security Best Practices](#️-devsecops--security-best-practices)
- [🧹 Infrastructure Teardown](#-infrastructure-teardown)

---

## 🏛️ System Architecture

```text
                                       Internet
                                          │
                                          ▼
                            ┌───────────────────────────┐
                            │  Internet Gateway (IGW)   │
                            └─────────────┬─────────────┘
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
        ┌─────────────────────────┐               ┌─────────────────────────┐
        │ Public Subnet (AZ-1)    │               │ Public Subnet (AZ-2)    │
        │  - NAT Gateway (EIP)    │               │                         │
        │  - ALB Listener (80) ───┼───────────────┼──> ALB Listener (80)    │
        └────────────┬────────────┘               └────────────┬────────────┘
                     │ (Forward to TG)                         │ (Forward to TG)
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                          ┌───────────────────────────────┐
                          │    ALB Target Group (Port     │
                          │     8000, /api/health)        │
                          └───────────────┬───────────────┘
                                          │ Ingress ONLY from ALB Security Group
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
        ┌─────────────────────────┐               ┌─────────────────────────┐
        │ Private Subnet (AZ-1)   │               │ Private Subnet (AZ-2)   │
        │                         │               │                         │
        │  ECS Task (Port 8000)   │               │  ECS Task (Port 8000)   │
        │  (Outbound via NAT GW)  │               │  (Outbound via NAT GW)  │
        └─────────────────────────┘               └─────────────────────────┘
                     │                                         │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ Amazon ECR (Private Image Registry)   │
                      │ AWS CloudWatch Logs (/ecs/fastapi)    │
                      └───────────────────────────────────────┘
```

---

## 📦 Repository Structure

```text
├── .github/
│   └── workflows/
│       ├── ci-cd.yml                # 10-Step automated CI/CD pipeline (Lint, Test, Trivy, ECR, ECS, Smoke Test, Slack)
│       └── rollback.yml             # One-click manual rollback workflow to re-point ECS to prior revision
├── app/
│   ├── .dockerignore                # Optimizes Docker build context
│   ├── .gitignore                   # Ignores Python caches and virtual environments
│   ├── Dockerfile                   # Multi-stage Docker build with non-root security (appuser:10001)
│   ├── README.md                    # In-depth application documentation & API specification
│   ├── main.py                      # FastAPI application entrypoint, REST endpoints & static file serving
│   ├── models.py                    # Pydantic data schemas & request validation
│   ├── requirements.txt             # Application & testing dependencies (FastAPI, Pytest, Pytest-cov, etc.)
│   ├── static/                      # Frontend single-page application
│   │   ├── app.js                   # Interactive client-side JavaScript (CRUD operations, health polling)
│   │   ├── index.html               # Semantic HTML5 UI layout
│   │   └── style.css                # Custom CSS styling with dark mode and responsive design
│   └── tests/
│       ├── __init__.py              # Python test package marker
│       └── test_main.py             # 14 Pytest unit tests (isolated in-memory store baseline)
├── deploy/                          # Production-ready Terraform infrastructure
│   ├── .gitignore                   # Ignores Terraform local state and variable overrides
│   ├── .terraform.lock.hcl          # Provider version locking
│   ├── README.md                    # Step-by-step infrastructure provisioning & teardown guide
│   ├── alb.tf                       # Application Load Balancer, Listener (80), and Target Group
│   ├── ecr.tf                       # Amazon ECR repository with scan-on-push & lifecycle cleanup policy
│   ├── ecs.tf                       # ECS Cluster, Fargate Capacity Providers, IAM Roles, Task Def & Service
│   ├── main.tf                      # AWS provider configuration & Availability Zone data lookups
│   ├── outputs.tf                   # Terraform output values (ALB DNS, ECR URL, Cluster & Service names)
│   ├── security_groups.tf           # Least-privilege ALB and ECS tasks security group rules
│   ├── terraform.tfvars.example     # Customizable environment variable defaults template
│   ├── variables.tf                 # Terraform input variable definitions with validations
│   ├── versions.tf                  # Minimum Terraform and AWS provider versions
│   └── vpc.tf                       # High Availability VPC (2 Public Subnets, 2 Private Subnets, IGW, NAT GW)
└── README.md                        # Master repository documentation (Workflows, IaC, CI/CD, DevSecOps)
```

---

## 💻 Application Overview (`app/`)

The application is a lightweight, asynchronous **FastAPI** service featuring an interactive frontend dashboard and clean REST APIs:

- **REST API Endpoints:**
  - `GET /` — Serves the frontend single-page application dashboard.
  - `GET /api/health` — Container & load balancer health check returning status, timestamp, and item count.
  - `GET /api/items` — Lists all items with query parameters for category, status, and search filtering.
  - `GET /api/items/{id}` — Retrieves item details by ID.
  - `POST /api/items` — Creates a new item with validation (HTTP 201 Created).
  - `PUT /api/items/{id}` — Full update of an existing item.
  - `PATCH /api/items/{id}` — Partial update (e.g., status transition).
  - `DELETE /api/items/{id}` — Removes an item.
  - `GET /docs` & `GET /redoc` — Auto-generated OpenAPI / Swagger UI interactive documentation.
- **In-Memory Store:** Uses thread-safe Python data structures seeded with sample tasks. Tests automatically run against an isolated store fixture.
- **Frontend Dashboard:** Built with vanilla HTML/CSS/JavaScript with responsive grid cards, modal dialogs, status badges, toast notifications, and live `/api/health` polling.

---

## 🏗️ Infrastructure as Code with Terraform (`deploy/`)

All cloud infrastructure is provisioned declaratively in AWS using Terraform.

### 1. Networking & VPC Layout
- **CIDR Block:** `10.0.0.0/16` with DNS hostnames and resolution enabled.
- **Availability Zones:** 2 Availability Zones dynamically discovered in the active region (e.g. `us-east-1a` and `us-east-1b`).
- **Subnets:**
  - `Public Subnet 1` (`10.0.1.0/24`) & `Public Subnet 2` (`10.0.2.0/24`) — Host the public ALB and NAT Gateway.
  - `Private Subnet 1` (`10.0.11.0/24`) & `Private Subnet 2` (`10.0.12.0/24`) — Host the private ECS Fargate tasks.
- **Gateways:**
  - **Internet Gateway (IGW)** routes public subnet traffic directly to the internet.
  - **NAT Gateway (with Elastic IP)** provisioned in Public Subnet 1 allows ECS tasks in private subnets to pull container images from ECR and send CloudWatch logs without exposing tasks to incoming internet traffic.

### 2. Security Group Architecture
- **ALB Security Group (`aws_security_group.alb`):**
  - **Ingress:** Port `80` (HTTP) open to `0.0.0.0/0` (public access).
  - **Egress:** All outbound traffic allowed to forward requests to private ECS tasks.
- **ECS Tasks Security Group (`aws_security_group.ecs_tasks`):**
  - **Ingress:** Port `8000` **STRICTLY restricted to `aws_security_group.alb.id` only**. Direct ingress from the public internet is completely blocked.
  - **Egress:** All outbound traffic allowed (for NAT Gateway outbound communication).

### 3. Application Load Balancer & Health Checks
- **ALB (`aws_lb.main`):** Public-facing Application Load Balancer distributed across both public subnets.
- **Target Group (`aws_lb_target_group.app`):**
  - Target type: `ip` (required for Fargate `awsvpc` network mode).
  - Port: `8000`.
  - Health check path: `/api/health`.
  - Interval: `30s`, Timeout: `5s`, Healthy Threshold: `2`, Unhealthy Threshold: `3`.
  - Deregistration delay: `30s` for fast connection draining during rolling updates.
- **Listener (`aws_lb_listener.http`):** Listens on port `80` and forwards traffic to the target group.

### 4. Amazon ECR & Lifecycle Rules
- **Repository (`aws_ecr_repository.app`):**
  - Tag mutability: `MUTABLE`.
  - Image vulnerability scanning enabled on push (`scan_on_push = true`).
  - Server-Side Encryption enabled using `AES256`.
- **Lifecycle Policy (`aws_ecr_lifecycle_policy.app`):**
  - Rule 1: Automatically expires untagged Docker images older than 7 days.
  - Rule 2: Retains only the last 10 tagged images, preventing unnecessary storage costs.

### 5. ECS Fargate Cluster & High Availability
- **ECS Cluster (`aws_ecs_cluster.main`):** Managed Fargate cluster with **Container Insights** enabled for CPU/Memory CloudWatch metrics.
- **Capacity Providers (`aws_ecs_cluster_capacity_providers.main`):** Configured with `FARGATE` (base: 1, weight: 100) and `FARGATE_SPOT`.
- **IAM Roles:**
  - **Execution Role (`aws_iam_role.ecs_execution_role`):** Grants the ECS agent permissions to authenticate with ECR, pull images, and stream logs to CloudWatch (`/ecs/fastapi-ecs-dev`).
  - **Task Role (`aws_iam_role.ecs_task_role`):** Least-privilege role granted to the running container itself.
- **Task Definition (`aws_ecs_task_definition.app`):**
  - Network mode: `awsvpc`.
  - CPU: `256` (0.25 vCPU), Memory: `512` (0.5 GB).
  - Container runs non-root on port 8000 with CloudWatch `awslogs` driver and container health check.
- **ECS Service (`aws_ecs_service.app`):**
  - Desired task count: `desired_count = 2` across 2 AZs for High Availability (HA).
  - Zero-downtime rolling update strategy:
    - `deployment_minimum_healthy_percent = 100` (at least 2 healthy tasks always running).
    - `deployment_maximum_percent = 200` (up to 4 tasks running during rolling rollout).

### 6. How to Provision Infrastructure

```bash
# 1. Navigate to deploy directory
cd deploy

# 2. Initialize Terraform providers and state backend
terraform init

# 3. Create and review custom parameters
cp terraform.tfvars.example terraform.tfvars
# (Optional: customize aws_region, project_name, etc.)

# 4. Review the execution plan
terraform plan

# 5. Apply and provision resources
terraform apply -auto-approve
```

---

## 🔁 CI/CD Pipeline Architecture (`.github/workflows/`)

The repository includes two GitHub Actions workflows:
1. [`.github/workflows/ci-cd.yml`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/.github/workflows/ci-cd.yml) — Automated 10-step DevSecOps CI/CD pipeline.
2. [`.github/workflows/rollback.yml`](file:///c:/STUDY/DevOps/DevOps_Project_ECS-Fargate-CICD-Pipeline/.github/workflows/rollback.yml) — Dedicated one-click manual rollback workflow.

---

### 1. 10-Step Main Deployment Pipeline (`ci-cd.yml`)

Triggers automatically on **`push` to `main`** and **`pull_request` targeting `main`**.

```text
Push / Merge to main
       │
       ▼
 1. Checkout ────────────► actions/checkout@v4 fetches repository source code
       │
       ▼
 2. Install deps/cache ──► Sets up Python 3.12, enables pip caching, upgrades pip & installs requirements
       │
       ▼
 3. Lint (flake8/eslint) ► Runs Flake8 syntax & style checks + Node.js JavaScript syntax validation
       │
       ▼
 4. Unit tests coverage ─► Executes Pytest suite with pytest-cov (generates terminal report & step summary)
       │
       ▼
 5. Build Docker image ──► Compiles production multi-stage container image locally
       │
       ▼
 6. Vulnerability scan ──► Scans image with Aqua Security Trivy (DevSecOps check for CRITICAL/HIGH CVEs)
       │
       ▼
 7. Push to ECR ─────────► Authenticates to AWS ECR, tags with Git SHA + 'latest', and pushes both tags
       │
       ▼
 8. Deploy to ECS ───────► Downloads active task def, renders new image, registers new revision & updates service
       │
       ▼
 9. Post-deploy smoke ───► Curls ALB '/api/health' with 12 retries (10s intervals); FAILS pipeline if not HTTP 200
       │
       ▼
 10. Notify ─────────────► Publishes detailed markdown table to GitHub Step Summary & sends Slack card alert
```

#### Detailed Breakdown of the 10 Steps:

| Step # | Name | Tool / Action | Description |
|---|---|---|---|
| **1** | **Checkout** | `actions/checkout@v4` | Fetches the full repository workspace. |
| **2** | **Install deps/cache** | `actions/setup-python@v5` | Configures Python 3.12, leverages pip caching, and installs application dependencies (`app/requirements.txt`) plus dev tools (`flake8`, `pytest-cov`). |
| **3** | **Lint** | `flake8` & `node --check` | Enforces PEP8 standards on all Python code (max length 127) and performs syntax validation on `app/static/app.js`. |
| **4** | **Unit tests coverage** | `pytest` + `pytest-cov` | Runs 14 automated tests, verifies 99% statement coverage, and appends a visual coverage table to `$GITHUB_STEP_SUMMARY`. |
| **5** | **Build Docker image** | `docker build` | Builds the unprivileged container using the multi-stage `Dockerfile`. |
| **6** | **Vulnerability scan** | `aquasecurity/trivy-action` | DevSecOps security gate scanning OS packages and Python packages for vulnerabilities (`CRITICAL,HIGH`) before publishing. |
| **7** | **Push to ECR** | `aws-actions/amazon-ecr-login@v2` | Tags the verified image with the unique commit **Git SHA** (`${{ github.sha }}`) and **`latest`**, pushing both to Amazon ECR. |
| **8** | **Deploy to ECS** | `aws-actions/amazon-ecs-deploy-task-definition@v2` | Records previous revision ARN, registers a new revision for the task definition family, updates the ECS service, and awaits rolling deployment stabilization. **Preserves previous revisions in AWS ECS for rollback**. |
| **9** | **Post-deploy smoke test** | `curl` (Automated Shell Script) | Curls `http://${ALB_DNS_NAME}/api/health` post-deploy with up to 12 retries (10s intervals = 2 minutes). Validates `200 OK` and fails the pipeline if unreached. |
| **10** | **Notify** | `$GITHUB_STEP_SUMMARY` & Slack | Runs on `if: always()` to render a comprehensive deployment dashboard in GitHub Actions and send an alert card to Slack (if `SLACK_WEBHOOK_URL` is set). |

---

### 2. Pull Request (PR) Validation Pipeline

When a developer opens or updates a Pull Request targeting `main`:
1. **Runs Steps 1 to 4**: Checkout, dependency installation with caching, Flake8 linting, and Pytest coverage report.
2. **Runs Step 5**: Compiles the Docker image locally to verify the Dockerfile builds without errors.
3. **Runs Step 6**: Runs Trivy vulnerability scanner on the PR container.
4. **Registry Push and Deployments are SKIPPED**: PRs are validated for quality and security without publishing images or affecting production infrastructure.

---

### 3. Manual Rollback Workflow (`rollback.yml`)

When an issue is identified in production, operators can trigger an instant rollback without touching code or redeploying previous commits.

#### Triggering Rollback:
1. Navigate to **GitHub Actions > "Rollback ECS Service"**.
2. Click **"Run workflow"** (`workflow_dispatch`).
3. *(Optional)* Enter a specific revision number (e.g., `2`), or leave blank to automatically rollback to `current_revision - 1`.
4. Click **Run workflow**.

#### How the Rollback Operates:
1. Queries the active ECS service to determine the current running revision.
2. Resolves the target revision (`current - 1` or explicit user input) and verifies its existence in AWS ECS.
3. Calls `aws ecs update-service --cluster <cluster> --service <service> --task-definition <family>:<target_revision>`.
4. Waits for the ECS service to reach a steady state (`aws ecs wait services-stable`).
5. Executes an automated post-rollback smoke test against the ALB `/api/health` endpoint to confirm recovery.

---

## 🔑 GitHub Secrets & Configuration

To enable automated AWS deployments and Slack notifications, configure the following under **Repository Settings > Secrets and variables > Actions**:

| Secret / Variable | Type | Description | Default Fallback |
|---|---|---|---|
| `AWS_ACCESS_KEY_ID` | Secret | AWS IAM Access Key ID with ECR, ECS & ELB permissions | *Required for AWS* |
| `AWS_SECRET_ACCESS_KEY` | Secret | AWS IAM Secret Access Key | *Required for AWS* |
| `AWS_REGION` | Secret / Var | Target AWS Region | `us-east-1` |
| `ECR_REPOSITORY` | Secret / Var | Amazon ECR repository name | `fastapi-ecs-dev-repo` |
| `ECS_CLUSTER` | Secret / Var | Amazon ECS cluster name | `fastapi-ecs-dev-cluster` |
| `ECS_SERVICE` | Secret / Var | Amazon ECS service name | `fastapi-ecs-dev-service` |
| `ECS_TASK_DEFINITION` | Secret / Var | Amazon ECS task definition family | `fastapi-ecs-dev-task` |
| `CONTAINER_NAME` | Secret / Var | Name of container inside task definition | `fastapi-ecs-dev-container` |
| `ALB_NAME` | Secret / Var | Application Load Balancer name | `fastapi-ecs-dev-alb` |
| `ALB_DNS_NAME` | Secret / Var | Direct ALB DNS name (auto-discovered from AWS if omitted) | Auto-discovered |
| `SLACK_WEBHOOK_URL` | Secret | Slack Incoming Webhook URL for deployment cards | *Optional* |

---

## ⚡ Quick Start & Local Development

### 1. Running the Application Locally

```powershell
# 1. Clone repository
git clone https://github.com/iam-aniket-dutta/DevOps_Project_FastApi_Terraform_ECS_Fargate_CICD_Pipeline.git
cd DevOps_Project_FastApi_Terraform_ECS_Fargate_CICD_Pipeline

# 2. Navigate to application folder and create virtual environment
cd app
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # On Linux/macOS: source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Start the FastAPI server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive Web UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Running Tests & Code Coverage

```bash
# Run pytest with 14 automated tests and coverage report
pytest -v --cov=app --cov-report=term-missing app/tests
```

### 3. Running Flake8 Linter

```bash
# Verify code syntax and PEP8 compliance
flake8 app --exclude=.venv,venv --max-line-length=127
```

### 4. Running with Docker

```bash
# Build the production container
docker build -t fastapi-app:local ./app

# Run the container locally on port 8000
docker run -d --name fastapi-demo -p 8000:8000 fastapi-app:local

# Verify container health
curl http://localhost:8000/api/health
```

---

## 🛡️ DevSecOps & Security Best Practices

1. **Non-Root Container Execution:**
   - Multi-stage Docker build copies only the pre-compiled virtual environment.
   - Dedicated unprivileged user `appuser` (UID `10001`) and group `appgroup` (GID `10001`) with zero root privileges.
2. **Private Subnet Isolation:**
   - ECS Fargate tasks run strictly inside private subnets without public IP addresses (`assign_public_ip = false`).
   - Outbound internet access is securely mediated through a managed AWS NAT Gateway.
3. **Strict Network Segmentation:**
   - ALB Security Group accepts port 80 from the public internet.
   - ECS Security Group rejects all incoming traffic except traffic originating from `aws_security_group.alb.id` on port 8000.
4. **Vulnerability Scanning in CI/CD:**
   - Aqua Security Trivy scans every Docker image for CVEs before pushing to ECR.
   - Amazon ECR `scan_on_push = true` scans images for vulnerabilities on AWS registry intake.
5. **Least Privilege IAM Policies:**
   - ECS Execution Role is restricted to ECR image pulls and CloudWatch log writes.
   - Task Role possesses no administrative AWS credentials.
6. **Zero-Downtime High Availability:**
   - Minimum healthy percent set to `100%`, maximum percent set to `200%`.
   - New tasks must pass ALB target group health checks on `/api/health` before old tasks are terminated.
7. **Auditability & Provenance:**
   - Every production deployment registers a specific Git SHA tag, making rollbacks deterministic and instantaneous.

---

## 🧹 Infrastructure Teardown

To avoid incurring ongoing AWS charges when you are done with the project:

```bash
cd deploy
terraform destroy -auto-approve
```

---

## 👨‍💻 Author

**Aniket Dutta**  
GitHub: [@iam-aniket-dutta](https://github.com/iam-aniket-dutta)
