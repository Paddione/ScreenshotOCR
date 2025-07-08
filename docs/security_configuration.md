# Security Configuration Guide

## 🔐 Generated Security Tokens

This document contains the cryptographically secure tokens generated for the ScreenshotOCR system.

### JWT Secret Key
```
u0SIBDV5qaHJhqNTItRocnx6G81c32OD
```
- **Length**: 32 characters
- **Purpose**: JWT token signing and validation
- **Usage**: API authentication and session management
- **Security**: Cryptographically secure random generation

### Traefik Dashboard Authentication
```
patrick:$2b$12$d0LxOQK0ew0VeLzrzFN3nutt8E5FQRFx0yWHPMlwAYR1mPcHZUkHG
```
- **Username**: patrick
- **Password**: 170591pk
- **Hash Type**: bcrypt with salt rounds 12
- **Purpose**: Traefik dashboard access protection

### API Authentication Token
```
8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df
```
- **Length**: 64 characters
- **Purpose**: Client API authentication
- **Usage**: Screenshot upload and external API calls
- **Security**: High entropy for maximum security

## 🛡️ Security Implementation

### JWT Authentication Flow
1. User submits credentials to `/api/auth/login`
2. API validates credentials using bcrypt
3. JWT token generated with 32-char secret
4. Token returned to client for subsequent requests
5. All protected endpoints validate JWT signature

### API Token Usage
Client applications use the API token for authentication:
```bash
curl -H "Authorization: Bearer 8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df" \
     -F "image=@screenshot.png" \
     https://10.0.0.44/api/screenshot
```

### Password Security
- All passwords hashed using bcrypt with 12 salt rounds
- Rainbow table attacks prevented by unique salts
- Timing attack resistance built into bcrypt algorithm

## 🔑 Environment Configuration

### Complete .env Configuration
```bash
# JWT Configuration
JWT_SECRET_KEY=u0SIBDV5qaHJhqNTItRocnx6G81c32OD

# Traefik Dashboard Authentication
TRAEFIK_DASHBOARD_PASSWORD=patrick:$2b$12$d0LxOQK0ew0VeLzrzFN3nutt8E5FQRFx0yWHPMlwAYR1mPcHZUkHG

# API Authentication Token
API_AUTH_TOKEN=8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df

# Database Configuration
POSTGRES_USER=screenshotocr
POSTGRES_PASSWORD=K2Jw5ea7n5lwlpLANE2bpOYyUJlgPTCC
POSTGRES_DB=screenshotocr

# Domain and SSL Configuration
DOMAIN=10.0.0.44
LETSENCRYPT_EMAIL=patrick@example.com

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration
REDIS_URL=redis://redis:6379
```

## 🔒 Security Best Practices

### Token Management
1. **Rotation**: Rotate API tokens regularly
2. **Storage**: Never commit tokens to version control
3. **Access**: Limit token access to necessary systems only
4. **Monitoring**: Log token usage for security auditing

### Password Policies
1. **Strength**: Enforce strong password requirements
2. **Expiration**: Implement password expiration policies
3. **History**: Prevent password reuse
4. **Multi-Factor**: Consider 2FA for administrative accounts

### SSL/TLS Configuration
1. **Certificates**: Automatic Let's Encrypt renewal
2. **Protocols**: TLS 1.2+ only via Traefik
3. **Ciphers**: Strong cipher suites configured
4. **HSTS**: HTTP Strict Transport Security enabled

## 🚨 Security Incident Response

### Token Compromise
If any security token is compromised:

1. **Immediate Actions**:
   - Generate new tokens using the provided scripts
   - Update .env configuration
   - Restart all services
   - Revoke compromised tokens

2. **Generate New Tokens**:
   ```bash
   python3 -c "
   import secrets
   import string
   import bcrypt
   
   # New JWT Secret (32 chars)
   jwt_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
   print('New JWT_SECRET_KEY:', jwt_key)
   
   # New API Token (64 chars)
   api_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
   print('New API_AUTH_TOKEN:', api_token)
   "
   ```

3. **Update Configuration**:
   - Replace values in .env file
   - Rebuild containers: `docker-compose build`
   - Restart services: `docker-compose up -d`

### Password Reset
To change Traefik dashboard password:
```bash
python3 -c "
import bcrypt
password = 'NEW_PASSWORD'
salt = bcrypt.gensalt()
hash_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
print(f'patrick:{hash_pw.decode()}')
"
```

## 🔍 Security Monitoring

### Log Analysis
Monitor these security events:
- Failed authentication attempts
- Unusual API usage patterns
- Token validation failures
- Administrative access

### Key Metrics
- Authentication success/failure rates
- API endpoint access patterns
- SSL certificate status
- Database connection security

## 📋 Compliance Notes

### Data Protection
- User passwords never stored in plaintext
- JWT tokens contain no sensitive information
- API communications encrypted via TLS
- Database connections use encrypted channels

### Access Control
- Role-based access implemented
- JWT token expiration configured
- API rate limiting in place
- Administrative functions protected

---

**Important**: Keep this document secure and limit access to authorized personnel only. These tokens provide full system access and must be protected accordingly. 