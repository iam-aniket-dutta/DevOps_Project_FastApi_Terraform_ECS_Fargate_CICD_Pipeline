provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Fetch available Availability Zones in the current region
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  # Pick the first two available AZs
  selected_azs = slice(data.aws_availability_zones.available.names, 0, 2)
}
