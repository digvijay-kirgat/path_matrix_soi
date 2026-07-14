# Deployment Guide

This guide provides step-by-step instructions for deploying the Intelligent Route Planning & Adaptive Optimization System to production using Render (for the backend) and Vercel (for the frontend).

## Backend Deployment (Render)

### Prerequisites

- A Render account (https://render.com)
- The backend code pushed to a GitHub repository

### Steps

1.  **Create a new Web Service on Render:**
    - Log in to your Render dashboard
    - Click "New +" and select "Web Service"
    - Connect your GitHub repository
    - Select the repository containing the backend code

2.  **Configure the Service:**
    - **Name:** Choose a name for your service (e.g., `route-planning-api`)
    - **Environment:** Select "Python 3"
    - **Build Command:** `pip install -r backend/requirements.txt`
    - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
    - **Instance Type:** Select an appropriate tier (start with "Free" for testing)

3.  **Set Environment Variables (if needed):**
    - Add any required environment variables in the "Environment" section

4.  **Deploy:**
    - Click "Create Web Service"
    - Render will automatically build and deploy your application
    - Once deployed, you'll receive a public URL (e.g., `https://route-planning-api.onrender.com`)

5.  **Update Frontend Configuration:**
    - Update the API base URL in the frontend to point to your Render deployment URL

### Alternative: Railway

If you prefer Railway instead of Render:

1.  **Create a new project on Railway:**
    - Log in to your Railway account (https://railway.app)
    - Click "New Project"
    - Select "Deploy from GitHub"
    - Connect your repository

2.  **Configure the Service:**
    - Set the start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
    - Railway will automatically detect `requirements.txt` and install dependencies

3.  **Deploy:**
    - Railway will automatically deploy your application
    - You'll receive a public URL for your API

## Frontend Deployment (Vercel)

### Prerequisites

- A Vercel account (https://vercel.com)
- The frontend code pushed to a GitHub repository

### Steps

1.  **Import Project on Vercel:**
    - Log in to your Vercel dashboard
    - Click "Add New..." and select "Project"
    - Click "Import Git Repository"
    - Select your GitHub repository

2.  **Configure the Project:**
    - **Framework Preset:** Select "Vite"
    - **Root Directory:** Select `frontend` (if your frontend is in a subdirectory)
    - **Build Command:** `pnpm build` (or `npm run build`)
    - **Output Directory:** `dist`

3.  **Set Environment Variables:**
    - Add an environment variable for the backend API URL:
      - Key: `VITE_API_URL`
      - Value: `https://your-render-deployment-url.onrender.com` (or your Railway URL)
    - Update the frontend code to use this environment variable:
      ```javascript
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      ```

4.  **Deploy:**
    - Click "Deploy"
    - Vercel will automatically build and deploy your application
    - Once deployed, you'll receive a public URL (e.g., `https://route-planning.vercel.app`)

### Alternative: Netlify

If you prefer Netlify instead of Vercel:

1.  **Connect Repository on Netlify:**
    - Log in to your Netlify account (https://netlify.com)
    - Click "Add new site" and select "Import an existing project"
    - Connect your GitHub repository

2.  **Configure Build Settings:**
    - **Build command:** `cd frontend && pnpm build`
    - **Publish directory:** `frontend/dist`

3.  **Set Environment Variables:**
    - In Site settings → Build & deploy → Environment, add:
      - Key: `VITE_API_URL`
      - Value: Your backend API URL

4.  **Deploy:**
    - Netlify will automatically deploy your application
    - You'll receive a public URL for your frontend

## Post-Deployment Verification

1.  **Test Backend API:**
    - Use curl or Postman to test the API endpoints:
      ```bash
      curl -X POST https://your-api-url.onrender.com/api/part-a/optimize \
        -H "Content-Type: application/json" \
        -d '{"locations": [...], "max_budget": 100, "category_threshold": 2, "k_decay": 0.1}'
      ```

2.  **Test Frontend:**
    - Visit your frontend URL and verify that:
      - The home page loads correctly
      - Navigation between Part A and Part B pages works
      - The forms are functional
      - The maps display correctly

3.  **Test Integration:**
    - Add some locations/requests on the frontend and verify that the backend API is called correctly
    - Check the browser console for any errors

## Continuous Deployment

Both Render and Vercel support continuous deployment. Once configured, any push to your GitHub repository will automatically trigger a new deployment. This ensures that your production environment is always up-to-date with your latest code.

## Troubleshooting

- **Backend not responding:** Check that the backend service is running on Render/Railway and that the API URL in the frontend is correct.
- **Frontend not loading:** Verify that the build command and output directory are correctly configured on Vercel/Netlify.
- **CORS errors:** If you encounter CORS errors, ensure that the backend is configured to accept requests from your frontend URL. You may need to add CORS middleware to the FastAPI application.
- **Environment variables not set:** Double-check that all required environment variables are correctly set in the deployment platform.

---

For more detailed information, refer to the official documentation:
- Render: https://render.com/docs
- Railway: https://docs.railway.app
- Vercel: https://vercel.com/docs
- Netlify: https://docs.netlify.com
