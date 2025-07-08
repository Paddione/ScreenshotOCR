# External Routing Configuration

## Overview

This document describes the configuration for routing the domain `web.korczewski.de` to an external service running at `10.0.0.44:8000` through Traefik with automatic SSL/TLS certificate provisioning via Let's Encrypt.

## Architecture Changes

The Traefik configuration has been updated to support external service routing while maintaining the existing ScreenshotOCR system routing:

```
web.korczewski.de (HTTPS) → Traefik → 10.0.0.44:8000 (HTTP)
```

## Configuration Components

### 1. Traefik Static Configuration (`traefik/traefik.yml`)

The static configuration includes:
- **Let's Encrypt Certificate Resolver**: Automatic SSL certificate provisioning
- **Email Configuration**: `patrick@korczewski.de` for Let's Encrypt notifications
- **Entry Points**: HTTP (port 80) and HTTPS (port 443)

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      httpChallenge:
        entryPoint: web
      email: patrick@korczewski.de
      storage: /letsencrypt/acme.json
```

### 2. Traefik Dynamic Configuration (`traefik/dynamic.yml`)

The dynamic configuration has been extended with:

#### External Service Router
```yaml
routers:
  web-korczewski-external:
    rule: "Host(`web.korczewski.de`)"
    entryPoints:
      - "websecure"
    service: "external-web-service"
    tls:
      certResolver: "letsencrypt"
    middlewares:
      - "secure-headers"
```

#### External Service Definition
```yaml
services:
  external-web-service:
          loadBalancer:
        servers:
          - url: "http://10.0.0.44:8000"
```

### 3. Environment Configuration

The `.env` file must include:

```env
# Domain and SSL Configuration
DOMAIN=10.0.0.44
WEBDOMAIN=web.korczewski.de
LETSENCRYPT_EMAIL=patrick@korczewski.de
```

## SSL/TLS Configuration

### Automatic Certificate Provisioning

- **Provider**: Let's Encrypt
- **Challenge Type**: HTTP Challenge (via port 80)
- **Storage**: `/letsencrypt/acme.json` (persistent volume)
- **Auto-renewal**: Managed by Traefik
- **Contact Email**: `patrick@korczewski.de`

### Security Headers

The external service benefits from the same security headers as the main application:

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HSTS) with preload
- `X-Forwarded-Proto: https`

## Routing Behavior

### Domain-based Routing

1. **`web.korczewski.de`** → External service at `10.0.0.44:8000`
   - **Protocol**: HTTPS with Let's Encrypt certificate
   - **Middleware**: Security headers applied
   - **Backend**: HTTP connection to 10.0.0.44:8000

2. **Other routes on `web.korczewski.de`** → ScreenshotOCR system (if configured)
   - `/api/*` → API service
   - `/dashboard/` → Traefik dashboard

### Load Balancing

The external service configuration supports:
- **Single backend server**: `10.0.0.44:8000`
- **Health checks**: Can be added if needed
- **Multiple servers**: Additional servers can be added for redundancy

## Deployment Process

### 1. Update Configuration Files

Ensure the following files are updated:
- `traefik/dynamic.yml` - External routing rules
- `env.example` - Environment template
- `.env` - Actual environment (create from template)

### 2. Deploy Changes

```bash
# Stop services
docker-compose down

# Rebuild and start
./rebuild.sh

# Or manually:
docker-compose up -d
```

### 3. Verify SSL Certificate

Check certificate provisioning:
```bash
# Check Traefik logs
docker-compose logs traefik

# Verify certificate in browser
# Visit https://web.korczewski.de
```

## Troubleshooting

### Common Issues

1. **Certificate not provisioning**:
   - Check DNS points to Traefik server
   - Verify port 80 is accessible for HTTP challenge
   - Check Traefik logs for ACME errors

2. **External service not reachable**:
   - Verify `10.0.0.44:8000` is accessible from Traefik container
   - Check network connectivity
   - Verify service is running on target port

3. **SSL redirect loops**:
   - Ensure backend service accepts HTTP traffic
   - Check X-Forwarded-Proto header handling

### Monitoring

Monitor the configuration through:
- **Traefik Dashboard**: `https://web.korczewski.de/dashboard/`
- **Container Logs**: `docker-compose logs traefik`
- **Certificate Status**: Check `/letsencrypt/acme.json`

## Security Considerations

### Network Security
- External traffic is terminated at Traefik (SSL/TLS)
- Backend communication is HTTP within secure network
- Security headers protect against common attacks

### Certificate Management
- Automatic renewal prevents expiration
- Certificates stored in persistent volume
- Email notifications for renewal issues

### Access Control
- No authentication required for external service
- Traefik dashboard remains protected with basic auth
- Rate limiting applied to prevent abuse

## Maintenance

### Regular Tasks

1. **Monitor certificate renewal**: Check logs monthly
2. **Update DNS records**: If IP changes
3. **Review security headers**: Update as needed
4. **Monitor external service**: Ensure availability

### Backup Considerations

- Backup `/letsencrypt/acme.json` for certificate recovery
- Document external service configuration
- Maintain configuration file backups

## Future Enhancements

Potential improvements:
- **Health checks** for external service
- **Multiple backend servers** for redundancy
- **Custom error pages** for service unavailability
- **Enhanced monitoring** and alerting
- **API Gateway features** like rate limiting per route 