import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();

// WorkOS token exchange endpoint
// This handles the OAuth callback server-side to avoid CORS issues
http.route({
  path: "/auth/callback",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    try {
      const body = await request.json();
      const { code, redirectUri } = body;

      if (!code) {
        return new Response(JSON.stringify({ error: "Missing authorization code" }), {
          status: 400,
          headers: { 
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        });
      }

      const clientId = process.env.WORKOS_CLIENT_ID;
      const clientSecret = process.env.WORKOS_CLIENT_SECRET;

      if (!clientId || !clientSecret) {
        console.error("Missing WORKOS_CLIENT_ID or WORKOS_CLIENT_SECRET");
        return new Response(JSON.stringify({ error: "Server configuration error - missing credentials" }), {
          status: 500,
          headers: { 
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        });
      }

      // Exchange the code for tokens with WorkOS
      const tokenResponse = await fetch("https://api.workos.com/user_management/authenticate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          client_id: clientId,
          client_secret: clientSecret,
          grant_type: "authorization_code",
          code: code,
          redirect_uri: redirectUri,
        }),
      });

      if (!tokenResponse.ok) {
        const errorText = await tokenResponse.text();
        console.error("WorkOS token exchange failed:", tokenResponse.status, errorText);
        return new Response(JSON.stringify({ 
          error: "Token exchange failed", 
          details: errorText 
        }), {
          status: tokenResponse.status,
          headers: { 
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        });
      }

      const tokenData = await tokenResponse.json();
      
      // Return the tokens to the frontend
      return new Response(JSON.stringify(tokenData), {
        status: 200,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    } catch (error) {
      console.error("Auth callback error:", error);
      return new Response(JSON.stringify({ error: "Internal server error" }), {
        status: 500,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    }
  }),
});

// Handle CORS preflight
http.route({
  path: "/auth/callback",
  method: "OPTIONS",
  handler: httpAction(async () => {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }),
});

export default http;
