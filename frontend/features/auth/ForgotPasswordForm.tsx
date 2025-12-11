"use client";

import { useActionState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";

import { Input } from "@/components/ui/input";
import FormWrapper from "@/components/common/FormWrapper";
import { forgotPassword, ForgotPasswordFormState } from "@/features/auth/actions";
import { ForgotPasswordSchema, ForgotPasswordFormValues } from "@/features/auth/types";
import { cn } from "@/lib/utils";

export function ForgotPasswordForm() {
  const [state, formAction, isPending] = useActionState<ForgotPasswordFormState, FormData>(
    forgotPassword,
    { message: '', errors: {} }
  );

  const { register, formState: { errors } } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(ForgotPasswordSchema),
    defaultValues: { email: "" },
  });

  return (
    <FormWrapper
      title="Forgot Your Password?"
      submitText="Send Reset Instructions"
      isPending={isPending}
      action={formAction}
    >
      <p className="text-center text-sm text-gray-600 mb-4">
        No problem. Enter your email address below and we'll send you instructions to reset it.
      </p>
      
      <div>
        <label htmlFor="email" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
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
            <p className={cn("mt-2 text-sm text-red-500")}>{errors.email.message}</p>
          )}
          {state?.errors?.email && (
            <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.email[0]}</p>
          )}
          {state?.errors?.server && (
            <p className={cn("mt-2 text-sm text-red-500 font-bold")}>{state.errors.server[0]}</p>
          )}
        </div>
      </div>

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
