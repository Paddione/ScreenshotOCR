# ScreenshotOCR - AI-Powered Screenshot Analysis System

A comprehensive, enterprise-grade system for capturing, processing, and analyzing screenshots using advanced OCR and AI technologies. This system provides automated screenshot analysis with intelligent text extraction and AI-powered content understanding.

## 🏗️ System Architecture

The ScreenshotOCR system is built as a microservices architecture with the following components:

### Core Services
- **Web Interface** (React 18) - Modern, responsive dashboard for managing analyses
- **API Server** (FastAPI) - High-performance REST API with async processing
- **OCR Processor** (Python + Tesseract) - Advanced image processing and text extraction
- **Storage Processor** (Python) - Dedicated database storage service
- **Windows Client** (PyQt5) - Desktop application for automated screenshot capture

### Infrastructure
- **Database** (PostgreSQL 15) - Persistent storage with optimized indexing
- **Redis** (v7) - High-performance job queue and caching layer
- **Traefik** (v3) - Reverse proxy with automatic SSL/TLS termination
- **Docker Compose** - Container orchestration with health checks

## 🔐 Security Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# JWT Configuration
JWT_SECRET_KEY=u0SIBDV5qaHJhqNTItRocnx6G81c32OD

# Traefik Dashboard Authentication
# User: patrick | Password: 170591pk
# Note: Dollar signs in bcrypt hash must be escaped with $$ for Docker Compose
TRAEFIK_DASHBOARD_PASSWORD=patrick:$$2b$$12$$d0LxOQK0ew0VeLzrzFN3nutt8E5FQRFx0yWHPMlwAYR1mPcHZUkHG

# API Authentication Token (for client API calls)
API_AUTH_TOKEN=8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df

# Database Configuration
POSTGRES_USER=screenshotocr
POSTGRES_PASSWORD=K2Jw5ea7n5lwlpLANE2bpOYyUJlgPTCC
POSTGRES_DB=screenshotocr

# Domain and SSL Configuration
DOMAIN=10.0.0.44
LETSENCRYPT_EMAIL=patrick@example.com

# OpenAI API Configuration
# Replace with your actual OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration
REDIS_URL=redis://redis:6379
```

### Security Features

- **JWT Authentication**: 32-character cryptographically secure secret key
- **Bcrypt Password Hashing**: Secure password storage for user accounts
- **API Token Authentication**: 64-character secure token for client API access
- **Traefik Dashboard Protection**: Bcrypt-hashed credentials for dashboard access
- **SSL/TLS Encryption**: Automatic Let's Encrypt certificate management

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Domain or IP address (configured for web.korczewski.de)

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd ScreenshotOCR
   ```

2. **Configure Environment** ⚠️ **REQUIRED**
   ```bash
   # Create .env file with the configuration from docs/security_configuration.md
   # Copy the complete configuration and replace your_openai_api_key_here with your actual API key
   ```
   
   **Important**: The `.env` file is essential for the system to work. See `docs/security_configuration.md` for the complete configuration.

3. **Build and Start Services**
   ```bash
   # Use the provided rebuild script (recommended)
   ./rebuild.sh
   
   # Or manually build and start
   docker-compose build
   docker-compose up -d

   # Check service status
   docker-compose ps
   ```

4. **Access the System**
   - Web Interface (Domain): `https://web.korczewski.de`
   - API Documentation (Domain): `https://web.korczewski.de/api/docs`
   - Traefik Dashboard: `https://web.korczewski.de/dashboard/`

### Default Credentials

- **Web Interface**: admin / admin123
- **Traefik Dashboard**: patrick / 170591pk

## 🚀 Core Functionality

### 1. **Screenshot Capture & Upload**
- **Windows Client Integration**: Automated screenshot capture via configurable hotkeys (Ctrl+S by default)
- **Web Upload Interface**: Drag-and-drop or click-to-upload functionality
- **API Integration**: RESTful endpoints for external application integration
- **Real-time Processing**: Immediate queuing and processing of uploaded images

### 2. **Advanced OCR Processing**
- **Multi-language Support**: German and English text recognition with automatic language detection
- **Image Preprocessing**: OpenCV-based enhancement for optimal OCR accuracy
  - Noise reduction and denoising
  - Contrast enhancement with CLAHE
  - Morphological operations for text clarity
- **Confidence Scoring**: Quality metrics for extracted text reliability
- **Tesseract Integration**: Industry-standard OCR engine with optimized configuration

