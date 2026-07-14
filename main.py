import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.database.mongodb import mongodb
from api.routes import users, contracts, ai, payments, admin, kyc, chat, webhooks, disputes, analytics, advanced, providers

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
app.include_router(kyc.router)
app.include_router(chat.router)
app.include_router(webhooks.router)
app.include_router(disputes.router)
app.include_router(analytics.router)
app.include_router(advanced.router)
app.include_router(providers.router)

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

@app.get("/contract-view/{contract_id}", response_class=HTMLResponse)
async def view_contract(contract_id: str):
    from api.routes.contracts import _contracts
    
    contract = None
    for c in _contracts:
        if c["id"] == contract_id:
            contract = c
            break
    
    if not contract:
        return "<h2>Contract not found</h2>"
    
    milestones_html = ""
    for ms in contract.get("milestones", []):
        milestones_html += f"""
        <div style="background:#F3F4F6;padding:1rem;border-radius:8px;margin-bottom:0.5rem;">
            <strong>{ms.get('title', 'Milestone')}</strong>
            <p>{ms.get('description', '')}</p>
            <p>Amount: {contract.get('currency', 'INR')} {ms.get('amount', 0)}</p>
            <p>Status: <span style="color:#4F46E5;">{ms.get('status', 'pending')}</span></p>
        </div>"""
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{contract['title']} - Dokets VouchAI</title>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family:'Segoe UI',sans-serif; background:#F0F2F5; padding:2rem; }}
            .container {{ max-width:700px; margin:0 auto; }}
            .card {{ background:white; border-radius:12px; padding:2rem; box-shadow:0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background:linear-gradient(135deg,#4F46E5,#7C3AED); color:white; padding:1.5rem; border-radius:12px 12px 0 0; text-align:center; }}
            h1 {{ font-size:1.8rem; }}
            .status {{ display:inline-block; padding:0.3rem 1rem; border-radius:20px; font-weight:600; }}
            .status-draft {{ background:#FEF3C7; color:#92400E; }}
            .btn {{ padding:0.8rem 2rem; border-radius:8px; border:none; cursor:pointer; font-weight:600; font-size:1rem; }}
            .btn-approve {{ background:#10B981; color:white; width:100%; }}
            .btn-approve:hover {{ background:#059669; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ {contract['title']}</h1>
                <p style="margin-top:0.5rem;opacity:0.9;">Dokets VouchAI Contract</p>
            </div>
            <div class="card">
                <p><strong>Contract ID:</strong> {contract['id']}</p>
                <p><strong>Customer:</strong> {contract.get('customer_id', 'N/A')}</p>
                <p><strong>Provider:</strong> {contract.get('provider_phone', 'N/A')}</p>
                <p><strong>Total Amount:</strong> {contract.get('currency', 'INR')} {contract.get('total_amount', 0)}</p>
                <p><strong>Status:</strong> <span class="status status-{contract.get('status', 'draft')}">{contract.get('status', 'draft')}</span></p>
                <p><strong>Created:</strong> {contract.get('created_at', 'N/A')}</p>
                
                <h3 style="margin-top:1.5rem;">Milestones</h3>
                {milestones_html}
                
                <p style="margin-top:1rem;color:#6B7280;font-size:0.9rem;">
                    🔒 Payment secured in escrow | 🤖 AI-verified | ⭐ Vouch Score tracked
                </p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/payment-tracker/{contract_id}", response_class=HTMLResponse)
async def payment_tracker(contract_id: str):
    from api.routes.contracts import _contracts
    
    contract = None
    for c in _contracts:
        if c["id"] == contract_id:
            contract = c
            break
    
    if not contract:
        return "<h2>Contract not found</h2>"
    
    total = contract.get("total_amount", 0)
    currency = contract.get("currency", "INR")
    milestones = contract.get("milestones", [])
    
    paid = sum(ms.get("amount", 0) for ms in milestones if ms.get("status") == "completed")
    pending = total - paid
    
    milestones_html = ""
    for ms in milestones:
        status_color = "#10B981" if ms.get("status") == "completed" else "#F59E0B" if ms.get("status") == "funded" else "#94A3B8"
        status_icon = "✅" if ms.get("status") == "completed" else "🔒" if ms.get("status") == "funded" else "⏳"
        milestones_html += f"""
        <div style="background:white;padding:1rem;border-radius:8px;margin-bottom:0.5rem;border-left:4px solid {status_color};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong>{status_icon} {ms.get('title', 'Milestone')}</strong>
                    <p style="color:#6B7280;font-size:0.9rem;">{ms.get('description', '')}</p>
                </div>
                <div style="text-align:right;">
                    <strong>{currency} {ms.get('amount', 0)}</strong>
                    <p style="font-size:0.8rem;color:{status_color};">{ms.get('status', 'pending').upper()}</p>
                </div>
            </div>
        </div>"""
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Tracker - {contract['title']}</title>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family:'Segoe UI',sans-serif; background:#F0F2F5; padding:2rem; }}
            .container {{ max-width:700px; margin:0 auto; }}
            .card {{ background:white; border-radius:12px; padding:2rem; box-shadow:0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background:linear-gradient(135deg,#4F46E5,#7C3AED); color:white; padding:1.5rem; border-radius:12px; text-align:center; margin-bottom:1rem; }}
            .progress-bar {{ background:#E5E7EB; border-radius:10px; height:20px; margin:1rem 0; overflow:hidden; }}
            .progress-fill {{ background:linear-gradient(90deg,#10B981,#34D399); height:100%; border-radius:10px; transition:width 0.3s; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Payment Tracker</h1>
                <p>{contract['title']}</p>
            </div>
            <div class="card">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;text-align:center;margin-bottom:1rem;">
                    <div><div style="font-size:1.5rem;font-weight:700;">{currency} {total}</div><div style="color:#6B7280;">Total</div></div>
                    <div><div style="font-size:1.5rem;font-weight:700;color:#10B981;">{currency} {paid}</div><div style="color:#6B7280;">Released</div></div>
                    <div><div style="font-size:1.5rem;font-weight:700;color:#F59E0B;">{currency} {pending}</div><div style="color:#6B7280;">In Escrow</div></div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{ (paid/total*100) if total > 0 else 0 }%;"></div>
                </div>
                <p style="text-align:center;color:#6B7280;">{ (paid/total*100) if total > 0 else 0:.0f}% Complete</p>
                
                <h3 style="margin-top:1.5rem;">Milestones</h3>
                {milestones_html}
                
                <p style="margin-top:1rem;text-align:center;color:#6B7280;font-size:0.85rem;">
                    🔒 All payments secured by Dokets VouchAI Escrow
                </p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/verification-result/{contract_id}", response_class=HTMLResponse)
async def verification_result(contract_id: str):
    from api.routes.contracts import _contracts
    
    contract = None
    for c in _contracts:
        if c["id"] == contract_id:
            contract = c
            break
    
    if not contract:
        return "<h2>Not found</h2>"
    
    ms_html = ""
    for ms in contract.get("milestones", []):
        proof = ms.get("proof", {})
        status = ms.get("status", "pending")
        verified = "✅ AI Verified" if status == "completed" else "⏳ Pending" if status == "awaiting_verification" else "🔒 Funded"
        color = "#10B981" if status == "completed" else "#F59E0B" if status == "awaiting_verification" else "#94A3B8"
        
        ms_html += f"""
        <div style="background:white;padding:1.5rem;border-radius:12px;margin-bottom:1rem;border-left:4px solid {color};">
            <h3>{ms.get('title', 'Milestone')}</h3>
            <p>{ms.get('description', '')}</p>
            <p><strong>Amount:</strong> {contract.get('currency', 'INR')} {ms.get('amount', 0)}</p>
            <p><strong>Status:</strong> {verified}</p>
            <p><strong>Proof:</strong> {proof.get('description', 'No proof submitted yet')}</p>
            <p><strong>Images:</strong> {len(proof.get('images', []))} uploaded</p>
        </div>"""
    
    return f"""
    <!DOCTYPE html>
    <html><head>
        <title>Verification - {contract['title']}</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box}}
            body{{font-family:'Segoe UI',sans-serif;background:#F0F2F5;padding:2rem}}
            .container{{max-width:700px;margin:0 auto}}
            .header{{background:linear-gradient(135deg,#4F46E5,#7C3AED);color:white;padding:2rem;border-radius:12px;text-align:center;margin-bottom:1rem}}
            h1{{font-size:1.8rem}}
        </style>
    </head><body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Verification Result</h1>
                <p>{contract['title']}</p>
                <p style="margin-top:1rem;opacity:0.9">Visible to both parties</p>
            </div>
            {ms_html}
            <p style="text-align:center;color:#6B7280;margin-top:1rem;">
                All verifications are AI-powered and visible to both customer and provider
            </p>
        </div>
    </body></html>"""


@app.get("/manifest.json")
async def manifest():
    return {
        "name": "Dokets VouchAI",
        "short_name": "Dokets",
        "start_url": "/dashboard",
        "display": "standalone",
        "background_color": "#0F172A",
        "theme_color": "#4F46E5"
    }


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