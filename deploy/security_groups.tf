# ==============================================================================
# Application Load Balancer Security Group
# ==============================================================================
resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Controls public inbound HTTP traffic to the ALB"
  vpc_id      = aws_vpc.main.id

  # Allow inbound HTTP from the public internet
  ingress {
    description = "Allow inbound HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic to forward requests to backend ECS tasks
  egress {
    description = "Allow all outbound traffic from ALB"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-alb-sg"
  }
}

# ==============================================================================
# ECS Tasks Security Group (Strict: ALB -> ECS only, NO public ingress)
# ==============================================================================
resource "aws_security_group" "ecs_tasks" {
  name        = "${local.name_prefix}-ecs-tasks-sg"
  description = "Allows ingress strictly from ALB to ECS container port; no public ingress"
  vpc_id      = aws_vpc.main.id

  # Ingress strictly allowed ONLY from ALB Security Group
  ingress {
    description     = "Allow traffic ONLY from ALB on application port"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow outbound traffic to pull images from ECR and send logs via NAT Gateway
  egress {
    description = "Allow all outbound traffic from ECS tasks"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-ecs-tasks-sg"
  }
}
