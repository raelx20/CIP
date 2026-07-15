/**
 * Cloudflare Workers Edge Gateway for CIP (Constituency Intelligence Platform)
 * 
 * Functions:
 * 1. Reverse Proxy to Vercel (Next.js + FastAPI Serverless Backend)
 * 2. Edge Caching for static assets & read-only API endpoints
 * 3. Security Headers & Edge CORS Handling
 * 4. Fast Edge Health Check
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 1. Instant Edge Health Check (no origin roundtrip needed)
    if (url.pathname === "/cdn-cgi/edge-health" || url.pathname === "/api/v1/system/edge-health") {
      return new Response(
        JSON.stringify({
          status: "healthy",
          layer: "Cloudflare Edge Gateway",
          timestamp: new Date().toISOString(),
          datacenter: request.cf?.colo || "local",
        }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-store",
          },
        }
      );
    }

    // 2. Handle CORS Preflight Requests at the Edge
    if (request.method === "OPTIONS") {
      return handleOptions(request);
    }

    // 3. Prepare target origin URL (Vercel Origin or Local split origin)
    const originUrl = new URL(request.url);
    let targetOriginString = env.ORIGIN_BACKEND_URL || "https://cip.vercel.app";

    // When running locally in development, route API requests to port 8000 and frontend to port 3000
    if (env.ENVIRONMENT === "development" || url.hostname === "localhost" || url.hostname === "127.0.0.1") {
      if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/docs") || url.pathname.startsWith("/openapi.json")) {
        targetOriginString = env.API_BACKEND_URL || "http://localhost:8000";
      } else {
        targetOriginString = env.ORIGIN_BACKEND_URL || "http://localhost:3000";
      }
    }

    const backendOrigin = new URL(targetOriginString);
    originUrl.protocol = backendOrigin.protocol;
    originUrl.hostname = backendOrigin.hostname;
    originUrl.port = backendOrigin.port;

    // Create modified request to forward to Vercel origin
    const originRequest = new Request(originUrl.toString(), {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: "follow",
    });

    // Add Edge security and tracing headers
    originRequest.headers.set("X-Forwarded-Host", url.hostname);
    originRequest.headers.set("X-Edge-Datacenter", request.cf?.colo || "unknown");

    // 4. Fetch from Origin
    let response;
    try {
      response = await fetch(originRequest);
    } catch (err) {
      return new Response(
        JSON.stringify({
          error: "Edge Proxy Error: Unable to reach origin Vercel backend.",
          details: err.message,
        }),
        {
          status: 502,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // 5. Clone and inject response headers
    response = new Response(response.body, response);
    response.headers.set("X-Served-By", `Cloudflare-Edge-${request.cf?.colo || "dev"}`);
    response.headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload");
    response.headers.set("X-Content-Type-Options", "nosniff");
    response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

    return response;
  },
};

/**
 * Handle CORS OPTIONS requests cleanly at Edge
 */
function handleOptions(request) {
  const corsHeaders = {
    "Access-Control-Allow-Origin": request.headers.get("Origin") || "*",
    "Access-Control-Allow-Methods": "GET, HEAD, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": request.headers.get("Access-Control-Request-Headers") || "Authorization, Content-Type, X-Request-ID",
    "Access-Control-Max-Age": "86400",
  };

  return new Response(null, {
    status: 204,
    headers: corsHeaders,
  });
}
