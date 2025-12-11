# PROJECT: AI RECRUITMENT PLATFORM (Fullstack)

Tài liệu này là "Bản đồ quy hoạch tổng thể" của dự án, quy định các tiêu chuẩn giao tiếp giữa Frontend và Backend.

## 1. Tổng quan hệ thống (System Overview)
* **Mục tiêu:** Xây dựng nền tảng tuyển dụng thông minh (AI Matching, CV Parsing).
* **Kiến trúc:** Client-Server Model (Decoupled).
    * **Frontend:** Next.js 14+ (App Router) chạy trên port **3000**.
    * **Backend:** FastAPI (Python) chạy trên port **8000**.
* **Language:** Tiếng Việt

## 2. Quy tắc giao tiếp (Integration Contract)

### 2.1. API Standard
* **Base URL (Dev):** `http://localhost:8000/api/v1`
* **Format:** JSON cho cả Request và Response.
* **Error Response:**
    ```json
    {
      "detail": "Nội dung lỗi chi tiết"
    }
    ```

### 2.2. Authentication Flow (Cookie-based)
Hệ thống sử dụng **HttpOnly Cookies** để bảo mật (thay vì lưu Token ở LocalStorage), tối ưu cho Next.js SSR.

* **Backend (Port 8000):**
    * Khi Login thành công, Server set headers `Set-Cookie` cho:
        1. `access_token` (ngắn hạn).
        2. `refresh_token` (dài hạn).
* **Frontend (Port 3000):**
    * Trình duyệt tự động quản lý Cookie.
    * Khi gọi API (Fetch/Axios), bắt buộc phải có option `credentials: 'include'`.
    * Không cần thủ công thêm Header `Authorization`.

### 2.3. CORS Policy (Chính sách tên miền)
Backend phải được cấu hình để chấp nhận request từ Frontend.

* **Backend Config:**
    * `allow_origins = ["http://localhost:3000"]` (Chính xác domain, KHÔNG dùng `*`).
    * `allow_credentials = True` (Bắt buộc để nhận Cookie).


