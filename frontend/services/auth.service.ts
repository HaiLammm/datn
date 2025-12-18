// src/services/auth.service.ts
import { apiClient } from './api-client';
import {
  LoginFormValues,
  RegisterFormValues,
  ForgotPasswordFormValues,
  ResetPasswordFormValues,
  VerifyEmailFormValues
} from '@/features/auth/types';

/**
 * Handles the login request.
 */
async function login(data: LoginFormValues) {
  const payload = {
    email: data.email,
    password: data.password,
  };
  return apiClient.post('/auth/login', payload);
}

/**
 * Handles the user registration request.
 */
async function register(data: RegisterFormValues) {
  const payload = {
    email: data.email,
    password: data.password,
    full_name: data.full_name,
    birthday: data.birthday || undefined,
    role: data.role,
  };
  return apiClient.post('/auth/register', payload);
}

/**
 * Handles the email verification request.
 */
async function verifyEmail(data: VerifyEmailFormValues) {
    const payload = {
        email: data.email,
        activation_code: data.otp,
    }
  return apiClient.post('/auth/verify-email', payload);
}

/**
 * Handles the forgot password request.
 */
async function forgotPassword(data: ForgotPasswordFormValues) {
    const payload = {
        email: data.email,
    }
  return apiClient.post('/auth/forgot-password', payload);
}

/**
 * Handles the reset password request.
 */
async function resetPassword(data: ResetPasswordFormValues) {
    const payload = {
        email: data.email,
        otp: data.otp,
        new_password: data.password
    }
  return apiClient.post('/auth/reset-password', payload);
}

/**
 * Handles the logout request.
 */
async function logout() {
  return apiClient.post('/auth/logout');
}

// Export the auth service methods
export const authService = {
  login,
  register,
  verifyEmail,
  forgotPassword,
  resetPassword,
  logout,
};
