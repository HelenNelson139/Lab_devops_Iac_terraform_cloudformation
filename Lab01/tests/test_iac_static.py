import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class TerraformStaticTests(unittest.TestCase):
    def test_root_uses_required_modules(self):
        main = read("terraform/main.tf")

        for module_name in ("network", "security", "compute"):
            self.assertRegex(main, rf'module\s+"{module_name}"')

    def test_network_module_defines_vpc_subnets_gateways_and_routes(self):
        network = read("terraform/modules/network/main.tf")

        required_resources = [
            'resource "aws_vpc" "this"',
            'resource "aws_default_security_group" "this"',
            'resource "aws_subnet" "public"',
            'resource "aws_subnet" "private"',
            'resource "aws_internet_gateway" "this"',
            'resource "aws_eip" "nat"',
            'resource "aws_nat_gateway" "this"',
            'resource "aws_route_table" "public"',
            'resource "aws_route_table" "private"',
        ]

        for resource in required_resources:
            self.assertIn(resource, network)

        self.assertIn('gateway_id = aws_internet_gateway.this.id', network)
        self.assertIn('nat_gateway_id = aws_nat_gateway.this.id', network)
        self.assertIn("map_public_ip_on_launch = true", network)
        self.assertIn("map_public_ip_on_launch = false", network)

    def test_security_groups_restrict_ssh_paths(self):
        security = read("terraform/modules/security/main.tf")

        self.assertIn('resource "aws_security_group" "public_ec2"', security)
        self.assertIn("from_port   = 22", security)
        self.assertIn("to_port     = 22", security)
        self.assertIn("cidr_blocks = [var.allowed_ssh_cidr]", security)
        self.assertIn('resource "aws_security_group" "private_ec2"', security)
        self.assertIn("security_groups = [aws_security_group.public_ec2.id]", security)

    def test_compute_module_creates_public_and_private_instances(self):
        compute = read("terraform/modules/compute/main.tf")

        self.assertIn('resource "aws_instance" "public"', compute)
        self.assertIn('resource "aws_instance" "private"', compute)
        self.assertRegex(
            compute,
            r'resource\s+"aws_instance"\s+"public"[\s\S]*associate_public_ip_address\s+=\s+true',
        )
        self.assertRegex(
            compute,
            r'resource\s+"aws_instance"\s+"private"[\s\S]*associate_public_ip_address\s+=\s+false',
        )


class CloudFormationStaticTests(unittest.TestCase):
    def test_root_stack_uses_nested_modules(self):
        root = read("cloudformation/root.yaml")

        for stack_name in ("NetworkStack", "SecurityStack", "ComputeStack"):
            self.assertIn(stack_name, root)

        for template_path in (
            "modules/network.yaml",
            "modules/security.yaml",
            "modules/compute.yaml",
        ):
            self.assertIn(template_path, root)

    def test_network_template_defines_required_resources(self):
        network = read("cloudformation/modules/network.yaml")

        for resource_type in (
            "AWS::EC2::VPC",
            "AWS::EC2::Subnet",
            "AWS::EC2::InternetGateway",
            "AWS::EC2::VPCGatewayAttachment",
            "AWS::EC2::EIP",
            "AWS::EC2::NatGateway",
            "AWS::EC2::RouteTable",
            "AWS::EC2::SubnetRouteTableAssociation",
            "AWS::EC2::SecurityGroup",
        ):
            self.assertIn(resource_type, network)

        self.assertRegex(network, r"GatewayId:\s+Ref:\s+InternetGateway")
        self.assertRegex(network, r"NatGatewayId:\s+Ref:\s+NatGateway")
        self.assertIn("MapPublicIpOnLaunch: true", network)
        self.assertIn("MapPublicIpOnLaunch: false", network)

    def test_security_template_restricts_public_and_private_ssh(self):
        security = read("cloudformation/modules/security.yaml")

        self.assertIn("PublicEc2SecurityGroup", security)
        self.assertIn("PrivateEc2SecurityGroup", security)
        self.assertRegex(security, r"CidrIp:\s+Ref:\s+AllowedSshCidr")
        self.assertRegex(
            security,
            r"SourceSecurityGroupId:\s+Ref:\s+PublicEc2SecurityGroup",
        )
        self.assertGreaterEqual(len(re.findall(r"FromPort:\s+22", security)), 2)
        self.assertGreaterEqual(len(re.findall(r"ToPort:\s+22", security)), 2)

    def test_compute_template_creates_public_and_private_instances(self):
        compute = read("cloudformation/modules/compute.yaml")

        self.assertIn("PublicInstance:", compute)
        self.assertIn("PrivateInstance:", compute)
        self.assertIn("AssociatePublicIpAddress: true", compute)
        self.assertIn("AssociatePublicIpAddress: false", compute)
        self.assertIn("AWS::EC2::Instance", compute)


if __name__ == "__main__":
    unittest.main()
