module "network" {
  source = "./modules/network"

  project_name        = var.project_name
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidr  = var.public_subnet_cidr
  private_subnet_cidr = var.private_subnet_cidr
  availability_zone   = var.availability_zone
}

module "security" {
  source = "./modules/security"

  project_name     = var.project_name
  vpc_id           = module.network.vpc_id
  allowed_ssh_cidr = var.allowed_ssh_cidr
}

module "compute" {
  source = "./modules/compute"

  project_name              = var.project_name
  instance_type             = var.instance_type
  key_name                  = var.key_name
  public_subnet_id          = module.network.public_subnet_id
  private_subnet_id         = module.network.private_subnet_id
  public_security_group_id  = module.security.public_ec2_security_group_id
  private_security_group_id = module.security.private_ec2_security_group_id
}
