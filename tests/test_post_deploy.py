import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGION = os.environ.get("AWS_REGION", "us-east-1")
IAC_SOURCE = os.environ.get("IAC_SOURCE", "terraform").lower()
STACK_NAME = os.environ.get("STACK_NAME", "devops-lab01")


def run_command(args, cwd=ROOT):
    completed = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        command = " ".join(str(arg) for arg in args)
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"Command failed: {command}\n{detail}")
    return completed.stdout.strip()


def aws(args):
    return json.loads(run_command(["aws", *args, "--region", REGION, "--output", "json"]))


def load_outputs():
    if IAC_SOURCE == "cloudformation":
        stack = aws([
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            STACK_NAME,
        ])
        outputs = stack["Stacks"][0].get("Outputs", [])
        mapped = {item["OutputKey"]: item["OutputValue"] for item in outputs}
        return {
            "vpc_id": mapped["VpcId"],
            "public_instance_id": mapped["PublicInstanceId"],
            "public_instance_public_ip": mapped["PublicInstancePublicIp"],
            "private_instance_id": mapped["PrivateInstanceId"],
            "private_instance_private_ip": mapped["PrivateInstancePrivateIp"],
        }

    try:
        raw = run_command(["terraform", "output", "-json"], cwd=ROOT / "terraform")
    except RuntimeError as exc:
        raise RuntimeError(
            "Terraform outputs are not available. Run `terraform apply` before "
            "this test, or set IAC_SOURCE=cloudformation after deploying the "
            "CloudFormation stack."
        ) from exc
    outputs = json.loads(raw)
    return {key: value["value"] for key, value in outputs.items()}


class AwsInfrastructurePostDeployTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = load_outputs()
        cls.vpc_id = cls.outputs["vpc_id"]
        cls.public_instance_id = cls.outputs["public_instance_id"]
        cls.private_instance_id = cls.outputs["private_instance_id"]

        cls.public_instance = cls.describe_instance(cls.public_instance_id)
        cls.private_instance = cls.describe_instance(cls.private_instance_id)

    @staticmethod
    def describe_instance(instance_id):
        response = aws(["ec2", "describe-instances", "--instance-ids", instance_id])
        return response["Reservations"][0]["Instances"][0]

    def test_vpc_exists_and_dns_enabled(self):
        response = aws(["ec2", "describe-vpcs", "--vpc-ids", self.vpc_id])
        vpc = response["Vpcs"][0]
        self.assertEqual(vpc["State"], "available")
        self.assertEqual(vpc["CidrBlock"], "10.10.0.0/16")

        dns_support = aws([
            "ec2",
            "describe-vpc-attribute",
            "--vpc-id",
            self.vpc_id,
            "--attribute",
            "enableDnsSupport",
        ])
        dns_hostnames = aws([
            "ec2",
            "describe-vpc-attribute",
            "--vpc-id",
            self.vpc_id,
            "--attribute",
            "enableDnsHostnames",
        ])
        self.assertTrue(dns_support["EnableDnsSupport"]["Value"])
        self.assertTrue(dns_hostnames["EnableDnsHostnames"]["Value"])

    def test_public_and_private_subnets_are_configured(self):
        public_subnet_id = self.public_instance["SubnetId"]
        private_subnet_id = self.private_instance["SubnetId"]
        response = aws([
            "ec2",
            "describe-subnets",
            "--subnet-ids",
            public_subnet_id,
            private_subnet_id,
        ])
        subnets = {subnet["SubnetId"]: subnet for subnet in response["Subnets"]}

        self.assertEqual(subnets[public_subnet_id]["CidrBlock"], "10.10.1.0/24")
        self.assertTrue(subnets[public_subnet_id]["MapPublicIpOnLaunch"])
        self.assertEqual(subnets[private_subnet_id]["CidrBlock"], "10.10.2.0/24")
        self.assertFalse(subnets[private_subnet_id]["MapPublicIpOnLaunch"])

    def test_public_route_table_uses_internet_gateway(self):
        route_table = self.route_table_for_subnet(self.public_instance["SubnetId"])
        default_routes = [
            route for route in route_table["Routes"]
            if route.get("DestinationCidrBlock") == "0.0.0.0/0"
        ]
        self.assertTrue(default_routes)
        self.assertTrue(default_routes[0].get("GatewayId", "").startswith("igw-"))

    def test_private_route_table_uses_nat_gateway(self):
        route_table = self.route_table_for_subnet(self.private_instance["SubnetId"])
        default_routes = [
            route for route in route_table["Routes"]
            if route.get("DestinationCidrBlock") == "0.0.0.0/0"
        ]
        self.assertTrue(default_routes)
        self.assertTrue(default_routes[0].get("NatGatewayId", "").startswith("nat-"))

        nat_gateway_id = default_routes[0]["NatGatewayId"]
        response = aws(["ec2", "describe-nat-gateways", "--nat-gateway-ids", nat_gateway_id])
        self.assertEqual(response["NatGateways"][0]["State"], "available")

    def test_security_groups_restrict_ssh_access(self):
        public_sg_id = self.public_instance["SecurityGroups"][0]["GroupId"]
        private_sg_id = self.private_instance["SecurityGroups"][0]["GroupId"]
        response = aws([
            "ec2",
            "describe-security-groups",
            "--group-ids",
            public_sg_id,
            private_sg_id,
        ])
        groups = {group["GroupId"]: group for group in response["SecurityGroups"]}

        public_ingress = groups[public_sg_id]["IpPermissions"]
        self.assertTrue(any(
            rule.get("IpProtocol") == "tcp"
            and rule.get("FromPort") == 22
            and rule.get("ToPort") == 22
            and rule.get("IpRanges")
            for rule in public_ingress
        ))

        private_ingress = groups[private_sg_id]["IpPermissions"]
        self.assertTrue(any(
            rule.get("IpProtocol") == "tcp"
            and rule.get("FromPort") == 22
            and rule.get("ToPort") == 22
            and any(pair.get("GroupId") == public_sg_id for pair in rule.get("UserIdGroupPairs", []))
            for rule in private_ingress
        ))

    def test_ec2_instances_match_public_private_requirements(self):
        self.assertEqual(self.public_instance["State"]["Name"], "running")
        self.assertIn("PublicIpAddress", self.public_instance)
        self.assertEqual(
            self.public_instance.get("PublicIpAddress"),
            self.outputs["public_instance_public_ip"],
        )

        self.assertEqual(self.private_instance["State"]["Name"], "running")
        self.assertNotIn("PublicIpAddress", self.private_instance)
        self.assertEqual(
            self.private_instance["PrivateIpAddress"],
            self.outputs["private_instance_private_ip"],
        )

    @staticmethod
    def route_table_for_subnet(subnet_id):
        response = aws([
            "ec2",
            "describe-route-tables",
            "--filters",
            f"Name=association.subnet-id,Values={subnet_id}",
        ])
        return response["RouteTables"][0]


if __name__ == "__main__":
    unittest.main(verbosity=2)