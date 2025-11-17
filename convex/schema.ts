// Convex schema for ALIVE Data
// Run: npx convex dev to generate types

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  sessions: defineTable({
    sessionId: v.string(),
    startTime: v.number(),
    endTime: v.optional(v.number()),
    pcName: v.optional(v.string()),
    pcNameAbbrev: v.optional(v.string()),
    status: v.union(
      v.literal("active"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("error")
    ),
    screenshotCount: v.optional(v.number()),
    durationSeconds: v.optional(v.number()),
  }).index("by_sessionId", ["sessionId"]),

  screenshots: defineTable({
    sessionId: v.id("sessions"),
    filename: v.string(),
    fileId: v.id("_storage"), // Convex file storage
    uploadedAt: v.number(),
    size: v.optional(v.number()),
  })
    .index("by_session", ["sessionId"])
    .index("by_uploaded", ["uploadedAt"]),

  ocrResults: defineTable({
    screenshotId: v.id("screenshots"),
    sessionId: v.id("sessions"),
    text: v.string(),
    processedAt: v.number(),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("error")
    ),
  })
    .index("by_screenshot", ["screenshotId"])
    .index("by_session", ["sessionId"]),

  documentation: defineTable({
    sessionId: v.id("sessions"),
    content: v.string(),
    generatedAt: v.number(),
    ocrText: v.optional(v.string()),
    commandHistory: v.optional(v.array(v.any())),
  }).index("by_session", ["sessionId"]),
  
  ocrProcessing: defineTable({
    screenshotId: v.id("screenshots"),
    sessionId: v.id("sessions"),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("error")
    ),
    text: v.optional(v.string()),
    error: v.optional(v.string()),
    processedAt: v.optional(v.number()),
  })
    .index("by_screenshot", ["screenshotId"])
    .index("by_session", ["sessionId"]),
});

