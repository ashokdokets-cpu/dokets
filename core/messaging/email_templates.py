"""
Dokets VouchAI - Professional Email Templates
"""

def welcome_email(name, verification_link):
    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;background:#F0F2F5;padding:2rem;">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;">
            <div style="background:linear-gradient(135deg,#4F46E5,#7C3AED);color:white;padding:2rem;text-align:center;">
                <h1>Welcome to Dokets VouchAI! 🛡️</h1>
            </div>
            <div style="padding:2rem;">
                <h2>Hi {name},</h2>
                <p>Welcome to the future of trust-based contracts!</p>
                <p>With Dokets VouchAI, you can:</p>
                <ul>
                    <li>🤖 Create AI-powered contracts in seconds</li>
                    <li>🔒 Secure payments with escrow</li>
                    <li>⭐ Build your reputation with Vouch Scores</li>
                </ul>
                <a href="{verification_link}" style="display:inline-block;background:#4F46E5;color:white;padding:1rem 2rem;border-radius:8px;text-decoration:none;font-weight:600;">
                    Verify Your Email
                </a>
                <p style="margin-top:2rem;color:#6B7280;font-size:0.9rem;">
                    Dokets VouchAI - Trust in Every Deal
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def contract_notification(type, contract_details):
    templates = {
        "created": f"Your contract '{contract_details['title']}' has been created with escrow protection.",
        "approved": f"Contract '{contract_details['title']}' has been approved. Work can begin!",
        "completed": f"Contract '{contract_details['title']}' is complete. Payment has been released.",
    }
    return templates.get(type, "Contract update from Dokets VouchAI")

def invoice_template(contract):
    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;">
        <div style="max-width:600px;margin:0 auto;padding:2rem;">
            <h1>Invoice</h1>
            <p>Contract: {contract.get('title')}</p>
            <p>Amount: {contract.get('currency')} {contract.get('total_amount')}</p>
            <p>Status: Paid via Dokets Escrow</p>
            <p style="color:#6B7280;">Dokets VouchAI - Trust in Every Deal</p>
        </div>
    </body>
    </html>
    """