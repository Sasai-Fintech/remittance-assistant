import { NextRequest, NextResponse } from "next/server";

// Mark this route as dynamic
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// Get backend URL from environment variable (available at runtime from configmap)
function getBackendUrl(): string {
  // Prefer BACKEND_URL (server-side only), fallback to NEXT_PUBLIC_BACKEND_URL
  const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
  if (backendUrl) {
    return backendUrl.replace(/\/$/, ''); // Remove trailing slash
  }
  // This should never happen in production if configmap is properly configured
  console.error('[sessions API] BACKEND_URL and NEXT_PUBLIC_BACKEND_URL are not set. Please check the Kubernetes configmap.');
  throw new Error('Backend URL not configured. Please set BACKEND_URL or NEXT_PUBLIC_BACKEND_URL in the configmap.');
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: { threadId: string } }
) {
  try {
    const { threadId } = params;
    const backendUrl = getBackendUrl();
    const url = `${backendUrl}/api/sessions/${threadId}`;
    
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[sessions API] Backend error: ${response.status} ${errorText}`);
      return NextResponse.json(
        { error: 'Failed to delete session', details: errorText },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true }, { status: 200 });
  } catch (error) {
    console.error('[sessions API] Error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

