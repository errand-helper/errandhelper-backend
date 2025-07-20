# Docker Setup for Chat Features

This document describes the Docker configuration for the ErrandHelper backend with real-time chat functionality.

## Architecture Overview

The application uses a multi-service Docker architecture:

- **PostgreSQL Database** (`db`) - Main application database
- **Redis** (`redis_db`) - Message broker for WebSocket connections and caching
- **HTTP Server** (`errandhelper`) - Django REST API server using Gunicorn (WSGI)
- **WebSocket Server** (`errandhelper-websocket`) - Django Channels server using Daphne (ASGI)
- **Nginx Proxy** (`admin-proxy`) - Reverse proxy handling HTTP and WebSocket requests

## Services Configuration

### Database Service
- **Image**: `postgres:17`
- **Port**: `5432`
- **Volume**: `postgres_data` for persistent storage

### Redis Service
- **Image**: `redis:7-alpine`
- **Port**: `6379`
- **Volume**: `redis_data` for persistent storage
- **Configuration**: Append-only mode enabled for durability

### HTTP Server (Django WSGI)
- **Container**: `errandhelper-backend`
- **Port**: `8000`
- **Purpose**: Handles REST API requests
- **Server**: Gunicorn with 3 workers
- **Dependencies**: Database and Redis

### WebSocket Server (Django ASGI)
- **Container**: `errandhelper-websocket`
- **Port**: `8002`
- **Purpose**: Handles WebSocket connections for real-time chat
- **Server**: Daphne ASGI server
- **Dependencies**: Database, Redis, and HTTP server

### Nginx Proxy
- **Port**: `80` (production) / `8080` (development)
- **Configuration**: 
  - `/ws/` → WebSocket server (port 8002)
  - `/` → HTTP server (port 8000)
  - `/static/` → Static files

## Running the Application

### Production Mode
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Development Mode
```bash
# Use development overrides with hot reload
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up --build

# Run specific services
docker-compose up db redis_db  # Start only database services
```

## Port Configuration

| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| PostgreSQL | 5432 | 5432 | Database connections |
| Redis | 6379 | 6379 | Cache and message broker |
| HTTP Server | 8000 | 8000 | REST API |
| WebSocket Server | 8002 | 8002 | WebSocket connections |
| Nginx Proxy | 80 | 80 (prod) / 8080 (dev) | Main entry point |

## WebSocket Connection

### Production
Connect to WebSocket at: `ws://localhost/ws/chat/<room_id>/`

### Development
Connect to WebSocket at: `ws://localhost:8080/ws/chat/<room_id>/`

## Environment Variables

Ensure your `.env` file includes:

```bash
# Database
POSTGRES_DB=docker_django
POSTGRES_USER=db_user
POSTGRES_PASSWORD=your_db_password

# Redis
REDIS_URL=redis://redis_db:6379/0

# Django
DEBUG=False
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1

# WebSocket
WEBSOCKET_PORT=8002
```

## Troubleshooting

### Check Service Status
```bash
docker-compose ps
docker-compose logs [service-name]
```

### Redis Connection Issues
```bash
# Test Redis connectivity
docker-compose exec redis_db redis-cli ping

# Check Redis logs
docker-compose logs redis_db
```

### WebSocket Connection Issues
```bash
# Check WebSocket server logs
docker-compose logs errandhelper-websocket

# Test WebSocket server directly
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8002/ws/chat/test/
```

### Database Migrations
```bash
# Run migrations manually
docker-compose exec errandhelper python manage.py migrate

# Create superuser
docker-compose exec errandhelper python manage.py createsuperuser
```

## Security Considerations

- The configuration uses non-root users in containers
- Redis runs with append-only mode for data durability
- Nginx handles SSL termination (configure for production)
- WebSocket connections require JWT authentication

## Scaling

To scale WebSocket servers:
```bash
docker-compose up --scale errandhelper-websocket=3
```

Note: You'll need to update the nginx configuration for load balancing across multiple WebSocket servers.
