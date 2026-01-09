#!/bin/bash
# Start the coloring page viewer with local web server

# Check if server is already running
if [ -f http_server.pid ] && kill -0 $(cat http_server.pid) 2>/dev/null; then
    echo "✓ Web server already running on port 8000"
    echo "  PID: $(cat http_server.pid)"
else
    echo "Starting web server on port 8000..."
    python3 -m http.server 8000 > /dev/null 2>&1 &
    echo $! > http_server.pid
    sleep 1
    echo "✓ Web server started (PID: $(cat http_server.pid))"
fi

echo ""
echo "Opening coloring page viewer..."
open http://localhost:8000/coloring_page_viewer.html

echo ""
echo "================================================"
echo "Coloring Page Viewer"
echo "================================================"
echo "URL: http://localhost:8000/coloring_page_viewer.html"
echo ""
echo "To stop the server:"
echo "  kill \$(cat http_server.pid)"
echo "  rm http_server.pid"
echo "================================================"
