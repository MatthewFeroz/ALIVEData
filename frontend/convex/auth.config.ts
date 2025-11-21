import type { AuthConfig } from "convex/server";

const requiredEnv = (name: string) => {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
};

const workosClientId = requiredEnv("WORKOS_CLIENT_ID");
const issuer = `https://api.workos.com/user_management/${workosClientId}`;
const jwksUrl = `https://api.workos.com/sso/jwks/${workosClientId}`;
export default {
  providers: [
    {
      type: "customJwt",
      issuer,
      jwks: jwksUrl,
      algorithm: "RS256",
    },
  ],
} satisfies AuthConfig;

