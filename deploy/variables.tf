variable "aws_region" {
  description = "The AWS region where resources will be provisioned."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix applied to all resources."
  type        = string
  default     = "fastapi-ecs"
}

variable "environment" {
  description = "Deployment environment name (e.g. dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the 2 public subnets across 2 AZs."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]

  validation {
    condition     = length(var.public_subnet_cidrs) == 2
    error_message = "Exactly two public subnet CIDRs must be specified for HA across 2 AZs."
  }
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the 2 private subnets across 2 AZs."
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]

  validation {
    condition     = length(var.private_subnet_cidrs) == 2
    error_message = "Exactly two private subnet CIDRs must be specified for HA across 2 AZs."
  }
}

variable "container_port" {
  description = "Port exposed by the FastAPI container."
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "Health check URL path for the ALB target group."
  type        = string
  default     = "/api/health"
}

variable "app_image" {
  description = "Docker image URI to deploy. If blank, defaults to the ECR repo URL with latest tag."
  type        = string
  default     = ""
}

variable "ecs_task_cpu" {
  description = "CPU units for the ECS task (e.g. '256' for 0.25 vCPU)."
  type        = string
  default     = "256"
}

variable "ecs_task_memory" {
  description = "Memory (in MiB) for the ECS task (e.g. '512' for 0.5 GB)."
  type        = string
  default     = "512"
}

variable "desired_count" {
  description = "Desired number of running ECS task instances for High Availability (HA)."
  type        = number
  default     = 2
}
