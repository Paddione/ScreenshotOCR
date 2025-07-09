# CI/CD Pipeline Documentation

## 📋 Overview

This document describes the comprehensive CI/CD pipeline for the ScreenshotOCR system. The pipeline is built using GitHub Actions and provides automated testing, building, security scanning, and deployment capabilities.

## 🏗️ Pipeline Architecture

### Workflow Triggers
- **Push events**: `main` and `develop` branches
- **Pull requests**: Against `main` and `develop` branches  
- **Scheduled runs**: Daily at 2 AM UTC
- **Manual triggers**: Workflow dispatch

### Pipeline Stages
1. **Frontend Testing** - React component and service tests
2. **Backend Testing** - Python API and OCR service tests
3. **Existing Test Suite** - Integration with current testing infrastructure
4. **Security Scanning** - Vulnerability and secret detection
5. **Docker Build** - Container image building and registry push
6. **Integration Testing** - End-to-end system validation
7. **Performance Testing** - Load and performance benchmarks
8. **Deployment** - Production and staging deployments
9. **Cleanup** - Artifact and resource cleanup

## 🚀 Pipeline Jobs

### 1. Frontend Tests (`frontend-tests`)
**Purpose**: Test React application components and services
**Duration**: ~3-5 minutes

**Steps**:
- Node.js 18 setup with npm caching
- Dependency installation (`npm ci`)
- ESLint code linting
- Jest test execution with coverage
- React application build
- Coverage upload to Codecov
- Build artifact storage

**Artifacts**: 
- `frontend-build` - Production build files
- Coverage reports

### 2. Backend Tests (`backend-tests`)
**Purpose**: Test Python API and OCR services
**Duration**: ~5-8 minutes

**Services**:
- PostgreSQL 15 (test database)
- Redis 7 (test cache/queue)

**Steps**:
- Python 3.11 setup with pip caching
- System dependencies (Tesseract OCR)
- Python dependency installation
- API service tests with pytest
- OCR service tests with pytest
- Coverage upload to Codecov

**Environment Variables**:
- `DATABASE_URL`: Test database connection
- `REDIS_URL`: Test Redis connection
- `JWT_SECRET_KEY`: Test JWT secret
- `OPENAI_API_KEY`: API key for AI services

### 3. Existing Test Suite (`existing-tests`)
**Purpose**: Run legacy test infrastructure
**Duration**: ~2-3 minutes

**Steps**:
- Node.js and Python setup
- Test dependency installation
- Existing test suite execution
- Test result artifact upload

**Artifacts**:
- `existing-test-results` - JSON test results

### 4. Security Scanning (`security-scan`)
**Purpose**: Identify vulnerabilities and security issues
**Duration**: ~2-4 minutes

**Tools**:
- **Trivy**: Filesystem vulnerability scanning
- **TruffleHog**: Secret detection scanning

**Steps**:
- Trivy vulnerability scan
- SARIF report upload to GitHub Security
- Secret scanning with TruffleHog

**Outputs**:
- Security advisories in GitHub Security tab
- SARIF reports for code analysis

### 5. Docker Build (`docker-build`)
**Purpose**: Build and push container images
**Duration**: ~8-12 minutes
**Strategy**: Matrix build for multiple services

**Services Built**:
- `api` - FastAPI backend service
- `ocr` - OCR processing service  
- `web` - React frontend service

**Steps**:
- Docker Buildx setup
- GitHub Container Registry login
- Metadata extraction for tagging
- Multi-platform image build and push
- Build cache optimization

**Registry**: `ghcr.io/username/screenshotocr-{service}`

### 6. Integration Tests (`integration-tests`)
**Purpose**: End-to-end system validation
**Duration**: ~5-10 minutes
**Dependencies**: `docker-build`

**Steps**:
- Test environment configuration
- Docker Compose system startup
- Health check validation
- Integration test execution
- System log collection
- Environment cleanup

**Artifacts**:
- `integration-logs` - Complete system logs

### 7. Performance Tests (`performance-tests`)
**Purpose**: System performance benchmarking
**Duration**: ~5-8 minutes
**Trigger**: Scheduled runs and main branch pushes

**Steps**:
- Test environment setup
- Performance benchmark execution
- Results collection and analysis

**Artifacts**:
- `performance-results` - Performance metrics

### 8. Production Deployment (`deploy-production`)
**Purpose**: Deploy to production environment
**Duration**: ~3-5 minutes
**Trigger**: Push to `main` branch
**Dependencies**: `integration-tests`, `security-scan`

**Steps**:
- SSH connection to production server
- Code deployment via git pull
- System rebuild with `./rebuild.sh`
- Health check validation
- Slack notification (success/failure)

**Required Secrets**:
- `PRODUCTION_HOST`: Server hostname
- `PRODUCTION_USER`: SSH username
- `PRODUCTION_SSH_KEY`: SSH private key
- `SLACK_WEBHOOK_URL`: Notification webhook

### 9. Staging Deployment (`deploy-staging`)
**Purpose**: Deploy to staging environment
**Duration**: ~2-3 minutes
**Trigger**: Push to `develop` branch
**Dependencies**: `integration-tests`, `security-scan`

**Steps**:
- Staging environment deployment
- Staging test execution

