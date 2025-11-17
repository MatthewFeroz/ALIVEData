# Deployment Guide for ALIVE Data Web Application

## Overview

Your application has two parts:
1. **Backend**: FastAPI (Python) - needs to run continuously
2. **Frontend**: React/Vite - static files that can be served

## Deployment Options

### Option 1: All-in-One Platforms (Easiest)
- **Render** (Recommended) - Free tier, easy setup
- **Railway** - Simple deployment
- **Fly.io** - Good for Docker
- **Heroku** - Popular but requires credit card

### Option 2: Separate Hosting
- **Backend**: Render/Railway/Fly.io
- **Frontend**: Vercel/Netlify (Free, excellent for React)

### Option 3: VPS/Server
- **DigitalOcean**, **Linode**, **AWS EC2**
- More control, requires server management

## Recommended: Render (Backend) + Vercel (Frontend)

This is the easiest and free option for most use cases.

---

## Deployment Option 1: Render (Backend) + Vercel (Frontend)

### Part A: Deploy Backend to Render

#### Step 1: Prepare for Production

1. **Create `render.yaml`** (already created below)
2. **Create `Procfile`** for Render
3. **Update CORS settings** for production

#### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

#### Step 3: Deploy on Render

1. Go to https://render.com
2. Sign up/login with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name**: `alive-data-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     ```
     OPENAI_API_KEY=your-actual-api-key
     ```
6. Click **"Create Web Service"**

#### Step 4: Get Backend URL

After deployment, Render gives you a URL like:
`https://alive-data-backend.onrender.com`

### Part B: Deploy Frontend to Vercel

#### Step 1: Update Frontend API URL

Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-backend-url.onrender.com/api'
```

#### Step 2: Create `vercel.json` (already created below)

#### Step 3: Deploy to Vercel

**Option A: Via Vercel CLI**
```bash
cd frontend
npm install -g vercel
vercel
```

**Option B: Via GitHub (Recommended)**
1. Push frontend to GitHub
2. Go to https://vercel.com
3. Import your repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Environment Variables**:
     ```
     VITE_API_URL=https://your-backend-url.onrender.com/api
     ```
5. Click **"Deploy"**

---

## Deployment Option 2: Railway (All-in-One)

### Step 1: Prepare Files

Create `railway.json` and `Procfile` (see below)

### Step 2: Deploy

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Python and deploys backend
6. Add environment variable: `OPENAI_API_KEY`

### Step 3: Deploy Frontend

1. In Railway, add another service
2. Select frontend directory
3. Build command: `cd frontend && npm install && npm run build`
4. Start command: Serve static files (Railway handles this)

---

## Deployment Option 3: Docker (Any Platform)

### Step 1: Create Dockerfile

See `Dockerfile` below

### Step 2: Build and Deploy

```bash
# Build
docker build -t alive-data .

# Run locally
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key alive-data

# Push to Docker Hub
docker tag alive-data yourusername/alive-data
docker push yourusername/alive-data
```

Deploy to:
- **Fly.io**: `flyctl launch`
- **DigitalOcean App Platform**: Use Dockerfile
- **AWS ECS**: Use Docker image

---

## Production Configuration

### Environment Variables Needed

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
OPENAI_MODEL=gpt-4o-mini
CORS_ORIGINS=https://your-frontend-domain.com
PORT=8000  # Usually set by platform
```

### CORS Configuration

Update `app/core/config.py` to include your frontend domain:

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "https://your-frontend-domain.vercel.app",  # Add your frontend URL
]
```

---

## Post-Deployment Checklist

- [ ] Backend is accessible (test API endpoint)
- [ ] Frontend can connect to backend
- [ ] CORS is configured correctly
- [ ] Environment variables are set
- [ ] File uploads work (check upload directory permissions)
- [ ] Static files are served correctly
- [ ] API documentation is accessible at `/docs`

---

## Troubleshooting

### Backend Issues

**502 Bad Gateway**
- Check if backend is running
- Verify start command is correct
- Check logs in Render/Railway dashboard

**CORS Errors**
- Add frontend URL to `CORS_ORIGINS` in config
- Restart backend after config change

**File Upload Fails**
- Check write permissions for `uploads/` directory
- Some platforms need persistent storage (Render requires paid plan)

### Frontend Issues

**API Connection Failed**
- Verify `VITE_API_URL` environment variable
- Check backend URL is correct
- Ensure backend is running

**Build Fails**
- Check Node.js version (should be 16+)
- Run `npm install` locally first
- Check for TypeScript/ESLint errors

---

## Cost Estimates

### Free Tier Options:
- **Render**: Free tier (spins down after 15min inactivity)
- **Vercel**: Free tier (excellent for frontend)
- **Railway**: $5/month minimum
- **Fly.io**: Free tier available

### Paid Options:
- **Render**: $7/month (always-on)
- **DigitalOcean**: $6/month (Droplet)
- **AWS**: Pay-as-you-go

---

## Security Considerations

1. **Never commit `.env` file** (already in .gitignore ✓)
2. **Use environment variables** for API keys
3. **Enable HTTPS** (most platforms do this automatically)
4. **Set up rate limiting** (consider adding to FastAPI)
5. **Validate file uploads** (already implemented ✓)

---

## Next Steps

1. Choose your deployment platform
2. Follow the specific guide above
3. Test thoroughly after deployment
4. Set up monitoring (optional)
5. Configure custom domain (optional)

