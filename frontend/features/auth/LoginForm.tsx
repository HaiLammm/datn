"use client";

import { useActionState, Suspense } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSearchParams } from "next/navigation";

import { loginUser } from "@/features/auth/actions";
import { Input } from "@/components/ui/input";
import FormWrapper from "@/components/common/FormWrapper";
import { LoginSchema, LoginFormValues } from "@/features/auth/types";
import { cn } from "@/lib/utils";

function LoginFormComponent() {
    const searchParams = useSearchParams();
    const isVerified = searchParams.get('verified') === 'true';
    const isReset = searchParams.get('reset') === 'success';

    const [state, formAction, isPending] = useActionState(loginUser, {
        message: '',
        errors: {}
    });

    const {
        register,
        formState: { errors },
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
            isPending={isPending}
            action={formAction}
        >
            {isVerified && (
                <div className="mb-4 text-center text-sm font-medium text-green-600 bg-green-50 p-3 rounded-md">
                    Email verified successfully! You can now log in.
                </div>
            )}
            {isReset && (
                <div className="mb-4 text-center text-sm font-medium text-green-600 bg-green-50 p-3 rounded-md">
                    Password has been reset successfully. You can now log in with your new password.
                </div>
            )}
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
                        {...register("email")}
                        className={cn("block w-full focus:ring-blue-600")}
                    />
                    
                    {errors.email && (
                        <p className={cn("mt-2 text-sm text-red-500")}>
                            {errors.email.message}
                        </p>
                    )}
                    
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
                        <Link href="/forgot-password" className={cn("font-semibold text-blue-600 hover:text-blue-500")}>
                            Forgot password?
                        </Link>
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
                     {state?.errors?.password && (
                         <p className={cn("mt-2 text-sm text-red-500")}>
                            {state.errors.password[0]}
                        </p>
                    )}
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

export function LoginForm() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <LoginFormComponent />
        </Suspense>
    )
}
