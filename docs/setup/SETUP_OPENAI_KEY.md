# Setting Up OpenAI API Key in Convex

## Quick Setup

You need to set your OpenAI API key as an environment variable in Convex. Here's how:

### Option 1: Using Convex CLI (Recommended)

1. **Get your OpenAI API key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key or copy an existing one
   - It should look like: `sk-proj-...`

2. **Set it in Convex:**
   ```bash
   cd frontend
   npx convex env set OPENAI_API_KEY sk-your-actual-key-here
   ```

3. **Verify it's set:**
   ```bash
   npx convex env ls
   ```
   You should see `OPENAI_API_KEY` in the list.

### Option 2: Using Convex Dashboard

1. Go to https://dashboard.convex.dev
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Click **Add Variable**
5. Name: `OPENAI_API_KEY`
6. Value: Your OpenAI API key (starts with `sk-`)
7. Click **Save**

### After Setting the Key

1. **Redeploy functions** (if needed):
   ```bash
   cd frontend
   npx convex dev --once
   ```

2. **Try generating documentation again** - it should work now!

## Important Notes

- ✅ The key is stored securely in Convex (encrypted)
- ✅ It's only accessible to your Convex functions (not the client)
- ✅ You can update it anytime using the same commands
- ⚠️ Never commit your API key to git!

## Troubleshooting

**If you still get errors:**
1. Make sure you're in the `frontend` directory when running commands
2. Verify the key is set: `npx convex env ls`
3. Check the Convex dashboard to confirm the variable exists
4. Make sure your OpenAI account has credits/quota available

## Cost Information

OpenAI API pricing (as of 2024):
- GPT-4o-mini: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
- Each documentation generation uses ~500-2000 tokens typically
- Very affordable for personal use!

