import { z } from "zod";

// User role type matching backend
export type UserRole = 'job_seeker' | 'recruiter' | 'admin';

// Schema cho form đăng nhập
export const LoginSchema = z.object({
  email: z.string().email({ message: "Invalid email address" }),
  password: z.string().min(6, { message: "Password must be at least 6 characters" }),
});
export type LoginFormValues = z.infer<typeof LoginSchema>;

// Schema cho form đăng ký
export const RegisterSchema = z.object({
  full_name: z.string().min(3, { message: "Full name must be at least 3 characters" }),
  email: z.string().email({ message: "Invalid email address" }),
  password: z.string().min(6, { message: "Password must be at least 6 characters" }),
  confirmPassword: z.string(),
  role: z.enum(["job_seeker", "recruiter"], { message: "Please select a role" }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});
export type RegisterFormValues = z.infer<typeof RegisterSchema>;

// Schema cho form quên mật khẩu
export const ForgotPasswordSchema = z.object({
  email: z.string().email({ message: "Invalid email address" }),
});
export type ForgotPasswordFormValues = z.infer<typeof ForgotPasswordSchema>;

// Schema cho form xác thực email bằng OTP
export const VerifyEmailSchema = z.object({
  email: z.string().email({ message: "Địa chỉ email không hợp lệ." }),
  otp: z.string().min(6, { message: "Mã OTP phải có 6 chữ số." }),
});
export type VerifyEmailFormValues = z.infer<typeof VerifyEmailSchema>;


// Schema cho form đặt lại mật khẩu
export const ResetPasswordSchema = z.object({
  email: z.string().email(),
  otp: z.string().min(6, { message: "Mã OTP phải có 6 chữ số." }),
  password: z.string().min(6, { message: "Mật khẩu phải có ít nhất 6 ký tự." }),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Mật khẩu không khớp.",
  path: ["confirmPassword"],
});
export type ResetPasswordFormValues = z.infer<typeof ResetPasswordSchema>;
