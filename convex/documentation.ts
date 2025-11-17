// Documentation management
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";

export const generateDocumentation = mutation({
  args: {
    sessionId: v.id("sessions"),
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
    const session = await ctx.db.get(args.sessionId);
    if (!session) {
      throw new Error("Session not found");
    }

    let documentation: string;

    if (args.ocrText) {
      // Generate from OCR text
      const summary = await ctx.scheduler.runAfter(
        0,
        api.ai.summarizeText,
        {
          ocrText: args.ocrText,
        }
      );
      documentation = summary;
    } else if (args.commandHistory && args.commandHistory.length > 0) {
      // Generate from command history
      const summary = await ctx.scheduler.runAfter(
        0,
        api.ai.summarizeCommands,
        {
          commandHistory: args.commandHistory,
          includeScreenshots: args.includeScreenshots ?? true,
        }
      );
      documentation = summary;
    } else {
      throw new Error("Either ocrText or commandHistory must be provided");
    }

    // Save documentation
    const docId = await ctx.db.insert("documentation", {
      sessionId: args.sessionId,
      content: documentation,
      generatedAt: Date.now(),
      ocrText: args.ocrText,
      commandHistory: args.commandHistory,
    });

    // Update session status
    await ctx.db.patch(args.sessionId, {
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

export const getDocumentation = query({
  args: { sessionId: v.id("sessions") },
  handler: async (ctx, args) => {
    const doc = await ctx.db
      .query("documentation")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .first();

    return doc;
  },
});

export const listDocumentation = query({
  handler: async (ctx) => {
    return await ctx.db.query("documentation").collect();
  },
});

