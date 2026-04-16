variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name used for all resources (Lambda, API Gateway, IAM role, etc.)"
  type        = string
  default     = "plan-estudio"
}

variable "table_name" {
  description = "DynamoDB table name"
  type        = string
  default     = "study-plan-items"
}

variable "environment" {
  description = "Environment tag (prod, staging, dev)"
  type        = string
  default     = "prod"
}
