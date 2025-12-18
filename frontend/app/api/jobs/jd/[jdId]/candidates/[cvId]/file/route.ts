import { NextRequest, NextResponse } from "next/server";

/**
 * Proxy route to forward CV file requests to backend with authentication.
 * 
 * This is necessary because:
 * 1. Frontend (Next.js) runs on a different port than backend (FastAPI)
 * 2. <embed>/<iframe> tags cannot send HttpOnly cookies cross-origin
 * 3. This route reads the access_token from cookies and forwards it to backend
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ jdId: string; cvId: string }> }
) {
  const { jdId, cvId } = await params;
  const { searchParams } = new URL(request.url);
  const download = searchParams.get("download") === "true";

  // Get access token from cookies
  const accessToken = request.cookies.get("access_token")?.value;

  if (!accessToken) {
    return NextResponse.json(
      { detail: "Authentication required" },
      { status: 401 }
    );
  }

  // Build backend URL
  const backendUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  const fileUrl = `${backendUrl}/jobs/jd/${jdId}/candidates/${cvId}/file${
    download ? "?download=true" : ""
  }`;

  try {
    // Forward request to backend with auth header
    const response = await fetch(fileUrl, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // Handle error responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { detail: errorData.detail || "Failed to fetch CV file" },
        { status: response.status }
      );
    }

    // Get headers from backend response
    const contentType =
      response.headers.get("content-type") || "application/octet-stream";
    const contentDisposition = response.headers.get("content-disposition");

    // Stream the file back to client
    const blob = await response.blob();
    const buffer = await blob.arrayBuffer();

    const headers: Record<string, string> = {
      "Content-Type": contentType,
    };

    if (contentDisposition) {
      headers["Content-Disposition"] = contentDisposition;
    }

    return new NextResponse(buffer, {
      status: 200,
      headers,
    });
  } catch (error) {
    console.error("Error proxying CV file:", error);
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
