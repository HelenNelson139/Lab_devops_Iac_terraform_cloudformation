variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "key_name" {
  description = "Existing EC2 key pair name."
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID."
  type        = string
}

variable "private_subnet_id" {
  description = "Private subnet ID."
  type        = string
}

variable "public_security_group_id" {
  description = "Security group ID for public EC2."
  type        = string
}

variable "private_security_group_id" {
  description = "Security group ID for private EC2."
  type        = string
}
