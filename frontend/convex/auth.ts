import { convexAuth } from "@convex-dev/auth/server";
import WorkOS from "@auth/core/providers/workos";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [
    WorkOS({
      clientId: process.env.WORKOS_CLIENT_ID,
      clientSecret: process.env.WORKOS_API_KEY,
    }),
  ],
  callbacks: {
    async redirect({ redirectTo }) {
      return "https://alivedata.vercel.app";
    },
  },
});

