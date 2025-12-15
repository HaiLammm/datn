"use client";

import { useState, useTransition } from "react";
import { deleteCVAction } from "@/features/cv/actions";
import { useDeleteMode } from "@/features/cv/context/DeleteModeContext";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import type { CheckedState } from "@radix-ui/react-checkbox";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";

interface DeleteCVDialogProps {
  cvId: string;
  filename: string;
}

export function DeleteCVDialog({ cvId, filename }: DeleteCVDialogProps) {
  const [isPending, startTransition] = useTransition();
  const [open, setOpen] = useState(false);
  const [dontAskAgain, setDontAskAgain] = useState(false);
  const { skipConfirmation, setSkipConfirmation } = useDeleteMode();

  const executeDelete = () => {
    startTransition(async () => {
      await deleteCVAction(cvId);
      setOpen(false);
    });
  };

  const handleDeleteClick = () => {
    if (skipConfirmation) {
      // Skip confirmation and delete directly
      executeDelete();
    } else {
      // Show confirmation dialog
      setOpen(true);
    }
  };

  const handleConfirmDelete = () => {
    if (dontAskAgain) {
      setSkipConfirmation(true);
    }
    executeDelete();
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <Button
        variant="destructive"
        size="sm"
        onClick={handleDeleteClick}
        disabled={isPending}
      >
        {isPending ? "Deleting..." : "Delete"}
      </Button>

      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete CV</AlertDialogTitle>
          <AlertDialogDescription asChild>
            <div className="space-y-3">
              <p>
                Are you sure you want to delete{" "}
                <span className="font-semibold text-foreground">
                  &quot;{filename}&quot;
                </span>
                ?
              </p>
              <p>
                This action cannot be undone. All analysis data associated with
                this CV will be permanently removed.
              </p>
              <div className="flex items-center space-x-2 pt-2">
                <Checkbox
                  id="dont-ask-again"
                  checked={dontAskAgain}
                  onCheckedChange={(checked: CheckedState) =>
                    setDontAskAgain(checked === true)
                  }
                />
                <label
                  htmlFor="dont-ask-again"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                >
                  Don&apos;t ask again for this session
                </label>
              </div>
            </div>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isPending}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirmDelete}
            disabled={isPending}
            className="bg-destructive text-white hover:bg-destructive/90"
          >
            {isPending ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
