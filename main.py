import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.database.mongodb import mongodb
from api.routes import users, contracts, ai, payments

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

app = FastAPI(
    title="Dokets VouchAI API",
    version="1.0.0",
    docs_url="/docs",
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

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html><html><head><title>Dokets VouchAI</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;color:white}
.container{text-align:center;padding:2rem}
h1{font-size:3rem;margin-bottom:.5rem}
.links{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin-top:2rem}
.links a{color:white;text-decoration:none;padding:.8rem 1.5rem;border:2px solid rgba(255,255,255,.3);border-radius:10px;transition:.3s}
.links a:hover{background:rgba(255,255,255,.2)}
</style></head><body><div class="container">
<h1>Dokets VouchAI</h1><p>AI-Powered Trust Platform</p>
<div class="links"><a href="/docs">API Docs</a><a href="/health">Health Check</a></div>
<p style="margin-top:1rem;opacity:0.7">v1.0.0 | Step 2</p>
</div></body></html>"""

@app.get("/health")
async def health():
    db_status = "connected" if mongodb.db else "disconnected"
    return {"status":"healthy","database":db_status,"version":"1.0.0"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*40)
    print("   DOKETS VOUCHAI - Step 2")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs")
    print("="*40 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)