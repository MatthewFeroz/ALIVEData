// OCR processing using Tesseract.js
import { action } from "./_generated/server";
import { v } from "convex/values";

// Process OCR using Tesseract.js
export const processOCR = action({
  args: {
    fileId: v.id("_storage"),
  },
  handler: async (ctx, args) => {
    // Get file from Convex storage
    const fileUrl = await ctx.storage.getUrl(args.fileId);
    if (!fileUrl) {
      throw new Error("File not found");
    }

    // Fetch the image
    const response = await fetch(fileUrl);
    const imageBuffer = await response.arrayBuffer();

    // Process OCR with Tesseract.js
    try {
      const { createWorker } = await import("tesseract.js");
      
      const worker = await createWorker("eng");
      try {
        const { data } = await worker.recognize(imageBuffer);
        return {
          text: data.text.trim(),
          processedAt: Date.now(),
        };
      } finally {
        await worker.terminate();
      }
    } catch (error) {
      throw new Error(`OCR processing failed: ${error}`);
    }
  },
});

// Extract terminal command from OCR text
export const extractTerminalCommand = action({
  args: {
    ocrText: v.string(),
  },
  handler: async (ctx, args) => {
    const lines = args.ocrText.split('\n');
    
    // Look for command patterns
    for (const line of lines.reverse()) {
      const trimmed = line.trim();
      
      // Look for prompt patterns: C:\> command or $ command
      if (trimmed.includes('>')) {
        const parts = trimmed.split('>', 2);
        if (parts.length > 1) {
          const command = parts[1].trim();
          if (command && command.length > 3) {
            return command;
          }
        }
      } else if (trimmed.includes('$')) {
        const parts = trimmed.split('$', 2);
        if (parts.length > 1) {
          const command = parts[1].trim();
          if (command && command.length > 3) {
            return command;
          }
        }
      }
      
      // If line looks like a command
      if (trimmed && !trimmed.startsWith('Microsoft') && trimmed.length > 3) {
        if (trimmed.includes(' ') || trimmed.startsWith('git') || trimmed.startsWith('npm')) {
          return trimmed;
        }
      }
    }
    
    // Fallback: return first substantial line
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && trimmed.length > 3) {
        return trimmed;
      }
    }
    
    return args.ocrText.substring(0, 100);
  },
});

