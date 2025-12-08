import axios from 'axios';

// Lấy URL từ biến môi trường (sẽ cài đặt sau)
const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tự động gắn Token nếu có (để xác thực User)
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : '';
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
