# Traefik Routing Configuration Diagram

## Current Routing Setup

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            Internet Traffic Flow                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

Internet User → web.korczewski.de:443 (HTTPS)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        Traefik Reverse Proxy                                      │
│                      (Running on your server)                                     │
│                                                                                     │
│  Entry Points:                                                                     │
│  • Port 80  (HTTP)  → Redirect to HTTPS + Let's Encrypt challenge                 │
│  • Port 443 (HTTPS) → SSL termination + routing                                   │
│                                                                                     │
│  SSL Certificate:                                                                  │
│  • Provider: Let's Encrypt                                                        │
│  • Domain: web.korczewski.de                                                      │
│  • Email: patrick@korczewski.de                                                   │
│  • Auto-renewal: Yes                                                              │
└─────────────────────────────┬───────────────────────────────────────────────────────┘
                              │
                              │ Dynamic routing rules
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            Routing Logic                                           │
│                                                                                     │
│  Rule: Host(`web.korczewski.de`)                                                   │
│  ├─ Entry Point: websecure (port 443)                                             │
│  ├─ Service: external-web-service                                                 │
│  ├─ TLS: letsencrypt certificate resolver                                         │
│  └─ Middleware: secure-headers                                                    │
│                                                                                     │
│  Security Headers Applied:                                                        │
│  • X-Frame-Options: DENY                                                          │
│  • X-Content-Type-Options: nosniff                                                │
│  • X-XSS-Protection: 1; mode=block                                                │
│  • Strict-Transport-Security: max-age=63072000; includeSubDomains; preload       │
│  • X-Forwarded-Proto: https                                                       │
└─────────────────────────────┬───────────────────────────────────────────────────────┘
                              │
                              │ Load balancer forwards to
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        External Web Service                                       │
│                         (Your Application)                                        │
│                                                                                     │
│  Target: 10.0.0.44:8000                                                           │
│  Protocol: HTTP (internal)                                                        │
│  Service Name: external-web-service                                               │
│                                                                                     │
│  Note: SSL is terminated at Traefik,                                              │
│        so your application receives plain HTTP                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘

## Configuration Files Modified

### 1. traefik/dynamic.yml
```yaml
http:
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

  services:
    external-web-service:
      loadBalancer:
        servers:
          - url: "http://10.0.0.44:8000"
```

### 2. Environment Variables (.env)
```env
DOMAIN=10.0.0.44
WEBDOMAIN=web.korczewski.de
LETSENCRYPT_EMAIL=patrick@korczewski.de
```

## Traffic Flow Summary

1. **User Request**: `https://web.korczewski.de` → Your server's IP
2. **Traefik Entry**: Request hits Traefik on port 443
3. **SSL Termination**: Traefik handles SSL using Let's Encrypt certificate
4. **Route Matching**: Host header matches `web.korczewski.de`
5. **Security Headers**: Applied to protect against common attacks
6. **Load Balancing**: Forwarded to `10.0.0.44:8000` via HTTP
7. **Response**: Your application response flows back through Traefik to user

## Verification Commands

```bash
# Check if services are running
docker-compose ps

# View Traefik logs
docker-compose logs traefik

# Test the routing (from external)
curl -I https://web.korczewski.de

# Check certificate
openssl s_client -connect web.korczewski.de:443 -servername web.korczewski.de
```

## Troubleshooting

### Certificate Issues
- Ensure DNS points to your server
- Port 80 must be accessible for HTTP challenge
- Check logs: `docker-compose logs traefik | grep acme`

### Routing Issues
- Verify `10.0.0.44:8000` is accessible from Traefik container
- Check service is running on port 8000
- Verify no firewall blocking port 8000

### Configuration Issues
- Validate YAML syntax in dynamic.yml
- Ensure .env file has correct values
- Restart Traefik after configuration changes: `docker-compose restart traefik`

## Security Features

✅ **SSL/TLS Encryption**: Automatic Let's Encrypt certificates
✅ **Security Headers**: HSTS, XSS protection, content type protection
✅ **HTTP to HTTPS Redirect**: Automatic for the domain
✅ **Certificate Auto-renewal**: Managed by Traefik
✅ **Modern TLS**: TLS 1.2+ with secure cipher suites 