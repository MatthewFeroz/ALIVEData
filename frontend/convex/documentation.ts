// Documentation management
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";

export const generateDocumentation = mutation({
  args: {
    sessionId: v.string(),
    ocrText: v.optional(v.string()),
    commandHistory: v.optional(
      v.array(
        v.object({
          command: v.string(),
          timestamp: v.number(),
          screenshotPath: v.optional(v.string()),
        })
      )
    ),
    includeScreenshots: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    // Require authentication
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated. Please sign in to generate documentation.");
    }

    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();

    if (!session) {
      throw new Error("Session not found");
    }

    // Verify user owns this session
    // Sessions without userId (old sessions) cannot be modified
    if (!session.userId || session.userId !== identity.tokenIdentifier) {
      throw new Error("You don't have permission to generate documentation for this session");
    }

    let documentation: string;

    if (args.ocrText) {
      // Generate from OCR text using action
      // Note: We need to call the action directly, not schedule it
      const summary = await ctx.runAction(api.ai.summarizeText, {
        ocrText: args.ocrText,
      });
      documentation = summary;
    } else if (args.commandHistory && args.commandHistory.length > 0) {
      // Generate from command history
      const summary = await ctx.runAction(api.ai.summarizeCommands, {
        commandHistory: args.commandHistory,
        includeScreenshots: args.includeScreenshots ?? true,
      });
      documentation = summary;
    } else {
      throw new Error("Either ocrText or commandHistory must be provided");
    }

    // Save documentation
    const docId = await ctx.db.insert("documentation", {
      sessionId: session._id,
      content: documentation,
      generatedAt: Date.now(),
      ocrText: args.ocrText,
      commandHistory: args.commandHistory,
    });

    // Update session status
    await ctx.db.patch(session._id, {
      status: "completed",
      endTime: Date.now(),
      durationSeconds: Math.floor((Date.now() - session.startTime) / 1000),
    });

    return {
      documentationId: docId,
      documentation,
      sessionId: args.sessionId,
    };
  },
});

export const saveDocumentation = mutation({
  args: {
    sessionId: v.string(),
    ocrText: v.optional(v.string()),
    documentation: v.string(),
  },
  handler: async (ctx, args) => {
    // Require authentication
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated. Please sign in to generate documentation.");
    }

    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();

    if (!session) {
      throw new Error("Session not found");
    }

    // Verify user owns this session
    // Sessions without userId (old sessions) cannot be modified
    if (!session.userId || session.userId !== identity.tokenIdentifier) {
      throw new Error("You don't have permission to generate documentation for this session");
    }

    // Check if documentation already exists
    const existingDoc = await ctx.db
      .query("documentation")
      .withIndex("by_session", (q) => q.eq("sessionId", session._id))
      .first();

    if (existingDoc) {
      // Update existing documentation
      await ctx.db.patch(existingDoc._id, {
        content: args.documentation,
        generatedAt: Date.now(),
        ocrText: args.ocrText,
      });
      return { documentationId: existingDoc._id, documentation: args.documentation };
    } else {
      // Create new documentation
      const docId = await ctx.db.insert("documentation", {
        sessionId: session._id,
        content: args.documentation,
        generatedAt: Date.now(),
        ocrText: args.ocrText,
      });

      // Update session status
      await ctx.db.patch(session._id, {
        status: "completed",
        endTime: Date.now(),
        durationSeconds: Math.floor((Date.now() - session.startTime) / 1000),
      });

      return { documentationId: docId, documentation: args.documentation };
    }
  },
});

export const getDocumentation = query({
  args: { sessionId: v.string() },
  handler: async (ctx, args) => {
    // Require authentication
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return null;
    }

    const session = await ctx.db
      .query("sessions")
      .withIndex("by_sessionId", (q) => q.eq("sessionId", args.sessionId))
      .first();

    if (!session) {
      return null;
    }

    // Verify user owns this session
    // Sessions without userId (old sessions) are not accessible
    if (!session.userId || session.userId !== identity.tokenIdentifier) {
      return null;
    }

    const doc = await ctx.db
      .query("documentation")
      .withIndex("by_session", (q) => q.eq("sessionId", session._id))
      .first();

    return doc;
  },
});

