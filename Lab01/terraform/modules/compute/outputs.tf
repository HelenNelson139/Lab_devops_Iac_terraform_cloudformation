output "public_instance_id" {
  description = "Public EC2 instance ID."
  value       = aws_instance.public.id
}

output "public_instance_public_ip" {
  description = "Public EC2 public IP."
  value       = aws_eip.public.public_ip
}

output "private_instance_id" {
  description = "Private EC2 instance ID."
  value       = aws_instance.private.id
}

output "private_instance_private_ip" {
  description = "Private EC2 private IP."
  value       = aws_instance.private.private_ip
}
