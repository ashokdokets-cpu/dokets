"""
Dokets VouchAI - Invoice Generator
"""

import uuid
from datetime import datetime

def generate_invoice(contract):
    """Generate invoice data for a contract"""
    invoice = {
        "invoice_number": f"INV-{uuid.uuid4().hex[:8].upper()}",
        "date": str(datetime.utcnow()),
        "contract_id": contract.get("id"),
        "title": contract.get("title"),
        "customer": contract.get("customer_id"),
        "provider": contract.get("provider_id", "Pending"),
        "amount": contract.get("total_amount"),
        "currency": contract.get("currency", "INR"),
        "platform_fee": round(contract.get("total_amount", 0) * 0.01, 2),
        "net_amount": round(contract.get("total_amount", 0) * 0.99, 2),
        "status": contract.get("status"),
        "payment_method": "Escrow via Dokets VouchAI",
        "download_url": f"https://dokets.com/invoice/{contract.get('id')}"
    }
    return invoice

def get_invoice_html(invoice):
    return f"""
    <html>
    <head><title>Invoice {invoice['invoice_number']}</title>
    <style>
        body {{ font-family:Arial; padding:2rem; }}
        .header {{ border-bottom:2px solid #4F46E5; padding-bottom:1rem; }}
        .amount {{ font-size:2rem; color:#4F46E5; }}
        table {{ width:100%; border-collapse:collapse; margin:1rem 0; }}
        td {{ padding:0.5rem; border-bottom:1px solid #E5E7EB; }}
    </style></head>
    <body>
        <div class="header">
            <h1>Dokets VouchAI</h1>
            <p>Invoice #{invoice['invoice_number']}</p>
            <p>Date: {invoice['date']}</p>
        </div>
        <table>
            <tr><td>Contract</td><td>{invoice['title']}</td></tr>
            <tr><td>Amount</td><td class="amount">{invoice['currency']} {invoice['amount']}</td></tr>
            <tr><td>Platform Fee (1%)</td><td>{invoice['currency']} {invoice['platform_fee']}</td></tr>
            <tr><td><strong>Net Amount</strong></td><td><strong>{invoice['currency']} {invoice['net_amount']}</strong></td></tr>
            <tr><td>Status</td><td>{invoice['status']}</td></tr>
        </table>
        <p style="color:#6B7280;">Payment secured by Dokets VouchAI Escrow</p>
    </body></html>
    """