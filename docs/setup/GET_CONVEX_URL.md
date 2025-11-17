# How to Get Your Convex URL

## Method 1: Run Convex Dev (Easiest)

Run this command in the `frontend` folder:

```bash
cd frontend
npx convex dev
```

When Convex starts, it will display:
```
Convex functions ready!
  Dashboard: https://dashboard.convex.dev
  Deployment: https://your-deployment-name.convex.cloud
```

**Copy the Deployment URL** - that's your `VITE_CONVEX_URL`!

## Method 2: Check Convex Dashboard

1. Go to https://dashboard.convex.dev
2. Login to your account
3. Select your project
4. Go to **Settings** → **Deployments**
5. Copy the **Deployment URL** (looks like `https://xxx.convex.cloud`)

## Method 3: Check Configuration Files

After running `npx convex dev`, check:

### `frontend/.convex/` folder
Look for `devUrl.txt` or similar files

### `frontend/.env.local` (if exists)
Should contain:
```
VITE_CONVEX_URL=https://your-deployment.convex.cloud
```

## Method 4: Use Convex CLI

```bash
cd frontend
npx convex env get CONVEX_URL
```

Or check deployment info:
```bash
npx convex deployments list
```

## Quick Setup

Once you have the URL, add it to `frontend/.env.local`:

```bash
# Create .env.local in frontend folder
echo VITE_CONVEX_URL=https://your-deployment.convex.cloud > frontend/.env.local
```

Or manually create `frontend/.env.local`:
```
VITE_CONVEX_URL=https://your-deployment-name.convex.cloud
```

## If Convex Isn't Initialized Yet

Run:
```bash
cd frontend
npx convex dev
```

Follow the prompts:
1. Login or create account
2. Create new project (or select existing)
3. Choose deployment name
4. Copy the URL it shows!

## Troubleshooting

**"No deployment found"**
- Run `npx convex dev` first to initialize

**"Cannot find .convex folder"**
- Convex hasn't been initialized yet
- Run `npx convex dev` to create it

**"URL not showing"**
- Check Convex dashboard: https://dashboard.convex.dev
- Look in Settings → Deployments

