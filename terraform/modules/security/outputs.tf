output "public_ec2_security_group_id" {
  description = "Security group ID for public EC2."
  value       = aws_security_group.public_ec2.id
}

output "private_ec2_security_group_id" {
  description = "Security group ID for private EC2."
  value       = aws_security_group.private_ec2.id
}
