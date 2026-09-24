# RailOptix Render Deployment Guide

This guide explains how to deploy the RailOptix backend and frontend to Render using Render PostgreSQL as the production database. **Supabase is NOT required.**

---

## 1. Create the Render PostgreSQL Database

1. Go to your **Render Dashboard** (https://dashboard.render.com).
2. Click **New** -> **PostgreSQL**.
3. Name it (e.g., `railoptix-db`) and select the Free tier.
4. Click **Create Database**.
5. Once created, scroll down to **Connections** and copy the **Internal Database URL** (if deploying the backend on Render) or **External Database URL**.

---

## 2. Deploy the Backend (FastAPI)

1. Click **New** -> **Web Service**.
2. Connect your GitHub repository: `sanketpatankar1-ai/Railoptix.ai`.
3. Configure the following settings:
   - **Name:** `railoptix-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

4. Expand **Environment Variables** and add:
   - `DATABASE_URL`: *(Paste the PostgreSQL connection URL from Step 1)*
   - `SECRET_KEY`: *(A random secure string, e.g., `RailoptixSecureSuperKey2026!@`)*
   - `CORS_ORIGINS`: `https://railoptix-frontend.onrender.com` *(The future URL of your frontend)*
   - `PYTHON_VERSION`: `3.11.9`
   - `ENVIRONMENT`: `production`

5. Click **Create Web Service**.

> **Note on Migrations and Seeding:** RailOptix automatically uses SQLAlchemy `create_all` to initialize missing tables when `uvicorn` starts. If the database is completely empty, it will auto-run the internal seed script (`backend.seed.seed_data.run_seed(db)` using bulk operations). You do NOT need to run Alembic or manual seed scripts.

---

## 3. Deploy the Frontend (React / Vite)

1. Click **New** -> **Static Site**.
2. Connect the same GitHub repository.
3. Configure the following settings:
   - **Name:** `railoptix-frontend`
   - **Build Command:** `cd client && npm install && npm run build`
   - **Publish Directory:** `client/dist`

4. Expand **Environment Variables** and add:
   - `VITE_API_URL`: `https://railoptix-api.onrender.com` *(Replace with your actual backend Render URL)*

5. Expand **Redirects/Rewrites** (under Advanced):
   - **Source:** `/*`
   - **Destination:** `/index.html`
   - **Action:** `Rewrite`

6. Click **Create Static Site**.

---

## 4. Production Testing

1. Open your frontend URL (e.g., `https://railoptix-frontend.onrender.com`).
2. Log in using `admin@railoptix.gov.in` / `Admin@123`.
3. The dashboard will load data directly from your Render PostgreSQL instance.
4. Verify the backend Health Check by visiting: `https://railoptix-api.onrender.com/api/health`

---

## Development vs Production

- **Local Development:** Continues to use the `DATABASE_URL` specified in your local `.env` (which defaults to your local Mac PostgreSQL if omitted).
- **Production (Render):** Uses the managed Render PostgreSQL cluster via the `DATABASE_URL` environment variable you configured in the dashboard.
