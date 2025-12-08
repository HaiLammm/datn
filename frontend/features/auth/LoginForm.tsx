"use client";

import { useActionState } from "react";
import Link from "next/link";
import { loginUser } from "@/features/auth/actions";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import FormWrapper from "@/components/common/FormWrapper"; // Đảm bảo đường dẫn đúng
import { LoginSchema, LoginFormValues } from "@/features/auth/types";
import { cn } from "@/lib/utils";

export function LoginForm() {
    // 1. SỬA: Cú pháp object khởi tạo đúng
    const [state, formAction, isPending] = useActionState(loginUser, {
        message: '',
        errors: {}
    });

    const {
        register,
        // handleSubmit, // Không cần dùng handleSubmit của hook-form nữa vì ta dùng Server Action
        formState: { errors }, // Đây là lỗi client (validate form)
    } = useForm<LoginFormValues>({
        resolver: zodResolver(LoginSchema),
        defaultValues: {
            email: "",
            password: "",
        },
    });

    return (
        <FormWrapper
            title="Sign in to your account"
            submitText="Sign in"
            // 2. SỬA: Truyền biến isPending vào trong ngoặc nhọn
            isPending={isPending}
            // 3. SỬA: Dùng đúng tên biến 'formAction' lấy từ hook
            action={formAction} 
        >
            <div>
                <label
                    htmlFor="email"
                    className={cn("block text-sm font-medium leading-6 text-gray-900")}
                >
                    Email address
                </label>

                <div className={cn("mt-2")}>
                    <Input
                        id="email"
                        type="email"
                        autoComplete="email"
                        // register sẽ tự thêm name="email" để Server Action đọc được
                        {...register("email")}
                        className={cn("block w-full focus:ring-blue-600")}
                    />
                    
                    {/* Hiển thị lỗi Client (Validate sai định dạng) */}
                    {errors.email && (
                        <p className={cn("mt-2 text-sm text-red-500")}>
                            {errors.email.message}
                        </p>
                    )}
                    
                    {/* 4. GỢI Ý THÊM: Hiển thị lỗi Server trả về (nếu có) */}
                    {state?.errors?.email && (
                         <p className={cn("mt-2 text-sm text-red-500")}>
                            {state.errors.email[0]}
                        </p>
                    )}
                </div>
            </div>

            <div>
                <div className={cn("flex items-center justify-between")}>
                    <label
                        htmlFor="password"
                        className={cn("block text-sm font-medium leading-6 text-gray-900")}
                    >
                        Password
                    </label>
                    <div className={cn("text-sm")}>
                        <a href="#" className={cn("font-semibold text-blue-600 hover:text-blue-500")}>
                            Forgot password?
                        </a>
                    </div>
                </div>

                <div className={cn("mt-2")}>
                    <Input
                        id="password"
                        type="password"
                        autoComplete="current-password"
                        {...register("password")}
                        className={cn("block w-full focus:ring-blue-600")}
                    />
                    {errors.password && (
                        <p className={cn("mt-2 text-sm text-red-500")}>
                            {errors.password.message}
                        </p>
                    )}
                    
                     {/* Hiển thị lỗi chung từ Server (ví dụ: Sai mật khẩu) */}
                     {state?.errors?.server && (
                        <p className={cn("mt-2 text-sm text-red-500 font-bold")}>
                            {state.errors.server[0]}
                        </p>
                    )}
                </div>
            </div>
             <div className="text-center mt-4">
                <p className="text-sm text-gray-600">
                    Chưa có tài khoản?{' '}
                    <Link href="/register" className="font-semibold text-blue-600 hover:text-blue-500">
                        Đăng kí ngay
                    </Link>
                </p>
            </div>
        </FormWrapper>
    );
}
