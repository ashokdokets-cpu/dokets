import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.database.mongodb import mongodb
from api.routes import users, contracts, ai, payments
from api.routes import admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("dokets")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Dokets VouchAI starting...")
    try:
        await mongodb.connect()
        logger.info("Database connected")
    except Exception as e:
        logger.warning(f"Database: {e}")
    yield
    await mongodb.close()
    logger.info("Dokets VouchAI shutting down...")

import os
is_production = os.getenv("ENVIRONMENT") == "production"


app = FastAPI(
    title="Dokets VouchAI API",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(contracts.router)
app.include_router(ai.router)
app.include_router(payments.router)
app.include_router(admin.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dokets VouchAI - Trust in Every Deal</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #0F172A 100%);
                min-height: 100vh;
                color: white;
                overflow-x: hidden;
            }
            .hero {
                max-width: 900px;
                margin: 0 auto;
                padding: 4rem 2rem;
                text-align: center;
            }
            .badge {
                display: inline-block;
                background: rgba(79,70,229,0.3);
                border: 1px solid rgba(79,70,229,0.5);
                padding: 0.4rem 1rem;
                border-radius: 50px;
                font-size: 0.9rem;
                margin-bottom: 2rem;
                animation: fadeIn 1s ease;
            }
            h1 {
                font-size: 3.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #818CF8, #C084FC, #34D399);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 1.5rem;
                animation: slideUp 0.8s ease;
            }
            .subtitle {
                font-size: 1.3rem;
                color: #94A3B8;
                margin-bottom: 3rem;
                line-height: 1.6;
                animation: slideUp 1s ease;
            }
            .cta-buttons {
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
                animation: slideUp 1.2s ease;
            }
            .btn {
                padding: 1rem 2rem;
                border-radius: 12px;
                font-size: 1.1rem;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.3s;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }
            .btn-primary {
                background: linear-gradient(135deg, #4F46E5, #7C3AED);
                color: white;
                box-shadow: 0 4px 15px rgba(79,70,229,0.4);
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(79,70,229,0.6);
            }
            .btn-outline {
                border: 2px solid rgba(255,255,255,0.3);
                color: white;
                background: rgba(255,255,255,0.05);
            }
            .btn-outline:hover {
                background: rgba(255,255,255,0.15);
                transform: translateY(-2px);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                max-width: 900px;
                margin: 4rem auto;
                padding: 0 2rem;
            }
            .feature-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                backdrop-filter: blur(10px);
                transition: all 0.3s;
                animation: fadeIn 1.5s ease;
            }
            .feature-card:hover {
                background: rgba(255,255,255,0.1);
                transform: translateY(-5px);
            }
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            .feature-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            .feature-desc {
                color: #94A3B8;
                font-size: 0.9rem;
                line-height: 1.5;
            }
            .footer {
                text-align: center;
                padding: 2rem;
                color: #64748B;
                font-size: 0.85rem;
            }
            .stats {
                display: flex;
                justify-content: center;
                gap: 3rem;
                margin: 3rem 0;
                animation: slideUp 1.4s ease;
            }
            .stat-item {
                text-align: center;
            }
            .stat-number {
                font-size: 2rem;
                font-weight: 700;
                color: #34D399;
            }
            .stat-label {
                color: #94A3B8;
                font-size: 0.85rem;
            }
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @media (max-width: 640px) {
                h1 { font-size: 2.2rem; }
                .subtitle { font-size: 1rem; }
                .stats { gap: 1.5rem; }
            }
        </style>
    </head>
    <body>
        <div class="hero">
            <div class="badge">🛡️ Powered by AI & Escrow Technology</div>
            <h1>Trust in Every Deal</h1>
            <p class="subtitle">
                Create AI-verified contracts in seconds.<br>
                Your money stays safe in escrow until the work is done.<br>
                <strong>No lawyers. No paperwork. Just trust.</strong>
            </p>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">1%</div>
                    <div class="stat-label">Platform Fee</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">AI Mediation</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">100+</div>
                    <div class="stat-label">Countries</div>
                </div>
            </div>
            
            <div class="cta-buttons">
                <a href="/dashboard" class="btn btn-primary">🎨 Get Started</a>
                <a href="/dashboard" class="btn btn-outline">🎨 Open Dashboard</a>
                <a href="/health" class="btn btn-outline">💚 System Status</a>
            </div>
        </div>

        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI Smart Contracts</div>
                <div class="feature-desc">Just describe the work naturally. Our AI extracts all details and creates a binding contract.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <div class="feature-title">Secure Escrow</div>
                <div class="feature-desc">Payment held securely until AI verifies work completion. Only 1% fee.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⭐</div>
                <div class="feature-title">Vouch Score</div>
                <div class="feature-desc">Build your reputation. Higher scores get more jobs and better rates.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">WhatsApp Ready</div>
                <div class="feature-desc">Create and manage contracts right from WhatsApp. No app needed.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🌍</div>
                <div class="feature-title">Multi-Currency</div>
                <div class="feature-desc">Support for INR, USD, EUR, BRL and more. Works globally.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Instant Setup</div>
                <div class="feature-desc">Create your first contract in under 60 seconds. No registration needed for basic use.</div>
            </div>
        </div>

        <div class="footer">
            <p>© 2026 Dokets VouchAI · Trust in Every Deal · dokets.com</p>
        </div>
    </body>
    </html>
    """

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health():
    db_status = "connected" if mongodb.db is not None else "disconnected"
    return {"status":"healthy","database":db_status,"version":"1.0.0"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*40)
    print("   DOKETS VOUCHAI - Step 2")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs")
    print("="*40 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)