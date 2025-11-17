// Convex functions for file management

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const uploadScreenshot = mutation({
  args: {
    sessionId: v.string(),
    filename: v.string(),
    fileId: v.id("_storage"),
    size: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    // Get session
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();

    if (!session) {
      throw new Error("Session not found");
    }

    // Create screenshot record
    const screenshot = await ctx.db.insert("screenshots", {
      sessionId: session._id,
      filename: args.filename,
      fileId: args.fileId,
      uploadedAt: Date.now(),
      size: args.size,
    });

    // Update session screenshot count
    await ctx.db.patch(session._id, {
      screenshotCount: (session.screenshotCount || 0) + 1,
    });

    return {
      screenshotId: screenshot,
      filename: args.filename,
      fileId: args.fileId,
      timestamp: Date.now(),
    };
  },
});

export const listScreenshots = query({
  args: { sessionId: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();

    if (!session) {
      return [];
    }

    const screenshots = await ctx.db
      .query("screenshots")
      .withIndex("by_session", (q) => q.eq("sessionId", session._id))
      .collect();

    // Get URLs for each screenshot
    const screenshotsWithUrls = await Promise.all(
      screenshots.map(async (s) => {
        const url = await ctx.storage.getUrl(s.fileId);
        return {
          _id: s._id,
          filename: s.filename,
          fileId: s.fileId, // Include fileId for OCR processing
          url: url || "",
          size: s.size,
          uploadedAt: s.uploadedAt,
        };
      })
    );

    return screenshotsWithUrls;
  },
});

export const getFileUrl = query({
  args: { fileId: v.id("_storage") },
  handler: async (ctx, args) => {
    return await ctx.storage.getUrl(args.fileId);
  },
});

export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => {
    // Generate upload URL for Convex file storage
    return await ctx.storage.generateUploadUrl();
  },
});

