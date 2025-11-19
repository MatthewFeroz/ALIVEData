# Setting Up Environment Variables

This guide shows you exactly where to set your environment variables.

## Step 1: Create `.env.local` File

1. **Navigate to the `frontend` folder** in your project
2. **Create a new file** called `.env.local` (note the dot at the beginning)
3. **Copy this template** into the file:

```env
# Convex Configuration
VITE_CONVEX_URL=your_convex_url_here

# WorkOS AuthKit Configuration
VITE_WORKOS_CLIENT_ID=your_workos_client_id_here
```

## Step 2: Get Your Convex URL

1. Run `npx convex dev` in the `frontend` directory
2. Look for the output that says: `Deployment: https://your-deployment.convex.cloud`
3. Copy that URL
4. Replace `your_convex_url_here` in `.env.local` with your actual URL

**Example:**
```env
VITE_CONVEX_URL=https://happy-animal-123.convex.cloud
```

## Step 3: Get Your WorkOS Client ID

1. **Sign up/Login to WorkOS**: Go to https://dashboard.workos.com
2. **Create a new project** (or select existing)
3. **Set up AuthKit**:
   - Go to **Authentication** → **AuthKit**
   - Click **Set up AuthKit** (if not already set up)
4. **Get your Client ID**:
   - Go to **Configuration** (in the left sidebar)
   - Find **Client ID** - it looks like: `client_01H123ABC456DEF`
   - Copy this value
5. **Replace in `.env.local`**:
   ```env
   VITE_WORKOS_CLIENT_ID=client_01H123ABC456DEF
   ```

## Step 4: Configure Redirect URI in WorkOS

1. In WorkOS Dashboard, go to **Authentication** → **AuthKit** → **Redirects**
2. Click **Add Redirect URI**
3. Add: `http://localhost:5000/callback` (replace 5000 with your actual port)
4. Click **Save**

**To find your port:**
- Look at your terminal when you run `npm run dev`
- It will show something like: `Local: http://localhost:5000`
- Use that port number

## Step 5: Restart Your Dev Server

After creating/updating `.env.local`:

1. **Stop your dev server** (Ctrl+C)
2. **Restart it**: `npm run dev`
3. The environment variables will be loaded

## File Location

Your `.env.local` file should be here:
```
ALIVEData/
  frontend/
    .env.local    ← This file (create it here)
    package.json
    src/
    ...
```

## Example `.env.local` File

```env
# Convex Configuration
VITE_CONVEX_URL=https://happy-animal-123.convex.cloud

# WorkOS AuthKit Configuration  
VITE_WORKOS_CLIENT_ID=client_01H123ABC456DEF

# Optional: Custom redirect URI
# VITE_WORKOS_REDIRECT_URI=http://localhost:5000/callback
```

## Important Notes

- ✅ `.env.local` is in the `frontend` folder (same level as `package.json`)
- ✅ File name starts with a dot: `.env.local` (not `env.local`)
- ✅ No spaces around the `=` sign
- ✅ No quotes needed around values
- ✅ Restart dev server after changes
- ❌ Don't commit `.env.local` to git (it's already in .gitignore)

## Troubleshooting

### "Cannot find .env.local"
- Make sure you're in the `frontend` folder
- Make sure the file name is exactly `.env.local` (with the dot)
- On Windows, you might need to create it as `env.local` first, then rename it

### "Environment variable not loading"
- Restart your dev server after creating/updating `.env.local`
- Make sure there are no typos in variable names (they start with `VITE_`)
- Check that values don't have extra spaces

### "Where do I get the Client ID?"
- WorkOS Dashboard → Configuration → Client ID
- It starts with `client_` followed by letters and numbers

## Next Steps

After setting up `.env.local`:
1. Restart your dev server
2. You should see the auth screen (not a blank screen)
3. Click "Sign In with WorkOS" to test authentication







