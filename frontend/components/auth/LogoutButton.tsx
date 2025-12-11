"use client";

import { logoutUser } from "@/features/auth/actions";

export function LogoutButton() {
  const handleLogout = async () => {
    await logoutUser();
  };

  return (
    <button
      onClick={handleLogout}
      className="px-6 py-2 font-semibold text-white bg-red-500 rounded-md hover:bg-red-600 transition-colors"
    >
      Logout
    </button>
  );
}
