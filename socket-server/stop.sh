#!/bin/bash

# Script dừng Socket.io Server
# Sử dụng: ./stop.sh

echo "🛑 Stopping Socket.io Server..."

# Tìm và dừng tất cả node server.js
if pgrep -f "node server.js" > /dev/null; then
    pkill -f "node server.js"
    sleep 1
    echo "✅ Socket.io Server đã dừng"
else
    echo "ℹ️  Socket.io Server không chạy"
fi

# Kiểm tra lại
if lsof -i :3001 > /dev/null 2>&1; then
    echo "⚠️  Port 3001 vẫn được sử dụng. Đang force kill..."
    lsof -ti :3001 | xargs kill -9
    echo "✅ Đã force kill process trên port 3001"
else
    echo "✅ Port 3001 đã được giải phóng"
fi
