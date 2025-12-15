import { NextRequest, NextResponse } from "next/server";

// Mark this route as dynamic to prevent Next.js from trying to analyze it during build
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

export async function GET(req: NextRequest) {
  console.log('[sessions API] 🔵 GET /api/sessions/ called');
  
  try {
    const backendUrl = getBackendUrl();
    const url = `${backendUrl}/api/sessions/`;
    
    console.log('[sessions API] Backend URL:', backendUrl);
    console.log('[sessions API] Full URL:', url);
    console.log('[sessions API] Fetching sessions from backend...');
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    console.log('[sessions API] Response status:', response.status, response.statusText);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[sessions API] ❌ Backend error: ${response.status} ${errorText}`);
      return NextResponse.json(
        { error: 'Failed to fetch sessions', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('[sessions API] ✅ Success! Received', Array.isArray(data) ? data.length : 0, 'sessions');
    console.log('[sessions API] Data preview:', JSON.stringify(data).substring(0, 200));
    
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('[sessions API] ❌ Error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

