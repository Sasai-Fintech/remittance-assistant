import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
  langGraphPlatformEndpoint,
  copilotKitEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai";

// Mark this route as dynamic to prevent Next.js from trying to analyze it during build
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// Lazy initialization function - only called at runtime, not during build
function getOpenAIClient() {
  const azureEndpoint = process.env.AZURE_OPENAI_ENDPOINT || "https://azureopenai-uswest-sandbox.openai.azure.com/";
  const azureDeployment = process.env.AZURE_OPENAI_DEPLOYMENT || "gpt-4o-mini";
  const azureApiKey = process.env.AZURE_OPENAI_API_KEY;
  const azureApiVersion = process.env.AZURE_OPENAI_API_VERSION || "2024-12-01-preview";

  if (!azureApiKey) {
    throw new Error("AZURE_OPENAI_API_KEY environment variable is required");
  }

  return new OpenAI({
    apiKey: azureApiKey,
    baseURL: `${azureEndpoint.replace(/\/$/, "")}/openai/deployments/${azureDeployment}`,
    defaultQuery: { "api-version": azureApiVersion },
    defaultHeaders: {
      "api-key": azureApiKey,
    },
  });
}

export const POST = async (req: NextRequest) => {
  try {
    // Initialize OpenAI client lazily (only at runtime, not during build)
    const openai = getOpenAIClient();
    
    const searchParams = req.nextUrl.searchParams;
    const deploymentUrl = searchParams.get("lgcDeploymentUrl");

    // Extract headers from request (including Authorization header from CopilotKit properties)
    // Note: CopilotKit sends properties in the request body, not as HTTP headers
    // The properties.headers are what CopilotKit will forward to the backend
    const headers: Record<string, string> = {};
    const authHeader = req.headers.get("authorization");
    const userIdHeader = req.headers.get("x-user-id");
    const sasaiTokenHeader = req.headers.get("x-sasai-token");
    const languageHeader = req.headers.get("x-language");
    
    if (authHeader) {
      headers["Authorization"] = authHeader;
    }
    if (userIdHeader) {
      headers["X-User-Id"] = userIdHeader;
    }
    if (sasaiTokenHeader) {
      headers["X-Sasai-Token"] = sasaiTokenHeader;
    }
    if (languageHeader) {
      headers["X-Language"] = languageHeader;
    }
    
    // Extract language preference (default to English)
    let language = languageHeader || "en";
    
    // Note: The actual token should come from CopilotKit properties which are set in page.tsx
    // CopilotKit will forward properties.headers to the backend automatically
    // Language will be extracted from properties.metadata.language by CopilotKit runtime
    
    // Configure LLM adapter with language-aware system message for suggestions
    // The language will be determined from the request, but we'll use a dynamic approach
    // Since we can't easily read the body without consuming it, we'll configure the adapter
    // to use language from headers, and the SuggestionsComponent will pass language in instructions
    const llmAdapter = new OpenAIAdapter({ 
      openai,
      model: process.env.AZURE_OPENAI_DEPLOYMENT || "gpt-4o-mini"
    } as any);

    const langsmithApiKey = process.env.LANGSMITH_API_KEY as string;

    const remoteEndpoint = deploymentUrl
      ? langGraphPlatformEndpoint({
          deploymentUrl,
          langsmithApiKey,
          agents: [
            {
              name: "remittance_agent",
              description:
                "Remittance Relationship Manager",
            },
          ],
          // Headers are forwarded via CopilotKit properties automatically
        })
      : copilotKitEndpoint({
          url:
            process.env.REMOTE_ACTION_URL || 
            (process.env.BACKEND_URL 
              ? `${process.env.BACKEND_URL}/api/copilotkit`
              : "http://remittance-assistant-backend.spg2-remittance-assistant.svc.cluster.local:80/api/copilotkit"),
          // Headers are forwarded via CopilotKit properties automatically
        });

    const runtime = new CopilotRuntime({
      remoteEndpoints: [remoteEndpoint],
    });

    // Use language-aware LLM adapter for this request
    const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
      runtime,
      serviceAdapter: llmAdapter, // Language-aware adapter configured above
      endpoint: "/api/copilotkit",
    });

    return handleRequest(req);
  } catch (error) {
    console.error("[COPILOTKIT API] Error:", error);
    return new Response(
      JSON.stringify({ 
        error: "Internal server error", 
        message: error instanceof Error ? error.message : "Unknown error" 
      }),
      { 
        status: 500,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
};
