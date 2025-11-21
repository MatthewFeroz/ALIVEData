# Deployment Guide for ALIVE Data Web Application

## Overview

Your application has two parts:
1. **Backend**: Convex (serverless) - automatically deployed
2. **Frontend**: React/Vite - deploy to Vercel

## Architecture

- **Convex Backend**: Serverless backend that handles database, file storage, and server functions
- **Vercel Frontend**: React/Vite frontend that connects to Convex
- **WorkOS**: Authentication provider (configured in both Convex and frontend)

---

## Deployment Steps

### Step 1: Deploy Convex Backend to Production

Convex automatically deploys when you run `npx convex deploy`. The dev deployment (`npx convex dev`) is for development only.

#### 1.1: Deploy Convex Functions

```bash
cd frontend
npx convex deploy
```

**Note:** `npx convex deploy` deploys to production by default. There is no `--prod` flag needed.

**First time:**
- This will prompt you to create a production deployment
- You'll get a production deployment URL (different from dev URL)
- Example: `https://your-project-prod.convex.cloud`

#### 1.2: Set Production Environment Variables in Convex

1. Go to https://dashboard.convex.dev
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Make sure these are set for **Production**:
   - `OPENAI_API_KEY` = `sk-your-openai-api-key`
   - `WORKOS_CLIENT_ID` = `your-workos-client-id`

**Note**: Convex has separate environment variables for dev and production. Make sure to set them for the production deployment.

#### 1.3: Get Production Convex URL

After deploying, you'll see:
```
Deployment URL: https://your-project-prod.convex.cloud
```

**Save this URL** - you'll need it for the frontend deployment.

---

### Step 2: Configure WorkOS for Production

#### 2.1: Update Redirect URI in WorkOS Dashboard

