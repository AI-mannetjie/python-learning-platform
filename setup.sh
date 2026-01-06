#!/bin/bash

# Setup script for Python Learning Platform
# This script helps set up the platform quickly

set -e

echo "=================================="
echo "Python Learning Platform Setup"
echo "=================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate random secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-20)
    
    # Update .env with generated secrets
    sed -i.bak "s/changeme123/$DB_PASSWORD/g" .env
    sed -i.bak "s/your-secret-key-change-in-production-min-32-chars/$SECRET_KEY/g" .env
    sed -i.bak "s/jwt-secret-key-change-in-production-min-32-chars/$JWT_SECRET_KEY/g" .env
    rm .env.bak
    
    echo "✅ .env file created with secure random secrets"
else
    echo "ℹ️  .env file already exists, skipping creation"
fi

echo ""
echo "🚀 Building and starting services..."
echo ""

# Build and start services
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if backend is ready
echo ""
echo "🔍 Checking backend health..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost/api/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend failed to start. Check logs with: docker-compose logs backend"
    exit 1
fi

# Run database migrations
echo ""
echo "🗄️  Setting up database migrations..."

# Check if migrations directory exists, if not initialize it
if docker-compose exec -T backend test -d migrations; then
    echo "Migrations directory exists, running upgrade..."
    docker-compose exec -T backend flask db upgrade
else
    echo "Initializing migrations for the first time..."
    docker-compose exec -T backend flask db init
    docker-compose exec -T backend flask db migrate -m "Initial migration"
    docker-compose exec -T backend flask db upgrade
fi

# Seed the database with sample data
echo ""
echo "🌱 Seeding database with sample data..."
docker-compose exec -T backend python seed_db.py

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "🌐 Access the application at: http://localhost"
echo "📚 API documentation: http://localhost/api"
echo "🏥 Health check: http://localhost/api/health"
echo ""
echo "📖 Next steps:"
echo "   1. Visit http://localhost to access the platform"
echo "   2. Register a new account"
echo "   3. Start learning Python!"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo ""
echo "📄 For more information, see README.md"
echo ""
