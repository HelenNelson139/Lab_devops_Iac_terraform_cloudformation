variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
  default     = "devops-lab01"
}

variable "environment" {
  description = "Deployment environment tag."
  type        = string
  default     = "lab"
}

variable "aws_region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "availability_zone" {
  description = "Availability zone for the lab subnets."
  type        = string
  default     = "us-east-1a"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.10.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.10.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet."
  type        = string
  default     = "10.10.2.0/24"
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH to the public EC2 instance. Use a /32 public IP in real deployments."
  type        = string
}

variable "key_name" {
  description = "Existing EC2 key pair name."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}
