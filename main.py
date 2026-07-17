import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.database.mongodb import mongodb
from api.routes import users, contracts, ai, payments, admin, kyc, chat, webhooks, disputes, analytics, advanced, providers, reviews, favorites, templates, jobs, referrals
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from core.security.limiter import limiter



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
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dokets.com",
        "https://www.dokets.com",
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://checkout.razorpay.com https://cdn.razorpay.com https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://dokets.com https://api.dokets.com https://api.razorpay.com; frame-src 'self' https://api.razorpay.com https://checkout.razorpay.com"
    return response

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
app.include_router(reviews.router)
app.include_router(favorites.router)
app.include_router(templates.router)
app.include_router(jobs.router)
app.include_router(referrals.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    with open("frontend/landing.html", "r", encoding="utf-8") as f:
        return f.read()
    
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/logo.png")
async def logo():
    from fastapi.responses import FileResponse
    return FileResponse("frontend/logo.png")

@app.get("/contract-view/{contract_id}", response_class=HTMLResponse)
async def view_contract(contract_id: str):
    from api.routes.contracts import _contracts
    
    contract = None
    for c in _contracts:
        if c.get("id") == contract_id:
            contract = c
            break
    
    if not contract:
        return f"""
        <!DOCTYPE html><html><head><title>Contract - Dokets</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>body{{font-family:Segoe UI;background:#F0F2F5;padding:2rem;text-align:center}}
        .card{{background:white;max-width:500px;margin:2rem auto;padding:2rem;border-radius:16px;box-shadow:0 4px 6px rgba(0,0,0,0.1)}}</style></head><body>
        <div class="card"><h2>📋 Contract: {contract_id}</h2>
        <p style="color:#6B7280;">View this contract in your dashboard for full details.</p>
        <a href="/dashboard" style="display:inline-block;background:#6366F1;color:white;padding:1rem 2rem;border-radius:8px;text-decoration:none;font-weight:600;margin-top:1rem;">📊 Go to Dashboard</a></div></body></html>"""
    
    milestones_html = ""
    for ms in contract.get("milestones", []):
        milestones_html += f"""
        <div style="background:#F3F4F6;padding:1rem;border-radius:8px;margin-bottom:0.5rem;">
            <strong>{ms.get('title', 'Milestone')}</strong>
            <p>Amount: {contract.get('currency','INR')} {ms.get('amount',0)}</p>
        </div>"""
    
    status_color = {'draft':'#F59E0B','active':'#10B981','completed':'#3B82F6'}.get(contract.get('status'),'#6B7280')
    
    return f"""
    <!DOCTYPE html><html><head><title>{contract['title']} - Dokets</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{{font-family:Segoe UI;background:#F0F2F5;padding:2rem}}
    .container{{max-width:700px;margin:0 auto}}
    .card{{background:white;border-radius:16px;padding:2rem;box-shadow:0 4px 6px rgba(0,0,0,0.1)}}
    .header{{background:linear-gradient(135deg,#6366F1,#8B5CF6);color:white;padding:1.5rem;border-radius:16px 16px 0 0;text-align:center}}
    .status{{display:inline-block;padding:0.3rem 1rem;border-radius:20px;font-weight:600;background:{status_color}20;color:{status_color}}}
</style></head><body><div class="container">
<div class="header"><h1>{contract['title']}</h1><p>Dokets VouchAI Contract</p></div>
<div class="card">
<p><strong>ID:</strong> {contract['id']}</p>
<p><strong>Status:</strong> <span class="status">{contract.get('status','draft').upper()}</span></p>
<p><strong>Amount:</strong> {contract.get('currency','INR')} {contract.get('total_amount',0)}</p>
<p><strong>Provider Phone:</strong> {contract.get('provider_phone','N/A')}</p>
<h3>Milestones</h3>{milestones_html}
<p style="color:#6B7280;margin-top:1rem;">🔒 Secured by Dokets Escrow</p>
</div></div></body></html>"""

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

@app.get("/sitemap.xml")
async def sitemap():
    return Response(content="""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://dokets.com/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://dokets.com/dashboard</loc>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://dokets.com/health</loc>
        <changefreq>monthly</changefreq>
        <priority>0.3</priority>
    </url>
</urlset>""", media_type="application/xml")

@app.get("/robots.txt")
async def robots():
    return Response(content="""User-agent: *
Allow: /
Sitemap: https://dokets.com/sitemap.xml""", media_type="text/plain")

@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return """
    <!DOCTYPE html><html><head><title>Privacy Policy - Dokets VouchAI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:Segoe UI,sans-serif;max-width:800px;margin:0 auto;padding:2rem;line-height:1.6;color:#1E293B;}
    h1{color:#6366F1;}h2{color:#4F46E5;margin-top:2rem;}a{color:#6366F1;}</style></head><body>
    <h1>🔒 Privacy Policy</h1><p>Last updated: July 2026</p>
    <p>Dokets VouchAI ("we," "our," or "us") is committed to protecting your privacy.</p>
    <h2>1. Information We Collect</h2>
    <p>• Email address and phone number for account creation<br>
    • Contract details (title, description, amount)<br>• KYC documents for identity verification<br>
    • Payment information (processed securely by Razorpay/PayPal)</p>
    <h2>2. How We Use Your Data</h2>
    <p>• To create and manage your contracts<br>• To process escrow payments<br>
    • To verify your identity (KYC)<br>• To calculate Vouch Scores<br>• To send notifications</p>
    <h2>3. Data Storage</h2>
    <p>Data is stored on MongoDB Atlas cloud servers with encryption at rest and in transit. 
    We retain your data as long as your account is active.</p>
    <h2>4. Data Sharing</h2>
    <p>We do NOT sell your data. We share data only:<br>
    • With the other party in your contract<br>• With payment processors (Razorpay, PayPal)<br>
    • When required by law</p>
    <h2>5. Your Rights (GDPR)</h2>
    <p>• Right to access your data<br>• Right to correct inaccurate data<br>
    • Right to delete your data<br>• Right to data portability<br>
    • Right to object to processing</p>
    <h2>6. Cookies</h2>
    <p>We use essential cookies for authentication. No tracking cookies. 
    See our <a href="/cookies">Cookie Policy</a>.</p>
    <h2>7. Security</h2>
    <p>• SSL/TLS encryption for all data<br>• JWT tokens for authentication<br>
    • Passwords hashed with bcrypt<br>• Regular security audits</p>
    <h2>8. Contact</h2>
    <p>📧 contact@dokets.com<br>🌐 <a href="/">dokets.com</a></p>
    <p><a href="/">← Back to Home</a></p></body></html>"""

@app.get("/terms", response_class=HTMLResponse)
async def terms():
    return """
    <!DOCTYPE html><html><head><title>Terms of Service - Dokets VouchAI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:Segoe UI,sans-serif;max-width:800px;margin:0 auto;padding:2rem;line-height:1.6;color:#1E293B;}
    h1{color:#6366F1;}h2{color:#4F46E5;margin-top:2rem;}a{color:#6366F1;}</style></head><body>
    <h1>📋 Terms of Service</h1><p>Last updated: July 2026</p>
    <h2>1. Acceptance of Terms</h2>
    <p>By using Dokets VouchAI, you agree to these terms. If you disagree, do not use the service.</p>
    <h2>2. Service Description</h2>
    <p>Dokets VouchAI provides an AI-powered escrow platform for creating and managing contracts 
    between service providers and customers.</p>
    <h2>3. Platform Fee</h2>
    <p>We charge a 1% platform fee on all transactions processed through our escrow system.</p>
    <h2>4. Escrow Terms</h2>
    <p>Funds are held in escrow until work is verified by AI or approved by the customer. 
    Disputes are resolved through our AI mediation system.</p>
    <h2>5. User Responsibilities</h2>
    <p>• Provide accurate information<br>• Complete work as agreed<br>
    • Make payments as promised<br>• Maintain professional conduct</p>
    <h2>6. Limitation of Liability</h2>
    <p>Dokets VouchAI is not liable for the quality of work performed or disputes between parties. 
    Our liability is limited to the platform fee collected.</p>
    <h2>7. Termination</h2>
    <p>We reserve the right to terminate accounts that violate these terms or engage in fraudulent activity.</p>
    <h2>8. Governing Law</h2>
    <p>These terms are governed by Indian law. Disputes subject to Hyderabad jurisdiction.</p>
    <p><a href="/">← Back to Home</a></p></body></html>"""

@app.get("/cookies", response_class=HTMLResponse)
async def cookies():
    return """
    <!DOCTYPE html><html><head><title>Cookie Policy - Dokets VouchAI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:Segoe UI,sans-serif;max-width:800px;margin:0 auto;padding:2rem;line-height:1.6;color:#1E293B;}
    h1{color:#6366F1;}h2{color:#4F46E5;margin-top:2rem;}a{color:#6366F1;}
    .cookie-box{background:#F8FAFC;padding:1rem;border-radius:8px;margin:1rem 0;border-left:4px solid #6366F1;}</style></head><body>
    <h1>🍪 Cookie Policy</h1><p>Last updated: July 2026</p>
    <h2>What Are Cookies?</h2>
    <p>Cookies are small text files stored on your device when you visit websites.</p>
    <h2>Cookies We Use</h2>
    <div class="cookie-box"><strong>Essential Cookies</strong><br>
    • JWT Token: For authentication (required)<br>• Theme Preference: Dark/Light mode<br>
    • Language Preference: Your selected language</div>
    <div class="cookie-box"><strong>NO Tracking Cookies</strong><br>
    We do NOT use tracking cookies, advertising cookies, or third-party analytics cookies.</div>
    <h2>Managing Cookies</h2>
    <p>You can clear cookies from your browser settings. However, this will log you out.</p>
    <h2>Third-Party Services</h2>
    <p>• Razorpay: May set cookies for payment processing<br>• Twilio: For WhatsApp messaging</p>
    <p><a href="/">← Back to Home</a></p></body></html>"""

@app.get("/about", response_class=HTMLResponse)
async def about():
    return """
    <!DOCTYPE html><html><head><title>About - Dokets VouchAI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:Segoe UI,sans-serif;max-width:800px;margin:0 auto;padding:2rem;line-height:1.6;color:#1E293B;}
    h1{color:#6366F1;}h2{color:#4F46E5;margin-top:2rem;}a{color:#6366F1;}
    .feature{background:#F8FAFC;padding:1rem;border-radius:8px;margin:0.5rem 0;border-left:4px solid #6366F1;}</style></head><body>
    <h1>🛡️ About Dokets VouchAI</h1>
    <p>Dokets VouchAI is the world's first AI-powered micro-escrow platform, 
    designed to bring trust to the informal economy.</p>
    <h2>Our Mission</h2>
    <p>To make every deal trustworthy - no lawyers, no paperwork, just AI-powered trust.</p>
    <h2>Why Dokets?</h2>
    <div class="feature">🤖 <strong>AI-Powered</strong> - Contracts created from natural language</div>
    <div class="feature">🔒 <strong>Secure Escrow</strong> - Payment held until work verified</div>
    <div class="feature">💬 <strong>WhatsApp Native</strong> - Create contracts via chat</div>
    <div class="feature">⭐ <strong>Vouch Score</strong> - Build your reputation</div>
    <div class="feature">🌍 <strong>Global</strong> - 13 currencies, 13 KYC types, 6 languages</div>
    <h2>Contact</h2>
    <p>📧 <a href="mailto:contact@dokets.com">contact@dokets.com</a><br>🌐 <a href="https://dokets.com">dokets.com</a></p>
    <p><a href="/">← Back to Home</a></p></body></html>"""

@app.get("/contact", response_class=HTMLResponse)
async def contact():
    return """
    <!DOCTYPE html><html><head><title>Contact - Dokets VouchAI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:Segoe UI,sans-serif;max-width:800px;margin:0 auto;padding:2rem;line-height:1.6;color:#1E293B;}
    h1{color:#6366F1;}h2{color:#4F46E5;margin-top:2rem;}a{color:#6366F1;}
    .contact-method{background:#F8FAFC;padding:1rem;border-radius:8px;margin:0.5rem 0;border-left:4px solid #6366F1;}</style></head><body>
    <h1>📞 Contact Us</h1>
    <div class="contact-method">📧 <strong>Email:</strong> <a href="mailto:contact@dokets.com">contact@dokets.com</a></div>
    <div class="contact-method">💬 <strong>WhatsApp:</strong> +91 9100014859</div>
    <div class="contact-method">🌐 <strong>Website:</strong> <a href="https://dokets.com">dokets.com</a></div>
    <div class="contact-method">📊 <strong>Dashboard:</strong> <a href="/dashboard">Go to Dashboard</a></div>
    <h2>Support Hours</h2>
    <p>We respond to all inquiries within 24 hours.</p>
    <p><a href="/">← Back to Home</a></p></body></html>"""

@app.get("/gdpr", response_class=HTMLResponse)
async def gdpr():
    return """
    <!DOCTYPE html><html><head><title>GDPR Compliance - Dokets VouchAI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:Segoe UI,sans-serif;max-width:800px;margin:0 auto;padding:2rem;line-height:1.6;color:#1E293B;}
    h1{color:#6366F1;}h2{color:#4F46E5;margin-top:2rem;}a{color:#6366F1;}</style></head><body>
    <h1>🇪🇺 GDPR Compliance</h1><p>Last updated: July 2026</p>
    <p>Dokets VouchAI is committed to GDPR compliance for our European users.</p>
    <h2>Your GDPR Rights</h2>
    <p>✅ Right to Access<br>✅ Right to Rectification<br>✅ Right to Erasure<br>
    ✅ Right to Restrict Processing<br>✅ Right to Data Portability<br>✅ Right to Object</p>
    <h2>Data Processing</h2>
    <p>We process data based on: Contract necessity, Legal obligation, Legitimate interest, and Consent.</p>
    <h2>Data Protection Officer</h2>
    <p>📧 contact@dokets.com</p>
    <h2>Request Your Data</h2>
    <p>Email us at contact@dokets.com to exercise any of your GDPR rights.</p>
    <p><a href="/">← Back to Home</a></p></body></html>"""


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