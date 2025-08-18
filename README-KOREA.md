# DevOps Demo 프로젝트 - 한국 리전 설정

이 프로젝트는 AWS EKS를 사용한 DevOps 데모 애플리케이션입니다. 한국 리전(ap-northeast-2, 서울)에 최적화되어 있습니다.

## 🗺️ 리전 정보

- **AWS 리전**: `ap-northeast-2` (서울, 한국)
- **사용 가능한 가용영역**: `ap-northeast-2a`, `ap-northeast-2c`
- **네트워크 지연**: 한국에서 가장 낮은 지연시간
- **데이터 주권**: 한국 내 데이터 저장

## 🚀 빠른 시작

### 1. 사전 요구사항

```bash
# AWS CLI 설치 및 설정
aws configure
# AWS Access Key ID: [입력]
# AWS Secret Access Key: [입력]
# Default region name: ap-northeast-2
# Default output format: json

# Terraform 설치
# kubectl 설치
```

### 2. 개발 환경 배포

```bash
# 개발 환경 배포 스크립트 실행
chmod +x scripts/deploy-development.sh
./scripts/deploy-development.sh
```

### 3. 프로덕션 환경 배포

```bash
cd infrastructure/production
terraform init
terraform plan
terraform apply
```

## 🏗️ 인프라 구성

### 개발 환경
- **EKS 클러스터**: `devops-demo-dev-cluster`
- **노드 그룹**: t3.small/t3.medium (비용 최적화)
- **데이터베이스**: RDS PostgreSQL (t3.micro)
- **캐시**: ElastiCache Redis (t3.micro)
- **가용영역**: 2개 (비용 절약)

### 프로덕션 환경
- **EKS 클러스터**: `devops-demo-cluster`
- **노드 그룹**: m5.large/m5.xlarge (성능 최적화)
- **데이터베이스**: RDS PostgreSQL (고가용성)
- **캐시**: ElastiCache Redis (Multi-AZ)
- **가용영역**: 2개 (한국 리전 제한)

## 💰 비용 최적화 (한국 리전)

### 개발 환경
- 단일 NAT Gateway 사용
- t3.micro 인스턴스 사용
- 백업 보관 기간 단축 (3일)
- Multi-AZ 비활성화

### 프로덕션 환경
- 고가용성 보장
- 자동 백업 및 복구
- 성능 모니터링 활성화

## 🔧 설정 파일

### Terraform 설정
- `infrastructure/development/` - 개발 환경
- `infrastructure/production/` - 프로덕션 환경

### Kubernetes 매니페스트
- `k8s/development/` - 개발 환경
- `k8s/production/` - 프로덕션 환경

## 📊 모니터링

### CloudWatch
- 애플리케이션 로그: `/aws/eks/devops-demo/application`
- VPC Flow Logs 활성화
- RDS 성능 인사이트

### Prometheus + Grafana
- 애플리케이션 메트릭 수집
- Kubernetes 리소스 모니터링
- 커스텀 대시보드

## 🚨 문제 해결

### 일반적인 문제

1. **EKS 클러스터 연결 실패**
   ```bash
   aws eks update-kubeconfig --region ap-northeast-2 --name devops-demo-dev-cluster
   ```

2. **Terraform 상태 잠금**
   ```bash
   aws dynamodb delete-item \
     --table-name terraform-state-lock \
     --key '{"LockID": {"S": "devops-demo-terraform-state/development/terraform.tfstate"}}' \
     --region ap-northeast-2
   ```

3. **리소스 정리**
   ```bash
   cd infrastructure/development
   terraform destroy
   ```

## 📞 지원

- **프로젝트 이슈**: GitHub Issues
- **AWS 지원**: 한국어 지원 가능
- **지역**: 서울 리전 기반

## 🔒 보안

- 모든 리소스에 암호화 적용
- VPC 내부에서만 리소스 접근
- IAM 역할 기반 접근 제어
- 보안 그룹으로 네트워크 보안

## 📈 확장성

- Auto Scaling Group으로 자동 확장
- 로드 밸런서로 트래픽 분산
- 다중 가용영역으로 고가용성 보장
- Terraform으로 인프라 자동화

---

**참고**: 한국 리전에서는 일부 AWS 서비스가 제한적일 수 있습니다. 프로덕션 배포 전에 서비스 가용성을 확인하세요.
