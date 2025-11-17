// Convex functions for session management

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const createSession = mutation({
  args: {
    customPrefix: v.optional(v.string()),
    folderName: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Require authentication
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated. Please sign in to create a session.");
    }

    // Generate session ID
    const sessionId = args.folderName || generateSessionId(args.customPrefix);
    const now = Date.now();

    await ctx.db.insert("sessions", {
      sessionId,
      userId: identity.tokenIdentifier,
      startTime: now,
      status: "active",
      screenshotCount: 0,
    });

    return sessionId; // Return just the sessionId string for navigation
  },
});

export const listSessions = query({
  handler: async (ctx) => {
    // Require authentication
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return []; // Return empty array if not authenticated
    }

    // Only return sessions for the current user
    // Note: Sessions without userId (old sessions) will be filtered out
    const sessions = await ctx.db
      .query("sessions")
      .withIndex("by_userId", (q) => q.eq("userId", identity.tokenIdentifier))
      .order("desc")
      .collect();
    
    // Filter to ensure we only return sessions with matching userId
    // (in case index includes undefined values)
    return sessions.filter(s => s.userId === identity.tokenIdentifier);
  },
});

export const getSession = query({
  args: { sessionId: v.string() },
  handler: async (ctx, args) => {
    // Require authentication
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return null; // Return null if not authenticated
    }

    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();
    
    // Verify user owns this session
    // Sessions without userId (old sessions) are not accessible
    if (!session || !session.userId || session.userId !== identity.tokenIdentifier) {
      return null; // Don't return session if user doesn't own it or it's an old session
    }
    
    return session;
  },
});

export const updateSession = mutation({
  args: {
    sessionId: v.string(),
    status: v.optional(
      v.union(
        v.literal("active"),
        v.literal("processing"),
        v.literal("completed"),
        v.literal("error")
      )
    ),
    screenshotCount: v.optional(v.number()),
    endTime: v.optional(v.number()),
    durationSeconds: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    // Require authentication
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated. Please sign in to update a session.");
    }

    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();

    if (!session) {
      throw new Error("Session not found");
    }

    // Verify user owns this session
    // Sessions without userId (old sessions) cannot be updated
    if (!session.userId || session.userId !== identity.tokenIdentifier) {
      throw new Error("You don't have permission to update this session");
    }

    await ctx.db.patch(session._id, {
      status: args.status,
      screenshotCount: args.screenshotCount,
      endTime: args.endTime,
      durationSeconds: args.durationSeconds,
    });

    return { success: true };
  },
});

function generateSessionId(customPrefix?: string): string {
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, "");
  const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, "");
  const random = Math.random().toString(36).substring(2, 5);
  
  if (customPrefix) {
    return `${customPrefix}_${dateStr}_${timeStr}_${random}`;
  }
  return `${dateStr}_${timeStr}_${random}`;
}