1. Go to https://dashboard.workos.com
2. Navigate to **Authentication** → **AuthKit** → **Configuration**
3. Add your production redirect URI:
   - `https://your-app.vercel.app/callback`
   - (You'll get the exact URL after deploying to Vercel)

**Important**: You can add multiple redirect URIs, so keep your dev URI (`http://localhost:5173/callback`) and add the production one.

---

### Step 3: Deploy Frontend to Vercel

#### Option A: Deploy via Vercel CLI (Recommended for first deployment)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   cd frontend
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

   Follow the prompts:
   - **Set up and deploy?** → Yes
   - **Which scope?** → Your account
   - **Link to existing project?** → No (first time)
   - **What's your project's name?** → `alive-data` (or your choice)
   - **In which directory is your code located?** → `./` (current directory)
   - **Want to override settings?** → No (first time)

4. **Set Environment Variables**:
   After the first deployment, you'll be asked to set environment variables, or you can set them in the Vercel dashboard:
   
   ```bash
   vercel env add VITE_CONVEX_URL
   # Enter: https://your-project-prod.convex.cloud
   
   vercel env add VITE_WORKOS_CLIENT_ID
   # Enter: your-workos-client-id
   
   vercel env add VITE_WORKOS_REDIRECT_URI
   # Enter: https://your-app.vercel.app/callback
   ```

5. **Redeploy with environment variables**:
   ```bash
   vercel --prod
   ```

#### Option B: Deploy via GitHub (Recommended for CI/CD)

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Import to Vercel**:
   - Go to https://vercel.com
   - Click **"Add New..."** → **"Project"**
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
     - **Install Command**: `npm install`

3. **Set Environment Variables** in Vercel Dashboard:
   - Go to **Settings** → **Environment Variables**
   - Add:
     - `VITE_CONVEX_URL` = `https://your-project-prod.convex.cloud`
     - `VITE_WORKOS_CLIENT_ID` = `your-workos-client-id`
     - `VITE_WORKOS_REDIRECT_URI` = `https://your-app.vercel.app/callback`
   
   **Important**: Make sure to set these for **Production**, **Preview**, and **Development** environments.

4. **Deploy**:
   - Click **"Deploy"**
   - Vercel will automatically deploy on every push to your main branch

---

### Step 4: Update WorkOS Redirect URI

After you get your Vercel deployment URL:

1. Go to WorkOS Dashboard
2. Add the production redirect URI: `https://your-app.vercel.app/callback`
3. Save changes

---

## Post-Deployment Checklist

- [ ] Convex backend deployed to production (`npx convex deploy`)
- [ ] Production environment variables set in Convex dashboard
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set in Vercel dashboard
- [ ] WorkOS redirect URI updated with production URL
- [ ] Test authentication flow in production
- [ ] Test file uploads
- [ ] Test session creation
- [ ] Test documentation generation

---

## Environment Variables Summary

### Convex Dashboard (Production)
```
OPENAI_API_KEY=sk-your-key
WORKOS_CLIENT_ID=your-client-id
```

### Vercel Dashboard (Production)
```
VITE_CONVEX_URL=https://your-project-prod.convex.cloud
VITE_WORKOS_CLIENT_ID=your-client-id
VITE_WORKOS_REDIRECT_URI=https://your-app.vercel.app/callback
```

---

## Troubleshooting

### Frontend can't connect to Convex

**Symptoms**: "Missing VITE_CONVEX_URL" error or connection failures

**Solutions**:
- Verify `VITE_CONVEX_URL` is set in Vercel environment variables
- Make sure you're using the **production** Convex URL (not dev URL)
- Check that the environment variable is set for the correct environment (Production)
- Redeploy after setting environment variables: `vercel --prod`

### Authentication not working

**Symptoms**: Sign in button doesn't work, redirect errors

**Solutions**:
- Verify `VITE_WORKOS_CLIENT_ID` is set in Vercel
- Check that redirect URI in WorkOS matches your Vercel URL exactly
- Make sure `WORKOS_CLIENT_ID` is set in the Convex production environment
- Check browser console for specific error messages

### Build fails on Vercel

**Symptoms**: Deployment fails during build step

**Solutions**:
- Check build logs in Vercel dashboard
- Ensure `package.json` has correct build script: `"build": "vite build"`
- Verify Node.js version (Vercel auto-detects, but you can set it in `package.json`)
- Make sure all dependencies are in `package.json` (not just `package-lock.json`)

### Convex functions not working

**Symptoms**: API calls fail, "function not found" errors

**Solutions**:
- Verify Convex is deployed: `npx convex deploy`
- Check Convex dashboard logs for errors
- Ensure environment variables are set for **production** deployment (not just dev)
- Check that your functions are in the `convex/` directory

### Environment variables not updating

**Symptoms**: Changes to env vars don't take effect

**Solutions**:
- **Vercel**: After adding/updating env vars, you must redeploy: `vercel --prod` or trigger a new deployment
- **Convex**: Environment variables are updated immediately, but you may need to redeploy functions: `npx convex deploy`

---

## Updating Your Deployment

### Update Frontend

1. Make your changes
2. Commit and push to GitHub (if using GitHub integration)
3. Vercel will automatically redeploy
4. Or manually deploy: `vercel --prod`

### Update Convex Backend

1. Make changes to files in `frontend/convex/`
2. Deploy: `npx convex deploy`
3. Changes are live immediately

### Update Environment Variables

**Vercel**:
- Update in Vercel dashboard → Settings → Environment Variables
- Redeploy: `vercel --prod`

**Convex**:
- Update in Convex dashboard → Settings → Environment Variables
- Make sure to update **Production** environment
- No redeploy needed, but you may want to: `npx convex deploy`

---

## Custom Domain Setup

### Vercel Custom Domain

1. Go to Vercel dashboard → Your project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
4. Update `VITE_WORKOS_REDIRECT_URI` to use your custom domain
5. Update WorkOS redirect URI to match

### Convex Custom Domain

Convex deployments use `.convex.cloud` domains by default. Custom domains are available on paid plans.

---

## Cost Estimates

### Free Tier (Sufficient for development/small projects)

- **Convex**: 
  - Free tier: 1M function calls/month, 1GB storage, 1GB bandwidth
  - Perfect for development and small projects
- **Vercel**: 
  - Free tier: Unlimited deployments, 100GB bandwidth
  - Perfect for frontend hosting
- **WorkOS**: 
  - Free tier: 1,000 MAU (Monthly Active Users)
  - Perfect for small applications

### Paid Plans (When you need more)

- **Convex**: Starts at $25/month (more function calls, storage, bandwidth)
- **Vercel**: Starts at $20/month (more bandwidth, team features)
- **WorkOS**: Starts at $99/month (more MAU, advanced features)

---

## Security Best Practices

1. ✅ **Never commit `.env.local`** - Already in `.gitignore`
2. ✅ **Use environment variables** - All secrets are in environment variables
3. ✅ **HTTPS enabled** - Vercel and Convex use HTTPS by default
4. ✅ **Authentication required** - All Convex functions check authentication
5. ✅ **User isolation** - Users can only access their own data

---

## Monitoring and Logs

### Convex Logs

- View in Convex Dashboard → Logs
- See function calls, errors, and performance metrics
- Filter by function, time range, etc.

### Vercel Logs

- View in Vercel Dashboard → Your project → Deployments → Click deployment → Logs
- See build logs, runtime errors, and function logs

### WorkOS Logs

- View in WorkOS Dashboard → Logs
- See authentication events, errors, and user activity

---

## Next Steps

1. ✅ Deploy Convex backend: `npx convex deploy`
2. ✅ Deploy frontend to Vercel
3. ✅ Set all environment variables
4. ✅ Test everything in production
5. ✅ Set up custom domain (optional)
6. ✅ Configure monitoring/alerts (optional)

---

## Quick Reference Commands

```bash
# Deploy Convex to production
cd frontend
npx convex deploy

# Deploy frontend to Vercel (first time)
cd frontend
vercel

# Deploy frontend to Vercel (production)
cd frontend
vercel --prod

# View Convex dashboard
npx convex dashboard

# View Vercel dashboard
vercel
```

---

## Need Help?

- **Convex Docs**: https://docs.convex.dev
- **Vercel Docs**: https://vercel.com/docs
- **WorkOS Docs**: https://workos.com/docs
- **Project Docs**: See `docs/` directory for detailed setup guides
