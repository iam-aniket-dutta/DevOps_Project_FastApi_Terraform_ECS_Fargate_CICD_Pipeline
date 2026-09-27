# ==============================================================================
# Networking Outputs
# ==============================================================================
output "vpc_id" {
  description = "The ID of the created VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets across 2 AZs."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets across 2 AZs."
  value       = aws_subnet.private[*].id
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway."
  value       = aws_nat_gateway.nat.id
}

# ==============================================================================
# Security Group Outputs
# ==============================================================================
output "alb_security_group_id" {
  description = "Security Group ID for the Application Load Balancer."
  value       = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  description = "Security Group ID for the ECS Tasks (ALB ingress only)."
  value       = aws_security_group.ecs_tasks.id
}

# ==============================================================================
# Application Load Balancer Outputs
# ==============================================================================
output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer."
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "Public HTTP URL of the Application Load Balancer."
  value       = "http://${aws_lb.main.dns_name}"
}

output "target_group_arn" {
  description = "ARN of the ALB Target Group for ECS tasks."
  value       = aws_lb_target_group.app.arn
}

# ==============================================================================
# ECR Outputs
# ==============================================================================
output "ecr_repository_url" {
  description = "URL of the Amazon ECR repository for Docker images."
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_repository_name" {
  description = "Name of the Amazon ECR repository."
  value       = aws_ecr_repository.app.name
}

# ==============================================================================
# ECS Cluster Outputs
# ==============================================================================
output "ecs_cluster_name" {
  description = "Name of the ECS Fargate cluster."
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS Fargate cluster."
  value       = aws_ecs_cluster.main.arn
}

output "ecs_execution_role_arn" {
  description = "ARN of the IAM role for ECS task execution."
  value       = aws_iam_role.ecs_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the IAM role for the ECS container task."
  value       = aws_iam_role.ecs_task_role.arn
}

output "ecs_task_definition_arn" {
  description = "ARN of the provisioned ECS Task Definition."
  value       = aws_ecs_task_definition.app.arn
}

output "ecs_service_name" {
  description = "Name of the provisioned ECS Service."
  value       = aws_ecs_service.app.name
}
