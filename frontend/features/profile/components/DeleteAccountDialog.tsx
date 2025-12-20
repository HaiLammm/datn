"use client";

import { useActionState, useState, useEffect } from "react";
import { useFormStatus } from "react-dom";
import { useRouter } from "next/navigation";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Trash2, AlertTriangle } from "lucide-react";
import { deleteUserAccount } from "../actions";

interface DeleteAccountDialogProps {
  userEmail: string;
}

function DeleteAccountForm({ userEmail, onClose }: { userEmail: string; onClose: () => void }) {
  const [state, formAction] = useActionState(deleteUserAccount, {});
  const [emailConfirmation, setEmailConfirmation] = useState("");
  const router = useRouter();

  const isEmailValid = emailConfirmation === userEmail;

  useEffect(() => {
    if ((state as any).success) {
      router.push("/login");
    }
  }, [state, router]);

  return (
    <form action={formAction} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Confirm your email address</Label>
        <Input
          id="email"
          type="email"
          name="email"
          value={emailConfirmation}
          onChange={(e) => setEmailConfirmation(e.target.value)}
          placeholder="Enter your email to confirm"
          required
          data-testid="email-confirmation-input"
        />
        <p className="text-sm text-muted-foreground">
          Type <strong>{userEmail}</strong> to confirm account deletion.
        </p>
      </div>

      {(state as any).message && (
        <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
          <AlertTriangle className="h-4 w-4 inline mr-2" />
          {(state as any).message}
        </div>
      )}

      <FormFooter isEmailValid={isEmailValid} onClose={onClose} />
    </form>
  );
}

function FormFooter({ isEmailValid, onClose }: { isEmailValid: boolean; onClose: () => void }) {
  const { pending } = useFormStatus();

  return (
    <AlertDialogFooter>
      <AlertDialogCancel onClick={onClose} disabled={pending}>
        Cancel
      </AlertDialogCancel>
      <AlertDialogAction
        type="submit"
        disabled={!isEmailValid || pending}
        className="bg-red-600 hover:bg-red-700"
        data-testid="confirm-delete-button"
      >
        {pending ? "Deleting..." : "Delete Account"}
      </AlertDialogAction>
    </AlertDialogFooter>
  );
}

export function DeleteAccountDialog({ userEmail }: DeleteAccountDialogProps) {
  const [open, setOpen] = useState(false);

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button
          variant="outline"
          className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
          data-testid="delete-account-button"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete Account
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent data-testid="delete-account-dialog">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-red-600">
            <AlertTriangle className="h-5 w-5 inline mr-2" />
            Delete Account
          </AlertDialogTitle>
          <AlertDialogDescription className="space-y-2">
            <p>
              This action cannot be undone. This will permanently delete your account
              and remove all associated data including:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Your profile information</li>
              <li>All uploaded CVs and files</li>
              <li>Analysis results and statistics</li>
              <li>Job descriptions and applications</li>
            </ul>
            <p className="font-medium">
              Are you sure you want to proceed?
            </p>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <DeleteAccountForm userEmail={userEmail} onClose={() => setOpen(false)} />
      </AlertDialogContent>
    </AlertDialog>
  );
}