import { NextRequest, NextResponse } from "next/server";

/**
 * Proxy route for job match calculation API.
 * 
 * This API route handles job match score calculation requests from client components.
 * It reads the access_token from HttpOnly cookies and forwards it to the backend API.
 * 
 * This is necessary because:
 * 1. Client components cannot access HttpOnly cookies directly
 * 2. Server actions that use headers() cannot be called from client components
 * 3. This proxy route bridges the gap by reading cookies server-side
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ jdId: string }> }
) {
  const { jdId } = await params;

  // Get access token from cookies
  const accessToken = request.cookies.get("access_token")?.value;

  if (!accessToken) {
    return NextResponse.json(
      { detail: "Authentication required" },
      { status: 401 }
    );
  }

  // Parse request body
  let requestBody;
  try {
    requestBody = await request.json();
  } catch (error) {
    return NextResponse.json(
      { detail: "Invalid request body" },
      { status: 400 }
    );
  }

  // Validate required fields
  if (!requestBody.cv_id) {
    return NextResponse.json(
      { detail: "cv_id is required" },
      { status: 400 }
    );
  }

  // Build backend URL
  const backendUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  const matchUrl = `${backendUrl}/jobs/jd/${jdId}/match`;

  try {
    // Forward request to backend with auth header
    const response = await fetch(matchUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(requestBody),
    });

    // Parse response
    const responseData = await response.json();

    // Return response with same status code
    return NextResponse.json(responseData, { status: response.status });
  } catch (error) {
    console.error("Error proxying job match request:", error);
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}