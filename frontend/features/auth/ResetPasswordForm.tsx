"use client";

import { useActionState, Suspense } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

import { Input } from "@/components/ui/input";
import FormWrapper from "@/components/common/FormWrapper";
import { resetPassword, ResetPasswordState } from "@/features/auth/actions";
import { ResetPasswordSchema, ResetPasswordFormValues } from "@/features/auth/types";
import { cn } from "@/lib/utils";

function ResetPasswordFormComponent() {
  const searchParams = useSearchParams();
  // Although the form doesn't show the email, it might be useful for state or display
  const email = searchParams.get('email');

  const [state, formAction, isPending] = useActionState<ResetPasswordState, FormData>(
    resetPassword,
    { message: '', errors: {} }
  );

  const { register, formState: { errors } } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(ResetPasswordSchema),
    defaultValues: {
      email: email || "",
      otp: "",
      password: "",
      confirmPassword: "",
    },
  });

  return (
    <FormWrapper
      title="Reset Your Password"
      submitText="Set New Password"
      isPending={isPending}
      action={formAction}
    >
      <p className="text-center text-sm text-gray-600 mb-4">
        Please enter the OTP sent to {email ? <strong>{email}</strong> : "your email"} and your new password.
      </p>

      <input type="hidden" {...register("email")} value={email || ''} />

      {/* OTP */}
      <div>
        <label htmlFor="otp" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          One-Time Password (OTP)
        </label>
        <div className={cn("mt-2")}>
          <Input
            id="otp"
            type="text"
            maxLength={6}
            {...register("otp")}
            className={cn("block w-full focus:ring-blue-600")}
          />
          {errors.otp && <p className={cn("mt-2 text-sm text-red-500")}>{errors.otp.message}</p>}
          {state?.errors?.otp && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.otp[0]}</p>}
        </div>
      </div>

      {/* New Password */}
      <div>
        <label htmlFor="password" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          New Password
        </label>
        <div className={cn("mt-2")}>
          <Input
            id="password"
            type="password"
            {...register("password")}
          />
          {errors.password && <p className={cn("mt-2 text-sm text-red-500")}>{errors.password.message}</p>}
          {state.errors?.password && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.password[0]}</p>}
        </div>
      </div>

      {/* Confirm New Password */}
      <div>
        <label htmlFor="confirmPassword" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          Confirm New Password
        </label>
        <div className={cn("mt-2")}>
          <Input
            id="confirmPassword"
            type="password"
            {...register("confirmPassword")}
          />
          {errors.confirmPassword && <p className={cn("mt-2 text-sm text-red-500")}>{errors.confirmPassword.message}</p>}
           {state.errors?.confirmPassword && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.confirmPassword[0]}</p>}
        </div>
      </div>

      {/* Server Error */}
      {state.errors?.server && <p className="mt-4 text-center text-sm font-bold text-red-500">{state.errors.server[0]}</p>}

      <div className="text-center mt-6">
        <p className="text-sm text-gray-600">
          Remembered your password?{' '}
          <Link href="/login" className="font-semibold text-blue-600 hover:text-blue-500">
            Back to Login
          </Link>
        </p>
      </div>
    </FormWrapper>
  );
}


export function ResetPasswordForm() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <ResetPasswordFormComponent />
        </Suspense>
    )
}
