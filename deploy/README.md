# 🏗️ Terraform Base Infrastructure: AWS ECS Fargate & ALB

Production-ready Terraform configurations to provision base AWS infrastructure for deploying containerized applications to **ECS Fargate**.

---

## 🏛️ Architecture Overview

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
                                      │ Ingress ONLY from ALB SG
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
    ┌─────────────────────────┐               ┌─────────────────────────┐
    │ Private Subnet (AZ-1)   │               │ Private Subnet (AZ-2)   │
    │                         │               │                         │
    │  ECS Task (Port 8000)   │               │  ECS Task (Port 8000)   │
    │  (Outbound via NAT GW)  │               │  (Outbound via NAT GW)  │
    └─────────────────────────┘               └─────────────────────────┘
```

---

## 📦 Provisioned Resources

| Component | Resource | Description |
|---|---|---|
| **VPC** | `aws_vpc` | CIDR `10.0.0.0/16` with DNS hostnames and support enabled |
| **Subnets** | `aws_subnet` | 2 Public Subnets & 2 Private Subnets across 2 Availability Zones |
| **Internet Gateway** | `aws_internet_gateway` | Direct internet ingress/egress for public subnets and ALB |
| **NAT Gateway** | `aws_nat_gateway`, `aws_eip` | Outbound internet access for ECS tasks in private subnets |
| **Route Tables** | `aws_route_table` | Public routes to IGW; Private routes to NAT Gateway |
| **ALB Security Group** | `aws_security_group` | Public ingress on port 80 (HTTP); all egress allowed |
| **ECS Security Group** | `aws_security_group` | Ingress on port 8000 **ONLY from ALB Security Group** (no direct public ingress) |
| **Load Balancer** | `aws_lb` | Public Application Load Balancer across the 2 public subnets |
| **Target Group** | `aws_lb_target_group` | Target type `ip` (port 8000) with health check path `/api/health` |
| **ALB Listener** | `aws_lb_listener` | Port 80 listener forwarding traffic to target group |
| **ECR Repository** | `aws_ecr_repository` | Container registry with image vulnerability scanning & lifecycle retention policy |
| **ECS Cluster** | `aws_ecs_cluster` | ECS cluster with Fargate & Fargate Spot capacity providers enabled |
| **CloudWatch Logs** | `aws_cloudwatch_log_group` | Centralized log group for ECS task execution |
| **IAM Roles** | `aws_iam_role` | ECS Task Execution Role & ECS Task Role with least-privilege policies |
| **Task Definition** | `aws_ecs_task_definition` | Fargate task definition with non-root container, port 8000, and awslogs driver |
| **ECS Service** | `aws_ecs_service` | Fargate service with `desired_count = 2` for HA, wired to ALB Target Group |

---

## 🚀 How to Deploy

### 1. Prerequisites
- **AWS CLI** installed and configured (`aws configure`).
- **Terraform** v1.5+ installed.
- Appropriate AWS IAM permissions to provision VPC, EC2, ALB, ECR, ECS, and IAM roles.

### 2. Initialize Terraform
```bash
cd deploy
terraform init
```

### 3. Review the Execution Plan
```bash
terraform plan
```

To customize variables (e.g. region, project name, or CIDRs):
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars as desired
terraform plan -var-file="terraform.tfvars"
```

### 4. Apply Infrastructure
```bash
terraform apply
```

### 5. Inspect Outputs
Once provisioned, Terraform outputs the key identifiers:
- `alb_dns_name` & `alb_url`
- `ecr_repository_url`
- `ecs_cluster_name`
- `ecs_service_name`
- `ecs_task_definition_arn`
- `vpc_id`, `public_subnet_ids`, `private_subnet_ids`
- `alb_security_group_id`, `ecs_tasks_security_group_id`

### 6. Clean Up / Destroy
To tear down all provisioned resources:
```bash
terraform destroy
```
