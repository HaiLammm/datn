#!/bin/bash

# Script khởi động lại Socket.io Server
# Sử dụng: ./restart.sh

echo "🔄 Restarting Socket.io Server..."

# Dừng server
./stop.sh

# Chờ 1 giây
sleep 1

# Khởi động lại
./start.sh
