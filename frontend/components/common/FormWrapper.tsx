import React from 'react';
import { cn } from "@/lib/utils"; // Import cn
import { Button } from "@/components/ui/button"; // Import Button

interface FormWrapperProps {
  title: string;
  children: React.ReactNode;
  submitText: string;
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
}

const FormWrapper: React.FC<FormWrapperProps> = ({ title, children, submitText, onSubmit }) => {
  return (
    <div className={cn("flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8")}>
      <div className={cn("sm:mx-auto sm:w-full sm:max-w-sm")}>
        <h2 className={cn("mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900")}>
          {title}
        </h2>
      </div>

      <div className={cn("mt-10 sm:mx-auto sm:w-full sm:max-w-sm")}>
        <form className={cn("space-y-6")} onSubmit={onSubmit}>
          {children}
          <div>
            <Button
              type="submit"
              className={cn("w-full bg-blue-500 hover:bg-blue-600 focus-visible:outline-blue-600")}
            >
              {submitText}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormWrapper;

