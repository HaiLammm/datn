"use client";

import { useActionState, useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import FormWrapper from "@/components/common/FormWrapper";
import { RegisterSchema, RegisterFormValues } from "@/features/auth/types";
import { registerUser, RegisterFormState } from "@/features/auth/actions";
import { cn } from "@/lib/utils";
import { User, Briefcase } from "lucide-react";

export function RegisterForm() {
  const [state, formAction, isPending] = useActionState<RegisterFormState, FormData>(
    registerUser,
    { message: '', errors: {} }
  );
  const [selectedRole, setSelectedRole] = useState<"user" | "recruiter">("user");

  const {
    register,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
      confirmPassword: "",
      birthday: "",
      role: "user",
    },
  });

  return (
    <FormWrapper
      title="Create a new account"
      submitText="Register"
      isPending={isPending}
      action={formAction}
    >
      {/* Role Selection */}
      <div>
        <label className={cn("block text-sm font-medium leading-6 text-gray-900 mb-3")}>
          I am a
        </label>
        <input type="hidden" name="role" value={selectedRole} />
        <RadioGroup
          value={selectedRole}
          onValueChange={(value) => setSelectedRole(value as "user" | "recruiter")}
          className="grid grid-cols-2 gap-4"
          aria-label="Select your role"
        >
          <div>
            <RadioGroupItem
              value="user"
              id="role-user"
              className="peer sr-only"
            />
            <Label
              htmlFor="role-user"
              className={cn(
                "flex flex-col items-center justify-center rounded-lg border-2 p-4 cursor-pointer transition-all",
                "hover:bg-gray-50",
                selectedRole === "user"
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-gray-200 text-gray-600"
              )}
            >
              <User className="h-8 w-8 mb-2" />
              <span className="font-medium">Job Seeker</span>
              <span className="text-xs text-gray-500 mt-1">Looking for jobs</span>
            </Label>
          </div>
          <div>
            <RadioGroupItem
              value="recruiter"
              id="role-recruiter"
              className="peer sr-only"
            />
            <Label
              htmlFor="role-recruiter"
              className={cn(
                "flex flex-col items-center justify-center rounded-lg border-2 p-4 cursor-pointer transition-all",
                "hover:bg-gray-50",
                selectedRole === "recruiter"
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-gray-200 text-gray-600"
              )}
            >
              <Briefcase className="h-8 w-8 mb-2" />
              <span className="font-medium">Recruiter / HR</span>
              <span className="text-xs text-gray-500 mt-1">Hiring talents</span>
            </Label>
          </div>
        </RadioGroup>
        {errors.role && <p className={cn("mt-2 text-sm text-red-500")}>{errors.role.message}</p>}
        {state.errors?.role && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.role[0]}</p>}
      </div>

      {/* Full Name */}
      <div className="mt-4">
        <label htmlFor="full_name" className={cn("block text-sm font-medium leading-6 text-gray-900")}>
          Full Name
        </label>
        <div className={cn("mt-2")}>
          <Input id="full_name" type="text" {...register("full_name")} />
          {errors.full_name && <p className={cn("mt-2 text-sm text-red-500")}>{errors.full_name.message}</p>}
          {state.errors?.full_name && <p className={cn("mt-2 text-sm text-red-500")}>{state.errors.full_name[0]}</p>}
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

      {/* Birthday (optional) */}
      <input type="hidden" name="birthday" value="" />

      {/* General Server Error */}
      {state.errors?.server && state.errors.server.length > 0 && (
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