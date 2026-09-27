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
- **Run Tests:** `pytest -v`
