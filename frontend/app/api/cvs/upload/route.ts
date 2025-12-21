import { NextRequest, NextResponse } from "next/server";
import { revalidatePath } from "next/cache";

/**
 * Proxy route to forward CV upload requests to backend with authentication.
 *
 * This is necessary because:
 * 1. Frontend (Next.js) runs on a different port than backend (FastAPI)
 * 2. Fetch requests cannot send HttpOnly cookies cross-origin
 * 3. This route reads the access_token from cookies and forwards it to backend
 * 4. Using client-side XHR allows us to track upload progress
 */
export async function POST(request: NextRequest) {
  // Get access token from cookies
  const accessToken = request.cookies.get("access_token")?.value;

  if (!accessToken) {
    return NextResponse.json(
      { detail: "Authentication required" },
      { status: 401 }
    );
  }

  try {
    // Get the form data from the request
    const formData = await request.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json(
        { detail: "No file provided" },
        { status: 400 }
      );
    }

    // Create a new FormData to send to backend
    // This ensures the file is properly formatted for FastAPI
    const backendFormData = new FormData();
    backendFormData.append("file", file, file.name);

    // Build backend URL
    // Note: trailing slash is required to avoid 307 redirect from FastAPI
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const uploadUrl = `${backendUrl}/cvs/`;

    // Forward request to backend with auth header
    const response = await fetch(uploadUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        // Don't set Content-Type - let fetch set it with the boundary
      },
      body: backendFormData,
    });

    // Get response data
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      console.error("Backend upload error:", response.status, data);
      return NextResponse.json(
        { detail: data.detail || "Failed to upload CV" },
        { status: response.status }
      );
    }

    // Revalidate related paths
    revalidatePath("/cvs");
    revalidatePath("/dashboard");

    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    console.error("Error proxying CV upload:", error);
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
