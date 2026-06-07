# BAO CAO THUC HANH 01

Dung Terraform va CloudFormation de quan ly va trien khai ha tang AWS

Mon hoc: Cong nghe DevOps va Ung dung  
Ma mon hoc: NT548  
Lop: `<Ma lop>`  
Nhom: `<So nhom>`

## Thanh Vien Thuc Hien

| STT | Ho va ten | MSSV | Phan cong | Diem tu danh gia |
| --- | --- | --- | --- | --- |
| 1 | Nguyen Van A |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

## Danh Gia Khac

| Noi dung | Chi tiet |
| --- | --- |
| Tong thoi gian thuc hien |  |
| Phan chia cong viec |  |
| Kho khan |  |
| De xuat, kien nghi |  |

## Bao Cao Chi Tiet

### 1. Terraform

#### 1.1. Cau truc module

- `modules/network`: VPC, public/private subnet, Internet Gateway, NAT Gateway, route tables, default security group.
- `modules/security`: Public EC2 Security Group va Private EC2 Security Group.
- `modules/compute`: Public EC2 va Private EC2.

#### 1.2. Ket qua trien khai

Dien ket qua `terraform output` sau khi apply:

```text
vpc_id =
public_instance_id =
public_instance_public_ip =
private_instance_id =
private_instance_private_ip =
```

### 2. CloudFormation

#### 2.1. Cau truc nested stacks

- `root.yaml`: Stack tong, truyen tham so va noi output giua cac module.
- `modules/network.yaml`: Tai nguyen network.
- `modules/security.yaml`: Security groups.
- `modules/compute.yaml`: EC2 instances.

#### 2.2. Ket qua trien khai

Dien output cua CloudFormation stack:

```text
VpcId =
PublicInstanceId =
PublicInstancePublicIp =
PrivateInstanceId =
PrivateInstancePrivateIp =
```

### 3. Test Cases

Lenh chay test:

```powershell
python -m unittest discover -s tests -v
```

Ket qua:

```text
<Dan ket qua test tai day>
```

### 4. Nhan Xet Bao Mat

- Public EC2 chi mo SSH tu CIDR duoc cau hinh.
- Private EC2 chi nhan SSH tu Public EC2 Security Group.
- Private subnet truy cap Internet qua NAT Gateway.
- Default Security Group duoc quan ly de tranh rule mo ngoai y muon.
