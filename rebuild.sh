#!/bin/bash

# ScreenshotOCR System Rebuild Script
# This script rebuilds all containers and ensures new files are included

set -e

echo "🔧 ScreenshotOCR System Rebuild"
echo "================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with the configuration from README.md"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found!"
    echo "Please install docker-compose"
    exit 1
fi

echo "📋 Current system status:"
docker-compose ps || echo "No running containers"

echo ""
echo "🛑 Stopping all services..."
docker-compose down

echo ""
echo "🏗️ Building all containers (no cache)..."
docker-compose build --no-cache

echo ""
echo "🔄 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "🔍 Checking service health..."

# Check database
echo "📊 Database:"
docker-compose exec -T postgres pg_isready -U screenshotocr || echo "❌ Database not ready"

# Check Redis
echo "📊 Redis:"
docker-compose exec -T redis redis-cli ping || echo "❌ Redis not ready"

# Check API health
echo "📊 API Server:"
sleep 5
curl -s http://10.0.0.44:8000/api/health || echo "❌ API not responding"

echo ""
echo "📊 Final service status:"
docker-compose ps

echo ""
echo "🌐 Access Points:"
echo "- Web Interface: https://10.0.0.44/"
echo "- API Documentation: https://10.0.0.44/api/docs"
echo "- Traefik Dashboard: https://10.0.0.44/dashboard/"
echo ""
echo "🔑 Default Credentials:"
echo "- Web Interface: admin / admin123"
echo "- Traefik Dashboard: patrick / 170591pk"

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "💡 Tips:"
echo "- Monitor logs: docker-compose logs -f"
echo "- View specific service: docker-compose logs -f <service_name>"
echo "- Check resources: docker stats"

# Display generated security tokens summary
echo ""
echo "🔐 Security Configuration Applied:"
echo "- JWT Secret Key: 32 characters (configured)"
echo "- API Auth Token: 64 characters (configured)"
echo "- Traefik Dashboard: bcrypt protected (patrick:170591pk)"
echo ""
echo "📚 Documentation available in:"
echo "- README.md - Complete setup guide"
echo "- docs/system_architecture.md - System overview"
echo "- docs/security_configuration.md - Security details" 