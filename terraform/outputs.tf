output "vpc_id" {
  description = "Created VPC ID."
  value       = module.network.vpc_id
}

output "public_instance_id" {
  description = "Public EC2 instance ID."
  value       = module.compute.public_instance_id
}

output "public_instance_public_ip" {
  description = "Public IP of the public EC2 instance."
  value       = module.compute.public_instance_public_ip
}

output "private_instance_id" {
  description = "Private EC2 instance ID."
  value       = module.compute.private_instance_id
}

output "private_instance_private_ip" {
  description = "Private IP of the private EC2 instance."
  value       = module.compute.private_instance_private_ip
}
