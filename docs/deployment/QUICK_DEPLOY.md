# Quick Deployment Guide

Follow these steps to deploy your ALIVE Data application to production.

## Prerequisites

- ✅ Code is ready for deployment
- ✅ You have a Convex account (sign up at https://convex.dev)
- ✅ You have a Vercel account (sign up at https://vercel.com)
- ✅ You have a WorkOS account (sign up at https://workos.com)
- ✅ You have your API keys ready:
  - OpenAI API key
  - WorkOS Client ID

---

## Step-by-Step Deployment

### 1. Deploy Convex Backend (5 minutes)

```bash
cd frontend
npx convex deploy
```

**Note:** `npx convex deploy` deploys to production by default. There is no `--prod` flag needed.

**What happens:**
- Creates a production deployment
- Deploys all your Convex functions
- Gives you a production URL (save this!)

**After deployment, set environment variables:**
1. Go to https://dashboard.convex.dev
2. Select your project
3. Settings → Environment Variables → **Production**
4. Add:
   - `OPENAI_API_KEY` = `sk-your-key`
   - `WORKOS_CLIENT_ID` = `your-client-id`

**Save your Convex production URL:**
```
https://your-project-prod.convex.cloud
```

---

### 2. Deploy Frontend to Vercel (5 minutes)

#### Option A: Using Vercel CLI

```bash
cd frontend
npm install -g vercel
vercel login
vercel
```

Follow the prompts, then set environment variables:

```bash
vercel env add VITE_CONVEX_URL production
# Paste: https://your-project-prod.convex.cloud

vercel env add VITE_WORKOS_CLIENT_ID production
# Paste: your-workos-client-id

vercel env add VITE_WORKOS_REDIRECT_URI production
# You'll get this after first deployment: https://your-app.vercel.app/callback
```

Then deploy to production:
```bash
vercel --prod
```

#### Option B: Using GitHub + Vercel Dashboard

1. Push your code to GitHub
2. Go to https://vercel.com
3. Click "Add New..." → "Project"
4. Import your repository
5. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Vite (auto-detected)
6. Add Environment Variables:
   - `VITE_CONVEX_URL` = `https://your-project-prod.convex.cloud`
   - `VITE_WORKOS_CLIENT_ID` = `your-workos-client-id`
   - `VITE_WORKOS_REDIRECT_URI` = `https://your-app.vercel.app/callback` (add after first deploy)
7. Click "Deploy"

**Save your Vercel URL:**
```
https://your-app.vercel.app
```

---

### 3. Update WorkOS Redirect URI (2 minutes)

1. Go to https://dashboard.workos.com
2. Authentication → AuthKit → Configuration
3. Add redirect URI: `https://your-app.vercel.app/callback`
4. Save

---

### 4. Update Vercel Environment Variable (1 minute)

After you have your Vercel URL, update the redirect URI:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `VITE_WORKOS_REDIRECT_URI` = `https://your-app.vercel.app/callback`
3. Redeploy: Click "Deployments" → "Redeploy" on latest deployment

Or via CLI:
```bash
vercel env rm VITE_WORKOS_REDIRECT_URI production
vercel env add VITE_WORKOS_REDIRECT_URI production
# Enter: https://your-app.vercel.app/callback
vercel --prod
```

---

### 5. Test Everything (5 minutes)

Visit your deployed app: `https://your-app.vercel.app`

Test:
- [ ] Page loads
- [ ] Sign in button works
- [ ] Authentication redirects correctly
- [ ] Can create a session
- [ ] Can upload a file
- [ ] Documentation generates

---

## Troubleshooting Quick Fixes

**"Missing VITE_CONVEX_URL"**
→ Set environment variable in Vercel and redeploy

**"Authentication not working"**
→ Check redirect URI matches in WorkOS and Vercel env vars

**"Convex functions not found"**
→ Run `npx convex deploy` again

**"Build fails"**
→ Check Vercel build logs, ensure all dependencies are in package.json

---

## What You'll Have After Deployment

- ✅ Production Convex backend: `https://your-project-prod.convex.cloud`
- ✅ Production frontend: `https://your-app.vercel.app`
- ✅ Authentication working via WorkOS
- ✅ All features functional in production

---

## Updating Your Deployment

**Update frontend code:**
```bash
git push origin main  # If using GitHub integration, Vercel auto-deploys
# OR
vercel --prod  # Manual deploy
```

**Update Convex functions:**
```bash
cd frontend
npx convex deploy
```

**Note:** `npx convex deploy` deploys to production by default. There is no `--prod` flag needed.

---

## Need More Details?

See the full deployment guide: [DEPLOYMENT.md](./DEPLOYMENT.md)


