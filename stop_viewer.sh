#!/bin/bash
# Stop the coloring page viewer web server

if [ -f http_server.pid ]; then
    PID=$(cat http_server.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping web server (PID: $PID)..."
        kill $PID
        rm http_server.pid
        echo "✓ Web server stopped"
    else
        echo "Web server not running (stale PID file)"
        rm http_server.pid
    fi
else
    echo "No web server running (no PID file found)"
fi
