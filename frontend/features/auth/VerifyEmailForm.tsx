"use client";

import { useActionState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSearchParams } from 'next/navigation';
import { Suspense } from "react";

import { Input } from "@/components/ui/input";
import FormWrapper from "@/components/common/FormWrapper";
import { verifyEmail, VerifyEmailFormState } from "@/features/auth/actions";
import { VerifyEmailSchema, VerifyEmailFormValues } from "@/features/auth/types";
import { cn } from "@/lib/utils";

function VerifyEmailFormComponent() {
  const searchParams = useSearchParams();
  const email = searchParams.get('email') || "";

  const [state, formAction, isPending] = useActionState<VerifyEmailFormState, FormData>(
    verifyEmail,
    { message: '', errors: {} }
  );

  const { register, formState: { errors } } = useForm<VerifyEmailFormValues>({
    resolver: zodResolver(VerifyEmailSchema),
    defaultValues: { email: email, otp: "" },
  });

  return (
    <FormWrapper
      title="Verify Your Email"
      submitText="Verify Account"
      isPending={isPending}
      action={formAction}
    >
      <p className="text-center text-sm text-gray-600 mb-4">
        An OTP has been sent to <strong>{email}</strong>. Please enter it below to activate your account.
      </p>

      <input type="hidden" {...register("email")} value={email} />

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
            placeholder="******"
          />
          {errors.otp && (
            <p className={cn("mt-2 text-sm text-red-500")}>{errors.otp.message}</p>
          )}
          {state?.errors?.otp && (
            <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.otp[0]}</p>
          )}
          {state?.errors?.server && (
            <p className={cn("mt-2 text-sm text-red-500 font-bold")}>{state.errors.server[0]}</p>
          )}
           {state.message && <p className="mt-2 text-sm text-green-500">{state.message}</p>}
        </div>
      </div>
    </FormWrapper>
  );
}


export function VerifyEmailForm() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <VerifyEmailFormComponent />
        </Suspense>
    )
}