resource "aws_security_group" "public_ec2" {
  name        = "${var.project_name}-public-ec2-sg"
  description = "Allow SSH to public EC2 from the configured CIDR."
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from configured client CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    description = "Outbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-public-ec2-sg"
  }
}

resource "aws_security_group" "private_ec2" {
  name        = "${var.project_name}-private-ec2-sg"
  description = "Allow SSH to private EC2 only from the public EC2 security group."
  vpc_id      = var.vpc_id

  ingress {
    description     = "SSH from public EC2 security group"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.public_ec2.id]
  }

  egress {
    description = "Outbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-private-ec2-sg"
  }
}
