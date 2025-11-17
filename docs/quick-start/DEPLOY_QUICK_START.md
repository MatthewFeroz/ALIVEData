# Quick Deployment Guide

## Fastest Option: Render + Vercel (Both Free!)

### 🚀 Deploy Backend (5 minutes)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your repo
   - Settings:
     - **Name**: `alive-data-backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variable**: `OPENAI_API_KEY` = your key
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Copy your backend URL (e.g., `https://alive-data-backend.onrender.com`)

### 🎨 Deploy Frontend (3 minutes)

1. **Update API URL**
   
   Edit `frontend/src/services/api.js`:
   ```javascript
   const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-backend-url.onrender.com/api'
   ```

2. **Deploy on Vercel**
   - Go to https://vercel.com
   - Sign up with GitHub
   - Click "Add New Project"
   - Import your repository
   - Settings:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend`
     - **Environment Variable**: 
       - Key: `VITE_API_URL`
       - Value: `https://your-backend-url.onrender.com/api`
   - Click "Deploy"
   - Wait 2-3 minutes
   - Get your frontend URL (e.g., `https://alive-data.vercel.app`)

3. **Update CORS**
   
   Edit `app/core/config.py` and add your Vercel URL:
   ```python
   CORS_ORIGINS: List[str] = [
       # ... existing URLs ...
       "https://alive-data.vercel.app",  # Your Vercel URL
   ]
   ```
   
   Commit and push - Render will auto-redeploy!

### ✅ Done!

Your app is now live at your Vercel URL!

---

## Alternative: Railway (All-in-One)

1. Go to https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Add environment variable: `OPENAI_API_KEY`
6. Railway auto-detects and deploys!

---

## Need Help?

- Check `DEPLOYMENT.md` for detailed guides
- Render docs: https://render.com/docs
- Vercel docs: https://vercel.com/docs