### 10. Cleanup (`cleanup`)
**Purpose**: Resource and artifact cleanup
**Duration**: ~1-2 minutes
**Trigger**: Always runs after deployments

**Steps**:
- Old artifact cleanup (keeps latest 5)
- Resource optimization

## 🔧 Configuration

### Environment Variables
```yaml
env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```

### Required Secrets
```yaml
secrets:
  OPENAI_API_KEY: "sk-..."           # OpenAI API access
  PRODUCTION_HOST: "10.0.0.44"      # Production server
  PRODUCTION_USER: "patrick"        # SSH username
  PRODUCTION_SSH_KEY: "-----BEGIN..." # SSH private key
  SLACK_WEBHOOK_URL: "https://..."   # Slack notifications
```

### Service Configuration
```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: screenshotocr
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: screenshotocr_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

  redis:
    image: redis:7
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## 📊 Pipeline Metrics

### Success Criteria
- **Test Coverage**: >70% for all services
- **Security Scans**: No critical vulnerabilities
- **Performance**: <5s API response times
- **Build Time**: <15 minutes total pipeline
- **Deployment**: <5 minutes downtime

### Monitoring
- **GitHub Actions**: Workflow status and logs
- **Codecov**: Coverage trending and reports
- **Security**: GitHub Security advisories
- **Slack**: Deployment notifications
- **Production**: Health check monitoring

## 🚨 Troubleshooting

### Common Issues

#### 1. Test Failures
**Symptoms**: Tests fail intermittently
**Solutions**:
- Check service dependencies (PostgreSQL, Redis)
- Verify environment variables
- Review test logs for specific errors
- Ensure test data consistency

#### 2. Build Failures
**Symptoms**: Docker builds fail
**Solutions**:
- Check Dockerfile syntax
- Verify build context
- Review dependency versions
- Clear build cache if needed

#### 3. Deployment Issues
**Symptoms**: Production deployment fails
**Solutions**:
- Verify SSH key permissions
- Check server disk space
- Review deployment logs
- Validate production environment

#### 4. Security Scan Failures
**Symptoms**: Security scans block pipeline
**Solutions**:
- Review vulnerability reports
- Update vulnerable dependencies
- Add exceptions for false positives
- Implement security fixes

### Debug Commands
```bash
# Local test execution
cd web && npm test
cd api && python -m pytest
cd OCR && python -m pytest

# Local Docker build
docker build -t test-api ./api
docker build -t test-ocr ./OCR
docker build -t test-web ./web

# Local integration test
docker-compose up -d
curl -f http://localhost/api/health
```

## 🔒 Security Considerations

### Security Scanning
- **Trivy**: Scans for known vulnerabilities
- **TruffleHog**: Detects committed secrets
- **SARIF**: Structured security reporting

### Secret Management
- Secrets stored in GitHub repository settings
- No secrets in code or configuration files
- Rotation schedule for sensitive credentials

### Access Control
- Branch protection rules
- Required status checks
- Administrator approval for sensitive changes

## 🚀 Deployment Strategy

### Environments
- **Development**: Local development environment
- **Staging**: `develop` branch auto-deployment
- **Production**: `main` branch auto-deployment

### Deployment Process
1. **Code Review**: Pull request review process
2. **Testing**: Comprehensive test execution
3. **Security**: Security scan validation
4. **Build**: Container image creation
5. **Integration**: End-to-end validation
6. **Deploy**: Production deployment
7. **Verify**: Health check validation
8. **Notify**: Team notification

### Rollback Strategy
- **Automatic**: Health check failures trigger alerts
- **Manual**: SSH access for emergency rollback
- **Database**: Backup and restore procedures
- **Monitoring**: Real-time system monitoring

## 📈 Performance Optimization

### Build Optimization
- **Docker Layer Caching**: Reduces build times
- **Dependency Caching**: npm and pip cache
- **Parallel Jobs**: Matrix builds for services
- **Artifact Reuse**: Build artifact sharing

### Test Optimization
- **Parallel Execution**: Multiple test jobs
- **Test Categorization**: Unit, integration, performance
- **Smart Triggering**: Only relevant tests run
- **Coverage Caching**: Incremental coverage

## 🔮 Future Enhancements

### Planned Improvements
1. **Multi-Environment**: Staging environment setup
2. **Blue-Green Deployment**: Zero-downtime deployments
3. **Canary Releases**: Gradual rollout strategy
4. **Monitoring Integration**: Prometheus/Grafana setup
5. **Chaos Engineering**: Fault injection testing

### Advanced Features
- **Auto-scaling**: Dynamic resource allocation
- **Feature Flags**: Gradual feature rollout
- **A/B Testing**: User experience testing
- **Disaster Recovery**: Backup and restore automation

## 📚 Resources

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Jest Testing Framework](https://jestjs.io/)
- [Python Testing with pytest](https://docs.pytest.org/)

### Tools
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Trivy Security Scanner](https://aquasecurity.github.io/trivy/)
- [TruffleHog Secret Scanner](https://github.com/trufflesecurity/trufflehog)
- [Codecov Coverage Reports](https://codecov.io/)

---

For questions about the CI/CD pipeline or to request changes, please create an issue in the project repository or contact the development team. 