### 3. **AI-Powered Analysis**
- **OpenAI GPT-4 Integration**: Advanced content understanding and analysis
- **Contextual Analysis**: Automatic identification of content type (documents, webpages, applications)
- **Actionable Insights**: Extraction of key information and next steps
- **Multi-language Response**: AI analysis in the same language as extracted text
- **Token Usage Tracking**: Cost monitoring and optimization

### 4. **User Management & Security**
- **JWT Authentication**: Secure, stateless authentication with 24-hour token expiration
- **Role-based Access Control**: Admin users can create and manage other users
- **Bcrypt Password Hashing**: Industry-standard password security with salt rounds
- **API Token Authentication**: Separate authentication system for client applications
- **Session Management**: Automatic token refresh and secure logout

### 5. **Data Organization & Management**
- **Folder System**: Hierarchical organization of analysis results
- **Response Management**: Full CRUD operations for analysis results
- **Search & Filter**: Advanced search across OCR text and AI analysis
- **Pagination**: Efficient handling of large datasets
- **Export Capabilities**: PDF generation for analysis reports

### 6. **Real-time Processing Pipeline**
```
Screenshot Upload → Redis Queue → OCR Processing → AI Analysis → Database Storage
```

## 📋 Service Components

### API Server (`/api`)
- **Framework**: FastAPI with async/await support and automatic API documentation
- **Authentication**: JWT tokens with bcrypt password hashing (12 salt rounds)
- **Database**: PostgreSQL with connection pooling and optimized queries
- **Features**: User management, folder organization, response storage, PDF export
- **Health Checks**: Comprehensive monitoring of database and Redis connections
- **Error Handling**: Structured error responses with detailed logging

### OCR Processor (`/OCR`)
- **Engine**: Tesseract OCR with multi-language support (German/English)
- **Image Processing**: OpenCV preprocessing pipeline for enhanced accuracy
- **AI Analysis**: OpenAI GPT-4 integration with intelligent prompt engineering
- **Queue Processing**: Redis-based job queue with retry mechanisms
- **Performance Monitoring**: Processing time and confidence metrics tracking

### Storage Processor (`/api`)
- **Dedicated Service**: Separate processor for database operations
- **Queue Management**: Handles storage_queue for reliable data persistence
- **Error Recovery**: Automatic retry mechanisms for failed storage operations
- **Data Validation**: Comprehensive validation before database insertion

### Web Interface (`/web`)
- **Framework**: React 18 with modern hooks and functional components
- **UI Library**: Lucide React icons with custom CSS styling
- **Authentication**: JWT token-based with automatic refresh
- **Features**: 
  - Interactive dashboard with statistics
  - Response management with search and filtering
  - Folder organization and management
  - File upload with drag-and-drop
  - PDF export functionality
- **Responsive Design**: Mobile-first approach with adaptive layouts

### Windows Client (`/Windows-Client`)
- **Framework**: PyQt5 for native Windows integration
- **Python Compatibility**: Updated for Python 3.13 support
- **Features**:
  - Global hotkey registration (customizable)
  - Active window screenshot capture
  - Automatic server communication
  - Offline queue for failed uploads
  - System tray integration
  - Configuration management UI
- **Screenshot Capture**: Win32 API integration for high-quality captures
- **Queue Management**: Background processing with retry logic
- **Installation**: Improved troubleshooting guide for Python 3.13

### Infrastructure
- **Traefik**: Reverse proxy with automatic Let's Encrypt SSL certificates
- **PostgreSQL**: Relational database with optimized indexes and foreign keys
- **Redis**: In-memory cache and job queue with persistence
- **Docker Compose**: Container orchestration with health checks and dependency management

## 🔧 Configuration Management

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for JWT token signing | 32-character random string |
| `TRAEFIK_DASHBOARD_PASSWORD` | Bcrypt hash for dashboard access | `user:$2b$12$hash...` |
| `API_AUTH_TOKEN` | Token for client API authentication | 64-character random string |
| `POSTGRES_*` | Database connection parameters | Standard PostgreSQL config |
| `DOMAIN` | Domain or IP for SSL certificates | `10.0.0.44` |
| `OPENAI_API_KEY` | OpenAI API key for AI analysis | `sk-...` |

### Service Ports

- **80/443**: HTTP/HTTPS (Traefik)
- **8080**: Traefik Dashboard
- **8000**: API Server (internal)
- **3000**: Web Interface (internal)
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)

