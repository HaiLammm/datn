# Socket.io Server - Real-time Messaging

Server Socket.io cho tính năng chat real-time giữa Recruiter và Job Seeker.

## 🚀 Khởi động nhanh

### Cách 1: Sử dụng Script (Khuyến nghị)

```bash
# Khởi động server
./start.sh

# Dừng server
./stop.sh

# Khởi động lại
./restart.sh
```

### Cách 2: Khởi động thủ công

```bash
# Cài đặt dependencies (lần đầu tiên)
npm install

# Khởi động server (chạy ngầm)
node server.js > /tmp/socket-server.log 2>&1 &

# Hoặc khởi động với log trực tiếp
node server.js
```

## 📋 Yêu cầu

- Node.js >= 16.x
- NPM >= 8.x
- Backend FastAPI đang chạy trên `http://localhost:8000`
- Frontend Next.js đang chạy trên `http://localhost:3000`

## ⚙️ Cấu hình

File `.env`:
```env
PORT=3001
FRONTEND_URL=http://localhost:3000
BACKEND_API_URL=http://localhost:8000
```

## 🔍 Kiểm tra trạng thái

```bash
# Kiểm tra server đang chạy
lsof -i :3001

# Xem log
tail -f /tmp/socket-server.log

# Kiểm tra tất cả server
ps aux | grep -E "uvicorn|next dev|node server"
```

## 🛑 Dừng server

```bash
# Sử dụng script
./stop.sh

# Hoặc thủ công
pkill -f "node server.js"

# Force kill nếu cần
kill -9 $(lsof -ti :3001)
```

## 📡 Socket.io Events

### Client → Server:
- `join-conversation` - Tham gia phòng chat
- `send-message` - Gửi tin nhắn
- `start-typing` - Bắt đầu đánh máy
- `stop-typing` - Dừng đánh máy

### Server → Client:
- `new-message` - Nhận tin nhắn mới
- `conversation-updated` - Cập nhật danh sách conversation
- `user-typing` - Người dùng đang đánh máy
- `user-stopped-typing` - Người dùng dừng đánh máy
- `error` - Lỗi xảy ra

## 🔐 Authentication

Server sử dụng JWT authentication:
1. Client gửi token qua `socket.handshake.auth.token`
2. Server xác thực với FastAPI endpoint `/api/v1/messages/auth/verify`
3. Nếu hợp lệ, attach `userId`, `userRole`, `userName` vào socket
4. Nếu không hợp lệ, reject connection

## 📂 Cấu trúc thư mục

```
socket-server/
├── server.js           # Main server file
├── start.sh            # Script khởi động
├── stop.sh             # Script dừng server
├── restart.sh          # Script khởi động lại
├── .env                # Environment variables
├── package.json        # Dependencies
└── README.md           # Tài liệu này
```

## 🐛 Debug

### Server không khởi động:
```bash
# Kiểm tra port 3001 có bị chiếm không
lsof -i :3001

# Kiểm tra log lỗi
cat /tmp/socket-server.log

# Kiểm tra .env file
cat .env
```

### Client không kết nối được:
1. Kiểm tra server đang chạy: `lsof -i :3001`
2. Kiểm tra log server: `tail -f /tmp/socket-server.log`
3. Kiểm tra CORS trong console browser
4. Kiểm tra JWT token hợp lệ

### Tin nhắn không gửi được:
1. Kiểm tra backend FastAPI đang chạy
2. Kiểm tra endpoint `/api/v1/messages` hoạt động
3. Kiểm tra database connection
4. Xem log trong `/tmp/socket-server.log`

## 📝 Development

```bash
# Chạy với nodemon (auto-restart khi code thay đổi)
npm install -g nodemon
nodemon server.js

# Test connection
node ../test-socket-cli.js
```

## 🔗 Related Documentation

- Story 7.1: `/home/luonghailam/Projects/datn/_bmad-output/planning-artifacts/stories/7.1.story.md`
- Coding Standards: `/home/luonghailam/Projects/datn/_bmad-output/planning-artifacts/architecture/coding-standards.md`
- API Specification: `/home/luonghailam/Projects/datn/_bmad-output/planning-artifacts/architecture/api-specification.md`
