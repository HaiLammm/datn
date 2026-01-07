# 🚀 Hướng dẫn Khởi động Socket.io Server

## TL;DR - Khởi động nhanh nhất

```bash
cd /home/luonghailam/Projects/datn/socket-server
./start.sh
```

## Các lệnh chính

| Lệnh | Mô tả |
|------|-------|
| `./start.sh` | Khởi động server |
| `./stop.sh` | Dừng server |
| `./restart.sh` | Khởi động lại server |
| `tail -f /tmp/socket-server.log` | Xem log real-time |
| `lsof -i :3001` | Kiểm tra server đang chạy |

## Các cách khởi động

### ✅ Cách 1: Sử dụng Script (KHUYẾN NGHỊ)

```bash
cd socket-server
./start.sh
```

**Output mong đợi:**
```
🚀 Starting Socket.io Server...
✅ Khởi động server trên port 3001...
✅ Socket.io Server đang chạy (PID: 12345)
📋 Xem log: tail -f /tmp/socket-server.log
🛑 Dừng server: kill 12345
```

### Cách 2: Khởi động thủ công (Background)

```bash
cd socket-server
node server.js > /tmp/socket-server.log 2>&1 &
```

### Cách 3: Khởi động với log trực tiếp (Foreground)

```bash
cd socket-server
node server.js
```

**Ưu điểm:** Thấy log ngay trong terminal  
**Nhược điểm:** Terminal bị "khóa", phải mở terminal khác

## Kiểm tra trạng thái

### Kiểm tra server đang chạy:
```bash
lsof -i :3001
```

**Output nếu đang chạy:**
```
COMMAND     PID        USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
MainThrea 51580 luonghailam   21u  IPv6 206266      0t0  TCP *:3001 (LISTEN)
```

**Output nếu không chạy:**
```
(không có output hoặc "Port 3001 is not in use")
```

### Kiểm tra process:
```bash
ps aux | grep "node server.js" | grep -v grep
```

### Xem log:
```bash
tail -f /tmp/socket-server.log
```

**Log mẫu khi khởi động thành công:**
```
[dotenv@17.2.3] injecting env (3) from .env
Socket.io server running on port 3001
Frontend URL: http://localhost:3000
Backend API URL: http://localhost:8000
```

### Kiểm tra tất cả 3 servers:
```bash
ps aux | grep -E "uvicorn|next dev|node server" | grep -v grep
```

**Output mong đợi:**
```
luongha+   7452  ... uvicorn app.main:app --reload          ← Backend
luongha+  31398  ... node .../next dev                      ← Frontend
luongha+  51580  ... node server.js                         ← Socket.io
```

## Dừng server

### Cách 1: Sử dụng script
```bash
cd socket-server
./stop.sh
```

### Cách 2: Thủ công
```bash
pkill -f "node server.js"
```

### Cách 3: Force kill (khi cách khác không work)
```bash
kill -9 $(lsof -ti :3001)
```

## Khởi động lại

```bash
cd socket-server
./restart.sh
```

Hoặc:
```bash
./stop.sh && sleep 1 && ./start.sh
```

## Troubleshooting

### ❌ Lỗi: "Port 3001 already in use"

**Nguyên nhân:** Server cũ vẫn đang chạy

**Giải pháp:**
```bash
# Dừng server cũ
./stop.sh

# Hoặc force kill
kill -9 $(lsof -ti :3001)

# Khởi động lại
./start.sh
```

### ❌ Lỗi: "Cannot find module"

**Nguyên nhân:** Chưa cài đặt dependencies

**Giải pháp:**
```bash
cd socket-server
npm install
./start.sh
```

### ❌ Lỗi: "Permission denied: ./start.sh"

**Nguyên nhân:** File script chưa có quyền thực thi

**Giải pháp:**
```bash
chmod +x start.sh stop.sh restart.sh
./start.sh
```

### ❌ Lỗi: "Connection refused" từ frontend

**Kiểm tra:**
1. Server có đang chạy không?
   ```bash
   lsof -i :3001
   ```

2. Backend có đang chạy không? (Socket server cần backend để verify JWT)
   ```bash
   lsof -i :8000
   ```

3. Xem log để tìm lỗi:
   ```bash
   tail -50 /tmp/socket-server.log
   ```

### ❌ Frontend báo "Authentication token not found"

**Đã fix!** Lỗi này đã được khắc phục bằng cách:
- Tạo `frontend/lib/auth-actions.ts` với Server Action
- Không đọc cookie từ client-side nữa
- Token được fetch từ server và pass qua props

**Kiểm tra lại:** Xóa cache browser và reload trang

## Thông tin quan trọng

- **Port:** 3001
- **Log file:** `/tmp/socket-server.log`
- **Config file:** `socket-server/.env`
- **Dependencies:** Express, Socket.io, CORS, Axios

## Environment Variables

File `.env` (đã có sẵn):
```env
PORT=3001
FRONTEND_URL=http://localhost:3000
BACKEND_API_URL=http://localhost:8000
```

## Testing

### Test Socket.io connection:
```bash
cd /home/luonghailam/Projects/datn
node test-socket-cli.js
```

### Test trong browser:
1. Mở `http://localhost:3000/test-socket`
2. Kiểm tra console log
3. Gửi tin nhắn test

### Test flow hoàn chỉnh:
1. Đăng nhập với role `recruiter`
2. Vào `/jobs/jd/{jdId}/applicants`
3. Click "Start Chat" với một candidate
4. Nhập tin nhắn → Modal hiện lên
5. Click "Send Message"
6. Trang chuyển đến `/messages/{conversationId}`
7. Kiểm tra status "Connected" ở góc phải
8. Gửi tin nhắn thử

## Socket.io Events

### Client gửi lên Server:
- `join-conversation` - Tham gia phòng chat
- `send-message` - Gửi tin nhắn
- `start-typing` - Bắt đầu gõ
- `stop-typing` - Dừng gõ

### Server gửi xuống Client:
- `new-message` - Tin nhắn mới
- `conversation-updated` - Cập nhật conversation
- `user-typing` - User đang gõ
- `user-stopped-typing` - User dừng gõ
- `error` - Có lỗi xảy ra

## Liên hệ

Nếu gặp vấn đề không giải quyết được, kiểm tra:
- Story 7.1: `_bmad-output/planning-artifacts/stories/7.1.story.md`
- Coding Standards: `_bmad-output/planning-artifacts/architecture/coding-standards.md`
- Socket Server README: `socket-server/README.md`