## 🔄 Complete Workflow

### 1. **Screenshot Capture**
```
Windows Client (Hotkey) → Screenshot Capture → Server Upload → Redis Queue
     OR
Web Interface → File Upload → Server Processing → Redis Queue
```

### 2. **Processing Pipeline**
```
Redis Queue → OCR Processor → Image Preprocessing → Tesseract OCR → 
OpenAI Analysis → Storage Queue → Database Storage → Web Dashboard
```

### 3. **User Interaction**
```
Web Dashboard → View Responses → Search/Filter → Export PDF → 
Folder Management → User Administration
```

## 🛠️ Development

### Project Cleanup Completed

All duplicate files, unused components, and broken references have been removed. See `docs/file_cleanup.md` for details.

✅ **Cleaned up:**
- Removed 6 duplicate/unused files
- Fixed all broken file references  
- Verified all imports are valid
- Created missing favicon placeholder

### Docker Build Fixes Applied

All Dockerfile issues have been resolved:

✅ **Fixed Issues:**
- Dockerfile naming - Updated docker-compose.yml to reference correct DOCKERFILE files
- Requirements file naming - Fixed API and OCR services to use correct requirements files  
- Entry point references - Corrected API service to use api_main:app
- Missing React files - Created essential React files (index.html, manifest.json, etc.)
- npm compatibility - Changed from npm ci to npm install for web build

✅ **All services now build successfully:**
- API Service: FastAPI with proper entry point
- OCR Service: Tesseract with correct dependencies  
- Web Service: React with all required files
- Storage Service: Database operations

### Rebuilding Containers

When making changes to the codebase:

```bash
# Use the provided rebuild script (recommended)
./rebuild.sh

# Or manually rebuild specific service
docker-compose build api

# Rebuild all services
docker-compose build

# Restart with new builds
docker-compose up -d --force-recreate
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f ocr
```

### Database Management

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U screenshotocr -d screenshotocr

# Run database migrations
docker-compose exec api python -c "from database import Database; import asyncio; asyncio.run(Database().create_tables())"
```

## 📊 System Monitoring

### Health Checks

The system includes health checks for all critical services:
- Database connectivity
- Redis availability  
- API responsiveness
- OCR processor status

### Performance Monitoring

Monitor system performance through:
- Docker container stats: `docker stats`
- Application logs: `docker-compose logs`
- Traefik metrics: Available at dashboard

## 🔒 Security Best Practices

1. **Change Default Passwords**: Update admin credentials immediately
2. **Secure API Keys**: Keep OpenAI API key secure and rotate regularly
3. **SSL Certificates**: Ensure Let's Encrypt certificates are renewed automatically
4. **Network Security**: Use Docker networks for internal communication
5. **Regular Updates**: Keep base images and dependencies updated

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration (admin only)
- `GET /api/auth/me` - Get current user info

### Data Management Endpoints

- `GET /api/responses` - List user responses with pagination
- `GET /api/folders` - Manage response folders
- `POST /api/upload` - Manual image upload
- `GET /api/export/{id}/pdf` - Export response as PDF

### Client Integration

For client applications, use the API_AUTH_TOKEN for authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     -F "image=@screenshot.png" \
     https://10.0.0.44/api/screenshot
```

## 🐛 Troubleshooting

### Common Issues

1. **SSL Certificate Issues**: Check domain configuration and Let's Encrypt logs
2. **Database Connection**: Verify PostgreSQL container health and credentials
3. **OCR Processing**: Check Tesseract installation and language packs
4. **API Authentication**: Verify JWT secret key and token validity

### Support Commands

```bash
# Check service health
docker-compose ps
docker-compose exec api curl http://localhost:8000/api/health

# Reset database
docker-compose down -v
docker-compose up -d

# View container resources
docker stats $(docker ps --format "table {{.Names}}" | grep screenshot)
```

## 🔄 Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U screenshotocr screenshotocr > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U screenshotocr screenshotocr < backup.sql
```

### File Storage Backup

```bash
# Backup uploaded files
tar -czf uploads-backup.tar.gz ./data/uploads/
```

---

**Note**: This system is configured for dual access:
- **Local Access**: `10.0.0.44` for development and internal network access
- **Domain Access**: `web.korczewski.de` for external HTTPS access with proper SSL certificates

Both domains are automatically configured with SSL/TLS certificates via Let's Encrypt. Adjust domain settings in `.env` file for different deployment scenarios. 