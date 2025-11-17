// Convex functions for session management

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const createSession = mutation({
  args: {
    customPrefix: v.optional(v.string()),
    folderName: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Generate session ID
    const sessionId = args.folderName || generateSessionId(args.customPrefix);
    const now = Date.now();

    await ctx.db.insert("sessions", {
      sessionId,
      startTime: now,
      status: "active",
      screenshotCount: 0,
    });

    return sessionId; // Return just the sessionId string for navigation
  },
});

export const listSessions = query({
  handler: async (ctx) => {
    const sessions = await ctx.db
      .query("sessions")
      .order("desc")
      .collect();
    return sessions;
  },
});

export const getSession = query({
  args: { sessionId: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();
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
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();

    if (!session) {
      throw new Error("Session not found");
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

