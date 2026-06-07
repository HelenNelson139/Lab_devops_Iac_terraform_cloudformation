# Devops - Terraform và CloudFormation để quản lý và triển khai hạ tầng AWS
Hướng dẫn chạy mã nguồn Terraform và CloudFormation để triển khai hạ tầng AWS cho bài thực hành 01.
## Điều Kiện Và Cách Chuẩn Bị
### 1. AWS CLI
Kiểm tra AWS CLI:
```powershell
aws --version
```
Nếu chưa có, cài bằng:
```powershell
winget install Amazon.AWSCLI
```
Nếu cài xong nhưng PowerShell chưa nhận lệnh `aws`, đóng PowerShell và mở lại. Nếu vẫn chưa nhận, thêm AWS CLI vào `PATH` tạm thời:
```powershell
$env:Path += ";C:\Program Files\Amazon\AWSCLIV2"
aws --version
```
### 2. AWS Credentials
Nếu dùng AWS Academy/VocLabs, vào `Cloud Access`, bấm `Show` ở mục `AWS CLI`, rồi copy block có dạng:
```ini
[default]
aws_access_key_id=...
aws_secret_access_key=...
aws_session_token=...
```
Tạo thư mục `.aws` và lưu credentials:
```powershell
New-Item -ItemType Directory -Force $env:USERPROFILE\.aws
notepad "$env:USERPROFILE\.aws\credentials"
```
Dán block credentials vào file trên, sau đó lưu lại. Tiếp theo tạo file cấu hình region:
```powershell
notepad "$env:USERPROFILE\.aws\config"
```
Dán nội dung sau, thay `us-east-1` bằng region đang dùng nếu khác:
```ini
[default]
region=us-east-1
output=json
```
Kiểm tra credentials:
```powershell
aws sts get-caller-identity
```
### 3. Terraform
Kiểm tra Terraform:
```powershell
terraform version
```
Nếu chưa có, cài bằng:
```powershell
winget install Hashicorp.Terraform
```
Đóng PowerShell, mở lại, rồi kiểm tra lại:
```powershell
terraform version
```
### 4. EC2 Key Pair
Trong AWS Console, chọn đúng region sẽ deploy, sau đó vào:
```text
EC2 -> Key pairs -> Create key pair
```
Tạo key pair với thông tin ví dụ:
```text
Name: devops-lab-key
Key pair type: RSA
Private key file format: .pem
```
Lưu file `.pem` ở một thư mục riêng. Nếu lưu file `.pem` ở đường dẫn khác, chỉ cần thay đường dẫn trong các lệnh SSH/SCP bên dưới. Terraform không cần đường dẫn file `.pem`; Terraform chỉ cần tên key pair trong `terraform/terraform.tfvars`:
```hcl
key_name = "devops-lab-key"
```
Nếu dùng tên key pair khác, sửa lại `key_name` cho khớp.

## Cấu Hình Terraform
Tạo file cấu hình từ file mẫu:
```powershell
cd <duong-dan-repo>\terraform
Copy-Item terraform.tfvars.example terraform.tfvars
```
Mở `terraform.tfvars` và cập nhật các giá trị cần thiết:

```hcl
project_name        = "devops-lab01"
environment         = "lab"
aws_region          = "us-east-1"
availability_zone   = "us-east-1a"
vpc_cidr            = "10.10.0.0/16"
public_subnet_cidr  = "10.10.1.0/24"
private_subnet_cidr = "10.10.2.0/24"
allowed_ssh_cidr    = "<cidr-duoc-phep-ssh>"
key_name            = "<ten-key-pair>"
instance_type       = "t3.micro"
```
Chỗ `allowed_ssh_cidr`:
```powershell
curl.exe https://checkip.amazonaws.com
```
Nếu IP public là `x.x.x.x`, có thể đặt:
```hcl
allowed_ssh_cidr = "x.x.x.x/32"
```
## Chạy Terraform
```powershell
cd <duong-dan-repo>\terraform
terraform init
terraform plan
terraform apply
```
Khi Terraform hỏi xác nhận, nhập:
```text
yes
```
Lấy output:
```powershell
terraform output
```
SSH vào Public EC2:
```powershell
ssh -i <duong-dan-file-pem> ec2-user@<public_instance_public_ip>
```
Copy private key lên Public EC2:
```powershell
scp -i <duong-dan-file-pem> <duong-dan-file-pem> ec2-user@<public_instance_public_ip>:/home/ec2-user/devops-lab-key.pem
```
Từ Public EC2, SSH vào Private EC2:
```bash
chmod 400 devops-lab-key.pem
ssh -i devops-lab-key.pem ec2-user@<private_instance_private_ip>
```
Xóa hạ tầng Terraform sau khi demo xong:
```powershell
terraform destroy
```
## Chạy Test Sau Khi Triển Khai
Các test này chạy sau khi đã `terraform apply` hoặc deploy CloudFormation thành công. Test dùng AWS CLI để kiểm tra tài nguyên thật trên AWS.
Chạy test cho hạ tầng triển khai bằng Terraform:
```powershell
cd <duong-dan-repo>
python -B -m unittest discover -s tests -v
```
Chạy test cho hạ tầng triển khai bằng CloudFormation:
```powershell
cd <duong-dan-repo>
$env:IAC_SOURCE="cloudformation"
$env:STACK_NAME="devops-lab01"
python -B -m unittest discover -s tests -v
```
Các test kiểm tra:
- VPC tồn tại và bật DNS.
- Public/private subnet đúng CIDR và cấu hình public IP.
- Public route table đi qua Internet Gateway.
- Private route table đi qua NAT Gateway.
- Security Group public chỉ mở SSH theo CIDR cấu hình.
- Security Group private chỉ mở SSH từ Security Group của Public EC2.
- Public EC2 có public IP và đang running.
- Private EC2 không có public IP và đang running.
## Chạy CloudFormation
Trước khi chạy CloudFormation, nên xóa hạ tầng Terraform nếu đã triển khai trước đó để tránh tạo trùng tài nguyên:
```powershell
cd <duong-dan-repo>\terraform
terraform destroy
```
Sau đó chuyển sang thư mục CloudFormation:
```powershell
cd <duong-dan-repo>\cloudformation
```
Package nested stacks lên S3. Tên bucket phải là duy nhất trên toàn AWS:
```powershell
aws s3 mb s3://<bucket-artifact-cua-ban> --region us-east-1
aws cloudformation package `
  --template-file root.yaml `
  --s3-bucket <bucket-artifact-cua-ban> `
  --output-template-file packaged.yaml `
  --region us-east-1
```
### Cách 1: Truyền tham số trực tiếp trong lệnh deploy
Thay `<cidr-duoc-phep-ssh>` và `<ten-key-pair>` theo môi trường của bạn.
```powershell
aws cloudformation deploy `
  --template-file packaged.yaml `
  --stack-name devops-lab01 `
  --parameter-overrides `
    ProjectName=devops-lab01 `
    Environment=lab `
    VpcCidr=10.10.0.0/16 `
    PublicSubnetCidr=10.10.1.0/24 `
    PrivateSubnetCidr=10.10.2.0/24 `
    AvailabilityZone=us-east-1a `
    AllowedSshCidr=<cidr-duoc-phep-ssh> `
    KeyName=<ten-key-pair> `
    InstanceType=t3.micro `
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM `
  --region us-east-1
```
### Cách 2: Sửa tham số trong file JSON
Tạo file parameter chạy thật từ file mẫu:
```powershell
Copy-Item parameters.example.json parameters.json
```
Mở `parameters.json` và sửa các giá trị cần thiết, đặc biệt là:
```text
AllowedSshCidr
KeyName
AvailabilityZone
```
Chuyển file JSON thành parameter overrides:
```powershell
$parameterFile = Get-Content .\parameters.json | ConvertFrom-Json
$params = foreach ($parameter in $parameterFile) {
  "$($parameter.ParameterKey)=$($parameter.ParameterValue)"
}
```
Deploy stack:
```powershell
aws cloudformation deploy `
  --template-file packaged.yaml `
  --stack-name devops-lab01 `
  --parameter-overrides $params `
  --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM `
  --region us-east-1
```
Xem output sau khi deploy:
```powershell
aws cloudformation describe-stacks `
  --stack-name devops-lab01 `
  --query "Stacks[0].Outputs" `
  --output table `
  --region us-east-1
```
Xóa CloudFormation stack:
```powershell
aws cloudformation delete-stack `
  --stack-name devops-lab01 `
  --region us-east-1
```