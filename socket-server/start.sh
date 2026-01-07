#!/bin/bash

# Script khởi động Socket.io Server
# Sử dụng: ./start.sh

echo "🚀 Starting Socket.io Server..."

# Chuyển đến thư mục socket-server
cd "$(dirname "$0")"

# Dừng server cũ nếu đang chạy
if lsof -i :3001 > /dev/null 2>&1; then
    echo "⚠️  Port 3001 đang được sử dụng. Đang dừng server cũ..."
    pkill -f "node server.js"
    sleep 2
fi

# Kiểm tra file .env tồn tại
if [ ! -f .env ]; then
    echo "❌ Không tìm thấy file .env"
    echo "📝 Tạo file .env với nội dung:"
    echo "PORT=3001"
    echo "FRONTEND_URL=http://localhost:3000"
    echo "BACKEND_API_URL=http://localhost:8000"
    exit 1
fi

# Kiểm tra node_modules
if [ ! -d node_modules ]; then
    echo "📦 Cài đặt dependencies..."
    npm install
fi

# Khởi động server
echo "✅ Khởi động server trên port 3001..."
node server.js > /tmp/socket-server.log 2>&1 &

# Lấy PID
SOCKET_PID=$!
sleep 2

# Kiểm tra server đã khởi động thành công chưa
if ps -p $SOCKET_PID > /dev/null; then
    echo "✅ Socket.io Server đang chạy (PID: $SOCKET_PID)"
    echo "📋 Xem log: tail -f /tmp/socket-server.log"
    echo "🛑 Dừng server: kill $SOCKET_PID"
else
    echo "❌ Không thể khởi động server. Kiểm tra log:"
    cat /tmp/socket-server.log
    exit 1
fi
