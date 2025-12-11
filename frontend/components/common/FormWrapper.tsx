import type React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface FormWrapperProps {
  title: string
  children: React.ReactNode
  submitText: string
  isPending: boolean
  action: (payload: FormData) => void
}

const FormWrapper: React.FC<FormWrapperProps> = ({ title, children, submitText, isPending, action }) => {
  return (
    <div
      className={cn("flex min-h-screen flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8 bg-background")}
    >
      <Card className={cn("w-full sm:max-w-sm shadow-lg")}>
        <CardHeader className={cn("space-y-1")}>
          <CardTitle className={cn("text-2xl font-bold tracking-tight text-center text-foreground")}>{title}</CardTitle>
        </CardHeader>

        <CardContent>
          <form className={cn("space-y-6")} action={action}>
            {children}

            <div>
              <Button disabled={isPending} type="submit" className={cn("w-full")}>
                {submitText}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default FormWrapper
