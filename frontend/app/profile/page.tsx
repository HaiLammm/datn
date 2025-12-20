import { Suspense } from "react";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { getCurrentUser, getUserStats } from "@/features/profile/actions";
import { ProfileCard } from "@/features/profile/components/ProfileCard";
import { UserStats } from "@/features/profile/components/UserStats";
import { AccountActions } from "@/features/profile/components/AccountActions";
import { ProfileSkeleton } from "@/features/profile/components/ProfileSkeleton";

export default async function ProfilePage() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const [user, stats] = await Promise.all([getCurrentUser(), getUserStats()]);

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Profile</h1>
        <p className="text-gray-600">
          View and manage your account information.
        </p>
      </div>

      <Suspense fallback={<ProfileSkeleton />}>
        <div className="grid gap-6 md:grid-cols-2">
          {/* Left Column - Profile Card */}
          <div className="space-y-6">
            <ProfileCard user={user} />
            <AccountActions userEmail={user.email} />
          </div>

          {/* Right Column - Stats */}
          <div>
            <UserStats stats={stats} />
          </div>
        </div>
      </Suspense>
    </div>
  );
}
