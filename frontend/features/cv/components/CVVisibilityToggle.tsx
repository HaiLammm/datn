"use client";

import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
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
import { updateCVVisibilityAction } from "@/features/cv/actions";

interface CVVisibilityToggleProps {
  cvId: string;
  isPublic: boolean;
  onVisibilityChange?: (isPublic: boolean) => void;
}

export function CVVisibilityToggle({
  cvId,
  isPublic,
  onVisibilityChange,
}: CVVisibilityToggleProps) {
  const [currentVisibility, setCurrentVisibility] = useState(isPublic);
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingVisibility, setPendingVisibility] = useState<boolean | null>(null);

  // Sync with prop changes (e.g., after page revalidation)
  useEffect(() => {
    setCurrentVisibility(isPublic);
  }, [isPublic]);

  const handleToggleClick = () => {
    setPendingVisibility(!currentVisibility);
    setShowConfirmDialog(true);
  };

  const handleConfirm = async () => {
    if (pendingVisibility === null) return;

    setIsLoading(true);
    setShowConfirmDialog(false);

    try {
      const result = await updateCVVisibilityAction(cvId, pendingVisibility);
      if (result.success) {
        setCurrentVisibility(pendingVisibility);
        onVisibilityChange?.(pendingVisibility);
        toast.success(
          pendingVisibility 
            ? "CV is now public. Recruiters can view your details." 
            : "CV is now private. Only you can see your details."
        );
      } else {
        console.error("Failed to update visibility:", result.error);
        toast.error(result.error || "Failed to update visibility");
      }
    } catch (error) {
      console.error("Error updating visibility:", error);
      toast.error("An unexpected error occurred");
    } finally {
      setIsLoading(false);
      setPendingVisibility(null);
    }
  };

  const handleCancel = () => {
    setShowConfirmDialog(false);
    setPendingVisibility(null);
  };

  return (
    <>
      <div className="flex items-center space-x-3">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center space-x-2">
                <Switch
                  id={`visibility-${cvId}`}
                  checked={currentVisibility}
                  onCheckedChange={handleToggleClick}
                  disabled={isLoading}
                  aria-label="Toggle CV visibility"
                />
                <Label
                  htmlFor={`visibility-${cvId}`}
                  className={`text-sm font-medium ${
                    currentVisibility ? "text-green-700" : "text-gray-600"
                  } ${isLoading ? "opacity-50" : ""}`}
                >
                  {isLoading ? "Updating..." : currentVisibility ? "Public" : "Private"}
                </Label>
              </div>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="max-w-xs">
              <p>
                {currentVisibility
                  ? "Recruiters can view your CV details when matching jobs"
                  : "Only you can see your CV details"}
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        {/* Visibility badge */}
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium transition-colors ${
            currentVisibility
              ? "bg-green-100 text-green-800"
              : "bg-gray-100 text-gray-800"
          } ${isLoading ? "opacity-50" : ""}`}
        >
          {currentVisibility ? (
            <>
              <svg
                className="w-3 h-3 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              Public
            </>
          ) : (
            <>
              <svg
                className="w-3 h-3 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
              Private
            </>
          )}
        </span>
      </div>

      {/* Confirmation Dialog */}
      <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {pendingVisibility
                ? "Make CV Public?"
                : "Make CV Private?"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {pendingVisibility
                ? "Your CV will be visible to recruiters when they match you with job descriptions. They can view your detailed CV analysis including skills, experience, and AI feedback."
                : "Your CV will be hidden from recruiters. They will only see your match score and skill summary, but not your full CV details."}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleCancel}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirm}>
              {pendingVisibility ? "Make Public" : "Make Private"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
