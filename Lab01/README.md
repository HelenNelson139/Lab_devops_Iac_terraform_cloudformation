# NT548 - Bai Tap Thuc Hanh 01

Bo ma nguon nay trien khai ha tang AWS bang Terraform va CloudFormation:

- VPC co public subnet va private subnet.
- Internet Gateway cho public subnet.
- NAT Gateway cho private subnet truy cap Internet theo chieu outbound.
- Route table rieng cho public/private subnet.
- Default Security Group cua VPC duoc quan ly va khoa rule mac dinh.
- EC2 public va private.
- Security Group cho public EC2 chi cho SSH tu CIDR duoc cau hinh.
- Security Group cho private EC2 chi cho SSH tu public EC2 Security Group.
- Test cases tinh de kiem tra cau truc va cac tai nguyen bat buoc.

## Cau Truc

```text
.
├── cloudformation/
│   ├── parameters.example.json
│   ├── root.yaml
│   └── modules/
│       ├── compute.yaml
│       ├── network.yaml
│       └── security.yaml
├── terraform/
│   ├── main.tf
│   ├── outputs.tf
│   ├── provider.tf
│   ├── terraform.tfvars.example
│   ├── variables.tf
│   ├── versions.tf
│   └── modules/
│       ├── compute/
│       ├── network/
│       └── security/
└── tests/
    └── test_iac_static.py
```

## Dieu Kien

- AWS CLI da cau hinh credentials hop le.
- Terraform >= 1.6 neu chay phan Terraform.
- Python >= 3.10 de chay tests.
- Mot EC2 key pair da ton tai trong AWS Region su dung.

Nen dat `allowed_ssh_cidr` thanh IP public cua nguoi dung theo dang `/32`, vi du `203.0.113.10/32`.

## Chay Bang Terraform

```powershell
cd terraform
Copy-Item terraform.tfvars.example terraform.tfvars
```

Cap nhat cac gia tri trong `terraform.tfvars`, dac biet:

- `aws_region`
- `availability_zone`
- `allowed_ssh_cidr`
- `key_name`

Sau do chay:

```powershell
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Xoa ha tang:

```powershell
terraform destroy
```

## Chay Bang CloudFormation

Cap nhat cac tham so deploy, dac biet `AllowedSshCidr` va `KeyName`. File `cloudformation/parameters.example.json` duoc de san neu muon dung voi `create-stack` hoac luu cau hinh nop bai.

Vi root stack dung nested stacks, can package cac template con len S3 truoc khi deploy:

```powershell
cd cloudformation
aws s3 mb s3://<bucket-artifact-cua-ban>
aws cloudformation package `
  --template-file root.yaml `
  --s3-bucket <bucket-artifact-cua-ban> `
  --output-template-file packaged.yaml

aws cloudformation deploy `
  --template-file packaged.yaml `
  --stack-name nt548-lab01 `
  --parameter-overrides `
    ProjectName=nt548-lab01 `
    Environment=lab `
    VpcCidr=10.10.0.0/16 `
    PublicSubnetCidr=10.10.1.0/24 `
    PrivateSubnetCidr=10.10.2.0/24 `
    AvailabilityZone=ap-southeast-1a `
    AllowedSshCidr=203.0.113.10/32 `
    KeyName=your-existing-key-pair `
    InstanceType=t3.micro
```

Xoa stack:

```powershell
aws cloudformation delete-stack --stack-name nt548-lab01
```

## Chay Test Cases

Tests khong tao tai nguyen AWS. Muc tieu la kiem tra nhanh cac thanh phan bat buoc co trong source code.

```powershell
python -m unittest discover -s tests -v
```

## Bao Cao

Mau bao cao nam tai `reports/BaoCaoThucHanh01.md`. Co the dien ket qua trien khai va chuyen sang Word theo mau cua mon hoc.

## Ghi Chu Bao Mat

- Default Security Group cua VPC duoc quan ly voi rule rong de tranh mo truy cap ngoai y muon.
- Public EC2 chi mo SSH tu `allowed_ssh_cidr`/`AllowedSshCidr`.
- Private EC2 khong co public IP va chi nhan SSH tu Security Group cua public EC2.
- Private subnet di Internet qua NAT Gateway, khong route truc tiep qua Internet Gateway.
