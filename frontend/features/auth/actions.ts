// src/features/auth/actions.ts
'use server'

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { LoginSchema, RegisterSchema } from './types'; 
import { apiClient } from '@/services/api-client'; 

// 1.Định nghĩa kiểu dữ liệu trả về cho Form State
export type LoginFormState = {
  errors?: {
    email?: string[];
    password?: string[];
    server?: string[]; 
  };
  message?: string;
}

export async function loginUser(prevState: LoginFormState, formData: FormData) {
  // 2. Validate dữ liệu đầu vào
  const rawData = Object.fromEntries(formData.entries());
  const validatedFields = LoginSchema.safeParse(rawData);

  if (!validatedFields.success) {
    const { email, password } = validatedFields.error.flatten().fieldErrors;
    return {
      errors: {
        email: email,
        password: password,
      },
      message: 'Dữ liệu không hợp lệ.',
    };
  }

  const { email, password } = validatedFields.data;

  // 3. Gọi sang Python Backend
  try {
    const response = await apiClient.post('/auth/login', { 
      email, 
      password 
    });
    
    const { access_token } = response.data;

    // 4. Lưu Token vào Cookie (Quan trọng!)
    const cookieStore = await cookies();
    cookieStore.set('session_token', access_token, {
      httpOnly: true, // JavaScript ở client không đọc được (chống XSS)
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 24 * 7, // 7 ngày
      path: '/',
    });

  } catch (error: any) {
    // Xử lý lỗi từ Python trả về
    return {
      errors: {
        server: [error.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.']
      },
       message: 'Đăng nhập thất bại.',
    };
  }

  // 5. Nếu thành công, chuyển hướng người dùng
  redirect('/dashboard');
}

export type RegisterFormState = {
  errors?: {
    user_name?: string[];
    email?: string[];
    password?: string[];
    confirmPassword?: string[];
    birthday?: string[];
    server?: string[];
  };
  message?: string;
};

export async function registerUser(prevState: RegisterFormState, formData: FormData): Promise<RegisterFormState> {
  const rawData = Object.fromEntries(formData.entries());
  const validatedFields = RegisterSchema.safeParse(rawData);

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: 'Invalid form data.',
    };
  }

  const { user_name, email, password, birthday } = validatedFields.data;

  // TODO: Implement actual API call to the backend
  console.log("Registering user with:", { user_name, email, password, birthday });
  
  // On success, redirect to the login page.
  redirect('/login');
}
