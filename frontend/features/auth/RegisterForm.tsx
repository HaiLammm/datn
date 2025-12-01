"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import FormWrapper from "@/components/common/FormWrapper";
import { registerSchema, RegisterFormValues } from "@/features/auth/types";
import { cn } from "@/lib/utils"; // Import cn

export function RegisterForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = (data: RegisterFormValues) => {
    console.log("Register submitted:", data);
    // Handle registration logic here
  };

  return (
    <FormWrapper
      title="Create a new account"
      submitText="Register"
      onSubmit={handleSubmit(onSubmit)}
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
            {...register("email")}
            className={cn("block w-full focus:ring-blue-600")}
          />
          {errors.email && (
            <p className={cn("mt-2 text-sm text-red-500")}>{errors.email.message}</p>
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
        </div>
        <div className={cn("mt-2")}>
          <Input
            id="password"
            type="password"
            autoComplete="new-password"
            {...register("password")}
            className={cn("block w-full focus:ring-blue-600")}
          />
          {errors.password && (
            <p className={cn("mt-2 text-sm text-red-500")}>
              {errors.password.message}
            </p>
          )}
        </div>
      </div>

      <div>
        <div className={cn("flex items-center justify-between")}>
          <label
            htmlFor="confirm-password"
            className={cn("block text-sm font-medium leading-6 text-gray-900")}
          >
            Confirm Password
          </label>
        </div>
        <div className={cn("mt-2")}>
          <Input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            {...register("confirmPassword")}
            className={cn("block w-full focus:ring-blue-600")}
          />
          {errors.confirmPassword && (
            <p className={cn("mt-2 text-sm text-red-500")}>
              {errors.confirmPassword.message}
            </p>
          )}
        </div>
      </div>
    </FormWrapper>
  );
}