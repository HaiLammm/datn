// src/features/auth/actions.ts
'use server';

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import {
  LoginSchema,
  RegisterSchema,
  VerifyEmailSchema,
  ForgotPasswordSchema,
  ResetPasswordSchema,
} from './types';
import { authService } from '@/services/auth.service';
import type { ReadonlyRequestCookies } from 'next/dist/server/web/spec-extension/adapters/request-cookies';

// Helper function to parse a single cookie string
function parseCookieString(cookieString: string) {
  const parts = cookieString.split(';').map((part) => part.trim());
  const [name, value] = parts[0].split('=');
  const options: any = {
    httpOnly: true, // Assume HttpOnly by default for security
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax', // Default SameSite policy
  };

  for (let i = 1; i < parts.length; i++) {
    const [key, val] = parts[i].split('=');
    const optionKey = key.toLowerCase();

    if (optionKey === 'expires') {
      options.expires = new Date(val);
    } else if (optionKey === 'max-age') {
      options.maxAge = parseInt(val, 10);
    } else if (optionKey === 'path') {
      options.path = val;
    } else if (optionKey === 'domain') {
      options.domain = val;
    } else if (optionKey === 'samesite') {
      options.sameSite = val.toLowerCase();
    } else if (optionKey === 'secure') {
      options.secure = true;
    } else if (optionKey === 'httponly') {
      options.httpOnly = true;
    }
  }
  return { name, value, options };
}

// Helper to apply Set-Cookie headers to the Next.js response
async function applySetCookie(setCookieHeader: string | string[]): Promise<void> {
  const cookieStore = await cookies();
  const headers = Array.isArray(setCookieHeader) ? setCookieHeader : [setCookieHeader];
  for (const cookieString of headers) {
    const { name, value, options } = parseCookieString(cookieString);
    if (name && value) {
      cookieStore.set(name, value, options);
    }
  }
}

// 1. LOGIN ACTION
export type LoginFormState = {
  errors?: { email?: string[]; password?: string[]; server?: string[] };
  message?: string;
};

export async function loginUser(prevState: LoginFormState, formData: FormData): Promise<LoginFormState> {
  const validatedFields = LoginSchema.safeParse(Object.fromEntries(formData.entries()));

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors };
  }

  try {
    const response = await authService.login(validatedFields.data);

    // Xử lý Set-Cookie header từ Backend
    const setCookieHeader = response.headers['set-cookie'];
    if (setCookieHeader) {
      await applySetCookie(setCookieHeader);
    } else {
      // This case might happen if login is successful but no cookie is set.
      return { errors: { server: ['Login response missing session cookie.'] } };
    }
  } catch (error: any) {
    const detail = error.response?.data?.detail;
    let errorMessage = 'Đăng nhập thất bại. Vui lòng thử lại.';
    if (typeof detail === 'string') {
      errorMessage = detail;
      if (detail.includes('không tồn tại')) {
        return { errors: { email: [detail] } };
      }
      if (detail.includes('Mật khẩu không đúng')) {
        return { errors: { password: [detail] } };
      }
    } else if (Array.isArray(detail) && detail.length > 0) {
      errorMessage = detail.map((e: any) => e.msg || e).join(', ');
    }
    return { errors: { server: [errorMessage] } };
  }

  redirect('/dashboard');
}

// 2. REGISTER ACTION
export type RegisterFormState = {
  errors?: { full_name?: string[]; email?: string[]; password?: string[]; confirmPassword?: string[]; role?: string[]; server?: string[] };
  message?: string;
};

export async function registerUser(prevState: RegisterFormState, formData: FormData): Promise<RegisterFormState> {
  const validatedFields = RegisterSchema.safeParse(Object.fromEntries(formData.entries()));

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors };
  }

  try {
    await authService.register(validatedFields.data);
  } catch (error: any) {
    const detail = error.response?.data?.detail;
    let errorMessage = 'Đăng ký thất bại. Vui lòng thử lại.';
    if (typeof detail === 'string') {
      errorMessage = detail;
    } else if (Array.isArray(detail) && detail.length > 0) {
      errorMessage = detail.map((e: any) => e.msg || e).join(', ');
    }
    return { errors: { server: [errorMessage] } };
  }

  // Chuyển hướng đến trang xác thực email sau khi đăng ký thành công
  redirect(`/verify-email?email=${validatedFields.data.email}`);
}

// 3. VERIFY EMAIL ACTION
export type VerifyEmailFormState = {
  errors?: { otp?: string[]; server?: string[] };
  message?: string;
};

export async function verifyEmail(prevState: VerifyEmailFormState, formData: FormData): Promise<VerifyEmailFormState> {
  const validatedFields = VerifyEmailSchema.safeParse(Object.fromEntries(formData.entries()));

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors };
  }

  try {
    await authService.verifyEmail(validatedFields.data);
  } catch (error: any) {
    const detail = error.response?.data?.detail;
    let errorMessage = 'Xác thực thất bại.';
    if (typeof detail === 'string') {
      errorMessage = detail;
    } else if (Array.isArray(detail) && detail.length > 0) {
      errorMessage = detail.map((e: any) => e.msg || e).join(', ');
    }
    return { errors: { server: [errorMessage] } };
  }

  redirect('/login?verified=true');
}

// 4. FORGOT PASSWORD ACTION
export type ForgotPasswordFormState = {
  errors?: { email?: string[]; server?: string[] };
  message?: string;
};

export async function forgotPassword(prevState: ForgotPasswordFormState, formData: FormData): Promise<ForgotPasswordFormState> {
  const validatedFields = ForgotPasswordSchema.safeParse(Object.fromEntries(formData.entries()));

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors };
  }
  
  const email = validatedFields.data.email;

  try {
    await authService.forgotPassword(validatedFields.data);
  } catch (error: any) {
    const detail = error.response?.data?.detail;
    let errorMessage = 'Yêu cầu thất bại.';
    if (typeof detail === 'string') {
      errorMessage = detail;
    } else if (Array.isArray(detail) && detail.length > 0) {
      errorMessage = detail.map((e: any) => e.msg || e).join(', ');
    }
    return { errors: { server: [errorMessage] } };
  }

  redirect(`/reset-password?email=${email}`);
}

// 5. RESET PASSWORD ACTION
export type ResetPasswordState = {
  errors?: { password?: string[]; confirmPassword?: string[]; otp?: string[]; server?: string[] };
  message?: string;
};

export async function resetPassword(prevState: ResetPasswordState, formData: FormData): Promise<ResetPasswordState> {
    const validatedFields = ResetPasswordSchema.safeParse(Object.fromEntries(formData.entries()));

    if (!validatedFields.success) {
        return { errors: validatedFields.error.flatten().fieldErrors };
    }

    try {
        await authService.resetPassword(validatedFields.data);
    } catch (error: any) {
        const detail = error.response?.data?.detail;
        let errorMessage = 'Đặt lại mật khẩu thất bại.';
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMessage = detail.map((e: any) => e.msg || e).join(', ');
        }
        return { errors: { server: [errorMessage] } };
    }

    redirect('/login?reset=success');
}

// 6. LOGOUT ACTION
export async function logoutUser(): Promise<void> {
  try {
    await authService.logout();
  } catch (error) {
    // Even if the API call fails, we should still redirect to login
    console.error('Logout error:', error);
  }
  
  redirect('/login');
}
