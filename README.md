# DevOps Demo Project

이 프로젝트는 엔터프라이즈급 DevOps 실무를 보여주는 데모 애플리케이션입니다. AWS 계정이 없어도 대부분의 DevOps 작업들을 진행할 수 있도록 설계되었습니다.

## 🚀 현재 상태

### ✅ AWS 계정 없이도 진행 가능한 작업들

1. **애플리케이션 개발 및 테스트**
   - Python Flask 애플리케이션
   - 단위 테스트 및 통합 테스트
   - 코드 품질 검사 (linting, type checking)
   - 보안 스캔 (Bandit, Trivy)

2. **컨테이너화**
   - Docker 이미지 빌드 (multi-stage)
   - 컨테이너 보안 스캔
   - 로컬 레지스트리 테스트

3. **Kubernetes 배포**
   - 로컬 클러스터 (Docker Desktop, Minikube, Kind)
   - 개발/스테이징 환경 배포
   - 매니페스트 파일 검증

4. **CI/CD 파이프라인**
   - GitHub Actions 워크플로우
   - 코드 품질 게이트
   - 자동화된 테스트 및 빌드

5. **모니터링 및 로깅**
   - Prometheus 메트릭 수집
   - 구조화된 로깅
   - 헬스 체크 엔드포인트

### ⏳ AWS 계정이 필요할 때 진행할 작업들

1. **인프라 배포**
   - EKS 클러스터 생성
   - VPC 및 네트워킹 설정
   - RDS 데이터베이스
   - ElastiCache Redis
   - Application Load Balancer

2. **프로덕션 환경 배포**
   - 프로덕션 EKS 클러스터에 애플리케이션 배포
   - 프로덕션 모니터링 및 알림 설정

## 🛠️ 빠른 시작

### 1. 로컬 개발 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd github-actions-project

# Python 의존성 설치
pip install -r requirements-dev.txt
pip install -r requirements.txt

# 테스트 실행
pytest tests/ -v --cov=src

# 애플리케이션 실행
cd src
python app.py
```

### 2. Docker 이미지 빌드 및 테스트

```bash
# 빌드 및 테스트 스크립트 실행
./scripts/build-and-test.sh

# 또는 수동으로 실행
docker build --target production -t devops-demo:latest .
docker run --rm devops-demo:latest python -c "import flask; print('Success')"
```

### 3. 로컬 Kubernetes 테스트

```bash
# 로컬 Kubernetes 클러스터 시작 (Docker Desktop, Minikube, 또는 Kind)
# 예: Docker Desktop에서 Kubernetes 활성화

# Kubernetes 테스트 스크립트 실행
./scripts/local-k8s-test.sh

# 또는 수동으로 배포
kubectl apply -f k8s/development/
kubectl port-forward -n development service/devops-demo-service 8000:8000
```

### 4. GitHub Actions 파이프라인 실행

```bash
# 코드 푸시하여 파이프라인 트리거
git add .
git commit -m "Update application"
git push origin develop
```

## 📁 Project Structure

```
├── .github/
│   └── workflows/
│       ├── enterprise-deployment.yml  # Main CI/CD pipeline
│       └── deploy-to-local-k8s.yml   # Local K8s deployment
├── src/                       # Application source code
├── infrastructure/            # Terraform configurations
├── requirements.txt           # Base Python dependencies
├── requirements-py39.txt      # Python 3.9 compatible dependencies
├── requirements-py310.txt     # Python 3.10 compatible dependencies
├── requirements-py311.txt     # Python 3.11 compatible dependencies
├── requirements-dev.txt       # Development dependencies
└── Dockerfile                # Container configuration
```

## 🛠️ Technologies Used

- **GitHub Actions**: CI/CD automation
- **Python**: Application development
- **Docker**: Containerization
- **Terraform**: Infrastructure as Code
- **Kubernetes**: Container orchestration
- **Security Tools**: Snyk, OWASP ZAP, Trivy

## 🚦 Getting Started

1. Fork this repository
2. Enable GitHub Actions in your fork
3. Configure required secrets (see Security section)
4. Push changes to trigger workflows

## 📦 Dependency Management

This project uses Python version-specific dependency files to ensure compatibility across different Python versions:

- **requirements-py39.txt**: Python 3.9 compatible dependencies
- **requirements-py310.txt**: Python 3.10 compatible dependencies  
- **requirements-py311.txt**: Python 3.11 compatible dependencies

The CI/CD pipeline automatically selects the appropriate dependency file based on the Python version being tested.

### Python Version Compatibility

Some dependencies have specific version requirements based on Python version support:

- **pytest-postgresql**: 
  - Python 3.9/3.10: `>=6.0.0,<7.0.0` (stable 6.x series)
  - Python 3.11+: `>=7.0.0` (latest 7.x series with Python 3.11+ support)

This ensures that all dependencies work correctly across the supported Python versions without compatibility issues.

## 🔐 Security

This project includes comprehensive security scanning:
- Dependency vulnerability analysis
- Container security scanning
- Code security analysis
- Infrastructure security validation

## 📊 Monitoring & Reporting

- Automated test reporting
- Security scan results
- Performance metrics
- Deployment status tracking

## 🌍 Multi-Environment Support

- Development
- Staging
- Production

Each environment has its own deployment pipeline with appropriate security controls.

## 📈 Performance Features

- Matrix builds for parallel testing
- Caching for faster builds
- Optimized Docker layers
- Efficient dependency management

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Ensure all tests pass
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

---

*This project demonstrates the DevOps expertise required for senior-level positions, showcasing automation, security, scalability, and best practices.* 