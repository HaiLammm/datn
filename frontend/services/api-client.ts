import axios from 'axios';

// Lấy URL từ biến môi trường và đảm bảo nó trỏ đến đúng API version
const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  // BẮT BUỘC: Cho phép trình duyệt tự động gửi và nhận HttpOnly cookies
  // khi thực hiện request sang domain khác (vd: frontend 3000 -> backend 8000)
  withCredentials: true,
});

// Interceptor đã bị xóa vì:
// 1. Với HttpOnly cookie, trình duyệt sẽ tự quản lý việc gửi cookie, không cần và không thể
//    can thiệp bằng JavaScript để thêm "Authorization" header ở phía client.
// 2. Việc thêm header "Authorization" chỉ cần thiết cho các request từ phía Server (Server Actions),
//    và logic đó sẽ được xử lý trực tiếp trong các actions đó để tránh lỗi.

