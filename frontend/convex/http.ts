// Convex HTTP endpoint for WorkOS OAuth callback
// This handles the OAuth callback server-side to avoid CORS issues

import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { WorkOS } from "@workos-inc/node";

const workos = new WorkOS(process.env.WORKOS_API_KEY, {
  clientId: process.env.WORKOS_CLIENT_ID,
});

const http = httpRouter();

// Handle WorkOS OAuth callback
http.route({
  path: "/workos/callback",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const url = new URL(request.url);
    const code = url.searchParams.get("code");
    const state = url.searchParams.get("state");
    
    if (!code) {
      return new Response("Missing authorization code", { status: 400 });
    }

    try {
      // Exchange authorization code for user identity (server-side for Convex)
      const { user } = await workos.userManagement.authenticateWithCode({
        code,
        clientId: process.env.WORKOS_CLIENT_ID!,
      });

      // Get the frontend URL from state param (passed from client) or environment
      // This ensures we redirect back to the correct environment (local or prod)
      let frontendUrl = state;
      
      // Validate frontendUrl - simple check to ensure it's a valid URL
      try {
        if (frontendUrl) new URL(frontendUrl);
      } catch (e) {
        frontendUrl = null; // Invalid URL in state, fall back to env
      }

      if (!frontendUrl) {
        frontendUrl = process.env.FRONTEND_URL || 'https://alivedata.vercel.app';
      }
      
      // Redirect to frontend callback with success - code already exchanged server-side
      // Don't pass code back - it would cause CSRF error if AuthKit tries to exchange it again
      const redirectUrl = new URL("/callback", frontendUrl);
      redirectUrl.searchParams.set("success", "true");
      redirectUrl.searchParams.set("userId", user.id);
      
      return Response.redirect(redirectUrl.toString());
    } catch (error) {
      console.error("WorkOS authentication error:", error);
      
      // Get the frontend URL from state param (passed from client) or environment
      let frontendUrl = state;
      try {
        if (frontendUrl) new URL(frontendUrl);
      } catch (e) {
        frontendUrl = null;
      }

      if (!frontendUrl) {
        frontendUrl = process.env.FRONTEND_URL || 'https://alivedata.vercel.app';
      }

      const redirectUrl = new URL("/callback", frontendUrl);
      redirectUrl.searchParams.set("error", "authentication_failed");
      return Response.redirect(redirectUrl.toString());
    }
  }),
});

export default http;

