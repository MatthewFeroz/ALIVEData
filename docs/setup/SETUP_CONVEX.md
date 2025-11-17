# Setting Up Convex - Run These Commands

## Step 1: Initialize Convex

Open a terminal in the `frontend` folder and run:

```bash
cd frontend
npx convex dev
```

This will:
1. Ask you to create a Convex account (or login)
2. Create a new project (or select existing)
3. Generate TypeScript types
4. Start the dev server

**Follow the prompts** - it will ask:
- "What would you like to configure?" → Choose "Create a new project"
- Project name → `alive-data` (or your choice)
- Deployment name → Auto-generated or custom

## Step 2: Install OCR Dependency

In the same terminal (after Convex is initialized):

```bash
npm install tesseract.js
```

## Step 3: Set Environment Variables

### In Convex Dashboard:
1. Go to https://dashboard.convex.dev
2. Select your project
3. Go to Settings → Environment Variables
4. Add:
   - `OPENAI_API_KEY` = `sk-your-actual-key-here`

### In Frontend `.env.local`:
Create `frontend/.env.local`:
```
VITE_CONVEX_URL=https://your-deployment-name.convex.cloud
```

(Convex will tell you the URL after initialization)

## Step 4: Copy Schema and Functions

The files are already created in `convex/`:
- ✅ `schema.ts` - Database schema
- ✅ `sessions.ts` - Session management
- ✅ `files.ts` - File handling  
- ✅ `ocr.ts` - OCR processing
- ✅ `ai.ts` - AI documentation
- ✅ `documentation.ts` - Documentation management

Convex will automatically pick them up when you run `npx convex dev`.

## Step 5: Update Frontend

We'll update the frontend components to use Convex hooks instead of the API client.

## What Happens Next

After running `npx convex dev`:
- Convex will watch for changes
- TypeScript types will be generated in `convex/_generated/`
- Your functions will be deployed to Convex cloud
- You'll get a deployment URL

## Troubleshooting

**"Cannot prompt for input"**
- Run `npx convex dev` in an interactive terminal (not script)
- Make sure you're in the `frontend` directory

**"Module not found"**
- Run `npm install` in frontend folder
- Make sure `tesseract.js` is installed

**"OPENAI_API_KEY not found"**
- Set it in Convex dashboard (Settings → Environment Variables)
- Restart `npx convex dev`

## Next Steps After Setup

1. ✅ Convex initialized
2. ✅ Schema deployed
3. ✅ Functions deployed
4. Update frontend to use Convex
5. Test each feature
6. Remove FastAPI backend

