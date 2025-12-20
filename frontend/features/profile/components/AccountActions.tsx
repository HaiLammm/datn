"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { KeyRound } from "lucide-react";
import { DeleteAccountDialog } from "./DeleteAccountDialog";

interface AccountActionsProps {
  userEmail: string;
}

export function AccountActions({ userEmail }: AccountActionsProps) {
  return (
    <Card data-testid="account-actions">
      <CardHeader>
        <CardTitle>Account Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Change Password */}
          <Button
            variant="outline"
            className="w-full justify-start"
            asChild
            data-testid="change-password-button"
          >
            <Link href="/forgot-password">
              <KeyRound className="h-4 w-4 mr-2" />
              Change Password
            </Link>
          </Button>

          {/* Delete Account */}
          <DeleteAccountDialog userEmail={userEmail} />
        </div>
      </CardContent>
    </Card>
  );
}
