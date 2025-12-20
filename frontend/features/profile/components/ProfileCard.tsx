"use client";

import type { User } from "@datn/shared-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Calendar, Mail } from "lucide-react";

interface ProfileCardProps {
  user: User;
}

function formatDate(dateString: string | undefined): string {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function getInitials(email: string, fullName?: string): string {
  if (fullName) {
    const names = fullName.split(" ");
    if (names.length >= 2) {
      return (names[0][0] + names[names.length - 1][0]).toUpperCase();
    }
    return fullName[0].toUpperCase();
  }
  return email[0].toUpperCase();
}

export function ProfileCard({ user }: ProfileCardProps) {
  const initials = getInitials(user.email, user.full_name);

  return (
    <Card data-testid="profile-card">
      <CardHeader>
        <CardTitle>Profile Information</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col sm:flex-row items-center gap-6">
          {/* Avatar */}
          <Avatar
            className="h-24 w-24 text-2xl"
            data-testid="profile-avatar"
          >
            {user.avatar && <AvatarImage src={user.avatar} alt={user.email} />}
            <AvatarFallback
              className="bg-blue-100 text-blue-700 text-2xl font-semibold"
              data-testid="avatar-fallback"
            >
              {initials}
            </AvatarFallback>
          </Avatar>

          {/* User Info */}
          <div className="flex-1 text-center sm:text-left">
            {user.full_name && (
              <h2
                className="text-xl font-semibold text-gray-900 mb-1"
                data-testid="profile-full-name"
              >
                {user.full_name}
              </h2>
            )}

            <div className="space-y-2">
              {/* Email */}
              <div className="flex items-center justify-center sm:justify-start gap-2 text-gray-600">
                <Mail className="h-4 w-4" />
                <span data-testid="profile-email">{user.email}</span>
              </div>

              {/* Member Since */}
              <div className="flex items-center justify-center sm:justify-start gap-2 text-gray-500 text-sm">
                <Calendar className="h-4 w-4" />
                <span>
                  Member since{" "}
                  <span data-testid="profile-member-since">
                    {formatDate(user.created_at)}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
