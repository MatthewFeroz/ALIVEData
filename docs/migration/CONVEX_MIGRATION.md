# Using Convex for Backend and Database

## What is Convex?

Convex is a modern backend-as-a-service platform that provides:
- **Database**: NoSQL/document database with real-time subscriptions
- **Backend Functions**: Serverless functions (JavaScript/TypeScript)
- **File Storage**: Built-in file upload and storage
- **Real-time**: Automatic real-time updates
- **TypeScript**: Full TypeScript support with type safety

## Can You Use Convex? Yes! But...

### Current Architecture:
- **Backend**: FastAPI (Python)
- **Database**: File system (sessions stored as folders/files)
- **Storage**: Local file system

### Convex Architecture:
- **Backend**: JavaScript/TypeScript functions
- **Database**: Convex database (NoSQL)
- **Storage**: Convex file storage

## Migration Options

### Option 1: Full Migration to Convex (Recommended for New Projects)

**Pros:**
- ✅ Real-time updates (sessions update live)
- ✅ Built-in file storage
- ✅ Type-safe with TypeScript
- ✅ Automatic scaling
- ✅ Free tier available
- ✅ No server management

**Cons:**
- ❌ Need to rewrite backend in JavaScript/TypeScript
- ❌ Python OCR libraries (pytesseract) won't work directly
- ❌ Need alternative for OCR (could use external API or Docker)
- ❌ Migration effort required

**Best For:** If you're willing to rewrite the backend

### Option 2: Hybrid Approach (Convex DB + FastAPI Backend)

**Architecture:**
- **Database**: Convex (sessions, metadata)
- **Backend**: FastAPI (OCR, AI processing)
- **Storage**: Convex file storage

**Pros:**
- ✅ Keep Python backend (OCR, AI)
- ✅ Get Convex database benefits
- ✅ Real-time updates for frontend
- ✅ Less migration needed

**Cons:**
- ⚠️ Two backends to maintain
- ⚠️ More complex architecture
- ⚠️ Need to sync between systems

**Best For:** If you want to keep Python backend but use Convex DB

### Option 3: Convex + External OCR Service

**Architecture:**
- **Backend**: Convex functions
- **Database**: Convex
- **OCR**: External API (Google Vision, AWS Textract, etc.)
- **AI**: OpenAI API (same as now)

**Pros:**
- ✅ Fully serverless
- ✅ Real-time everything
- ✅ No Python backend needed
- ✅ Simpler architecture

**Cons:**
- ❌ OCR costs money (external APIs)
- ❌ Need to rewrite backend
- ❌ Less control over OCR

**Best For:** If you want fully serverless and don't mind OCR costs

## Recommended: Hybrid Approach

Keep your FastAPI backend for OCR/AI processing, but use Convex for:
- Session management
- File storage
- Real-time updates
- Frontend state management

## Implementation Plan for Hybrid Approach

### Step 1: Set Up Convex

```bash
npm install -g convex
cd frontend
npx convex dev
```

### Step 2: Define Schema

Create `convex/schema.ts`:
```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  sessions: defineTable({
    sessionId: v.string(),
    startTime: v.number(),
    pcName: v.optional(v.string()),
    status: v.union(v.literal("active"), v.literal("completed")),
  }),
  
  screenshots: defineTable({
    sessionId: v.id("sessions"),
    filename: v.string(),
    fileId: v.id("_storage"), // Convex file storage ID
    uploadedAt: v.number(),
  }),
  
  ocrResults: defineTable({
    screenshotId: v.id("screenshots"),
    text: v.string(),
    processedAt: v.number(),
  }),
  
  documentation: defineTable({
    sessionId: v.id("sessions"),
    content: v.string(),
    generatedAt: v.number(),
  }),
});
```

### Step 3: Create Convex Functions

Create `convex/sessions.ts`:
```typescript
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const createSession = mutation({
  args: {},
  handler: async (ctx) => {
    const sessionId = crypto.randomUUID();
    const session = await ctx.db.insert("sessions", {
      sessionId,
      startTime: Date.now(),
      status: "active",
    });
    return session;
  },
});

export const listSessions = query({
  handler: async (ctx) => {
    return await ctx.db.query("sessions").collect();
  },
});
```

### Step 4: Update FastAPI to Use Convex

Install Convex client in Python:
```bash
pip install convex
```

Update FastAPI routes to write to Convex:
```python
from convex import ConvexClient

client = ConvexClient("https://your-convex-url.convex.cloud")

@router.post("/sessions")
async def create_session():
    # Create in Convex
    session_id = client.mutation("sessions:createSession")
    # Process OCR/AI in FastAPI
    # Update Convex with results
    return {"session_id": session_id}
```

### Step 5: Update Frontend

Use Convex React hooks for real-time updates:
```typescript
import { useQuery } from "convex/react";
import { api } from "./convex/_generated/api";

function SessionsList() {
  const sessions = useQuery(api.sessions.listSessions);
  // Automatically updates in real-time!
  return <div>{/* render sessions */}</div>;
}
```

## Full Convex Migration (Alternative)

If you want to fully migrate to Convex:

### OCR Options:
1. **Google Cloud Vision API** - Best accuracy, costs money
2. **AWS Textract** - Good for documents, costs money
3. **Tesseract.js** - Free, runs in Node.js (lower accuracy)
4. **Docker container** - Run Python OCR in container, call from Convex

### Implementation:
```typescript
// convex/ocr.ts
import { action } from "./_generated/server";
import { v } from "convex/values";

export const processOCR = action({
  args: { fileId: v.id("_storage") },
  handler: async (ctx, args) => {
    // Option 1: Call external OCR API
    const fileUrl = await ctx.storage.getUrl(args.fileId);
    const ocrResult = await callGoogleVisionAPI(fileUrl);
    return ocrResult;
    
    // Option 2: Use Tesseract.js (limited)
    // const image = await ctx.storage.get(args.fileId);
    // const text = await tesseract.recognize(image);
    // return text;
  },
});
```

## Cost Comparison

### Current (Render + Vercel):
- Render: Free (or $7/month for always-on)
- Vercel: Free
- OpenAI API: Pay per use
- **Total**: ~$0-7/month + API costs

### Convex:
- Convex: Free tier (1M function calls/month)
- File storage: Free tier (1GB)
- OpenAI API: Same
- OCR API: $1-5 per 1000 images (if using external)
- **Total**: ~$0-10/month + API costs

## Recommendation

### For Your Use Case:

**If you want to keep Python OCR:**
→ **Hybrid Approach**: Convex for DB/storage, FastAPI for processing

**If you want fully serverless:**
→ **Full Convex Migration**: Rewrite backend, use external OCR API

**If you want simplest solution:**
→ **Keep current setup**: FastAPI + file system (works fine!)

## Next Steps

1. **Try Convex locally**:
   ```bash
   cd frontend
   npm install convex
   npx convex dev
   ```

2. **Start with hybrid**: Keep FastAPI, add Convex for database

3. **Or go full Convex**: Rewrite backend in TypeScript

Would you like me to:
- Set up Convex integration?
- Create hybrid architecture?
- Show full Convex migration example?

