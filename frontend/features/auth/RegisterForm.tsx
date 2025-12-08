"use client";

import { useActionState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import FormWrapper from "@/components/common/FormWrapper";
import { RegisterSchema, RegisterFormValues } from "@/features/auth/types";
import { registerUser, RegisterFormState } from "@/features/auth/actions";
import { cn } from "@/lib/utils";

export function RegisterForm() {
  const [state, formAction, isPending] = useActionState<RegisterFormState, FormData>(
    registerUser,
    { message: '', errors: {} }
  );

  const {
    register,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      user_name: "",
      email: "",
      password: "",
      confirmPassword: "",
      birthday: "",
    },
  });

  return (
    <FormWrapper
      title="Create a new account"
      submitText="Register"
      isPending={isPending}
      action={formAction}
    >
      {/* User Name */}
      <div>
        <label htmlFor="user_name" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          Username
        </label>
        <div className={cn("mt-2")}>
          <Input id="user_name" type="text" {...register("user_name")} />
          {errors.user_name && <p className={cn("mt-2 text-sm text-red-500")}>{errors.user_name.message}</p>}
          {state.errors?.user_name && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.user_name[0]}</p>}
        </div>
      </div>

      {/* Email */}
      <div className="mt-4">
        <label htmlFor="email" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          Email address
        </label>
        <div className={cn("mt-2")}>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
          {errors.email && <p className={cn("mt-2 text-sm text-red-500")}>{errors.email.message}</p>}
          {state.errors?.email && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.email[0]}</p>}
        </div>
      </div>

      {/* Password */}
      <div className="mt-4">
        <label htmlFor="password" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          Password
        </label>
        <div className={cn("mt-2")}>
          <Input id="password" type="password" autoComplete="new-password" {...register("password")} />
          {errors.password && <p className={cn("mt-2 text-sm text-red-500")}>{errors.password.message}</p>}
          {state.errors?.password && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.password[0]}</p>}
        </div>
      </div>

      {/* Confirm Password */}
      <div className="mt-4">
        <label htmlFor="confirmPassword" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          Confirm Password
        </label>
        <div className={cn("mt-2")}>
          <Input id="confirmPassword" type="password" autoComplete="new-password" {...register("confirmPassword")} />
          {errors.confirmPassword && <p className={cn("mt-2 text-sm text-red-500")}>{errors.confirmPassword.message}</p>}
          {state.errors?.confirmPassword && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.confirmPassword[0]}</p>}
        </div>
      </div>

      {/* Birthday */}
      <div className="mt-4">
        <label htmlFor="birthday" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          Birthday
        </label>
        <div className={cn("mt-2")}>
          <Input id="birthday" type="date" {...register("birthday")} />
          {errors.birthday && <p className={cn("mt-2 text-sm text-red-500")}>{errors.birthday.message}</p>}
          {state.errors?.birthday && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.birthday[0]}</p>}
        </div>
      </div>

      {/* General Server Error */}
      {state.errors?.server && (
          <p className={cn("mt-4 text-sm font-medium text-red-500")}>{state.errors.server[0]}</p>
      )}
       <div className="text-center mt-4">
          <p className="text-sm text-gray-600">
              Đã có tài khoản?{' '}
              <Link href="/login" className="font-semibold text-blue-600 hover:text-blue-500">
                  Đăng nhập
              </Link>
          </p>
      </div>
    </FormWrapper>
  );
}