#!/usr/bin/env bash

# Set Django settings module
export DJANGO_SETTINGS_MODULE=configs.settings

# Wait for the HTTP server to be ready (migrations, etc.)
echo "Waiting for HTTP server to be ready..."
sleep 10

# Start the ASGI server with Daphne for WebSocket support
echo "Starting WebSocket server (ASGI)..."
echo "Django settings module: $DJANGO_SETTINGS_MODULE"

# Start Daphne (Django setup happens in asgi.py)
python -m daphne --bind 0.0.0.0 --port ${WEBSOCKET_PORT:-8002} configs.asgi:application
