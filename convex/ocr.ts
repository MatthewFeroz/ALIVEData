// OCR processing using external APIs or Tesseract.js
import { action } from "./_generated/server";
import { v } from "convex/values";

// Option 1: Google Cloud Vision API (recommended for production)
async function processWithGoogleVision(imageUrl: string): Promise<string> {
  // You'll need to set up Google Cloud Vision API
  // Install: npm install @google-cloud/vision
  // Set GOOGLE_APPLICATION_CREDENTIALS environment variable
  
  // const vision = require('@google-cloud/vision');
  // const client = new vision.ImageAnnotatorClient();
  // const [result] = await client.textDetection(imageUrl);
  // return result.fullTextAnnotation?.text || '';
  
  throw new Error("Google Vision API not configured");
}

// Option 2: Tesseract.js (free, runs in Node.js)
async function processWithTesseract(imageBuffer: ArrayBuffer): Promise<string> {
  // Install: npm install tesseract.js
  const { createWorker } = await import("tesseract.js");
  
  const worker = await createWorker("eng");
  try {
    const { data } = await worker.recognize(imageBuffer);
    return data.text;
  } finally {
    await worker.terminate();
  }
}

// Option 3: AWS Textract
async function processWithTextract(imageUrl: string): Promise<string> {
  // AWS Textract integration
  // Install: npm install @aws-sdk/client-textract
  throw new Error("AWS Textract not configured");
}

export const processOCR = action({
  args: {
    fileId: v.id("_storage"),
    method: v.optional(v.union(v.literal("tesseract"), v.literal("google"), v.literal("aws"))),
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

    // Process OCR based on method
    const method = args.method || "tesseract";
    let text: string;

    try {
      switch (method) {
        case "tesseract":
          text = await processWithTesseract(imageBuffer);
          break;
        case "google":
          text = await processWithGoogleVision(fileUrl);
          break;
        case "aws":
          text = await processWithTextract(fileUrl);
          break;
        default:
          text = await processWithTesseract(imageBuffer);
      }
    } catch (error) {
      throw new Error(`OCR processing failed: ${error}`);
    }

    return {
      text: text.trim(),
      method,
      processedAt: Date.now(),
    };
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

