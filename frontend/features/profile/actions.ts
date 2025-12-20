"use server";

import { headers, cookies } from "next/headers";
import { redirect } from "next/navigation";
import { userService } from "@/services/user.service";
import type { User, UserStats } from "@datn/shared-types";

type DeleteAccountResult = { message?: string } | { success: boolean };

async function getAccessToken(): Promise<string> {
  const headersList = await headers();
  const cookieHeader = headersList.get("cookie") || "";
  const cookieList = cookieHeader.split(";").map((c) => c.trim());
  const accessTokenCookie = cookieList.find((c) => c.startsWith("access_token="));
  return accessTokenCookie ? accessTokenCookie.split("=")[1] : "";
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    const accessToken = await getAccessToken();
    if (!accessToken) {
      return null;
    }
    return await userService.getCurrentUser(accessToken);
  } catch (error) {
    console.error("Error fetching current user:", error);
    return null;
  }
}

export async function getUserStats(): Promise<UserStats | null> {
  try {
    const accessToken = await getAccessToken();
    if (!accessToken) {
      return null;
    }
    return await userService.getUserStats(accessToken);
  } catch (error) {
    console.error("Error fetching user stats:", error);
    return null;
  }
}

export async function deleteUserAccount(prevState: DeleteAccountResult, formData: FormData): Promise<DeleteAccountResult> {
  try {
    const accessToken = await getAccessToken();
    if (!accessToken) {
      return { message: "Not authenticated" };
    }

    // Call the delete API
    await userService.deleteAccount(accessToken);

    // Return success - client will handle redirect
    return { success: true };
  } catch (error) {
    console.error("Error deleting account:", error);
    return { message: "Failed to delete account. Please try again." };
  }
}
