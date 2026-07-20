"""
Dokets VouchAI - Payment & WhatsApp Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from core.security.auth import get_current_user
from core.payments.razorpay_payments import razorpay_escrow
from core.messaging.whatsapp_bot import whatsapp_bot
from core.messaging.notifications import notifications
from config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["Payments & WhatsApp"])

# ========== Payment Routes ==========

@router.post("/payments/create-order")
async def create_payment_order(data: dict, current_user: dict = Depends(get_current_user)):
    """Create a Razorpay escrow order"""
    amount = data.get("amount", 0)
    currency = data.get("currency", "INR")
    contract_id = data.get("contract_id", "PENDING")
    milestone_id = data.get("milestone_id", "PENDING")
    provider_id = data.get("provider_id", "")
    
    order = razorpay_escrow.create_escrow_order(
        customer_id=current_user["user_id"],
        provider_id=provider_id,
        amount=amount,
        currency=currency,
        contract_id=contract_id,
        milestone_id=milestone_id
    )
    
    # Build payment links based on currency
        
    if currency == "INR":
        payment_links = {
            "razorpay": f"https://checkout.razorpay.com/v1/payment/authorize?order_id={order['order_id']}&amount={order['amount']}&key={order.get('razorpay_key', '')}",
            "upi": f"upi://pay?pa=dokets@razorpay&pn=Dokets&am={amount}&cu=INR",
            "paypal": f"https://dokets.com/pay-paypal?order={order['order_id']}&amount={amount}&currency={currency}"
        }
    elif currency == "USD":
        payment_links = {
            "paypal": f"https://www.paypal.com/checkoutnow?token={order['order_id']}&amount={amount}&currency=USD",
            "stripe": f"https://checkout.stripe.com/pay/{order['order_id']}",
            "razorpay": f"https://checkout.razorpay.com/v1/payment/authorize?order_id={order['order_id']}&amount={int(amount*83)}&key={order.get('razorpay_key', '')}"
        }
    elif currency == "EUR":
        payment_links = {
            "paypal": f"https://www.paypal.com/checkoutnow?token={order['order_id']}&amount={amount}&currency=EUR",
            "stripe": f"https://checkout.stripe.com/pay/{order['order_id']}"
        }
    elif currency == "GBP":
        payment_links = {
            "paypal": f"https://www.paypal.com/checkoutnow?token={order['order_id']}&amount={amount}&currency=GBP",
            "stripe": f"https://checkout.stripe.com/pay/{order['order_id']}"
        }
    elif currency in ["BRL", "IDR", "NGN", "PHP", "MXN", "AED", "SAR", "BDT", "PKR"]:
        payment_links = {
            "paypal": f"https://www.paypal.com/checkoutnow?token={order['order_id']}&amount={amount}&currency={currency}",
            "razorpay": f"https://checkout.razorpay.com/v1/payment/authorize?order_id={order['order_id']}&amount={order['amount']}&key={order.get('razorpay_key', '')}"
        }
    else:
        payment_links = {
            "paypal": f"https://dokets.com/pay-paypal?order={order['order_id']}&amount={amount}&currency={currency}"
        }

    return {
        "success": True,
        "data": {
            "order": order,
            "currency": currency,
            "key_id": settings.RAZORPAY_KEY_ID,
            "payment_links": payment_links,
            "supported_methods": list(payment_links.keys()),
            "instructions": f"Choose payment method. Payment held in escrow in {currency} until work verified.",
            "escrow_info": {
                "contract_id": contract_id,
                "milestone_id": milestone_id,
                "released_when": "Work verified by AI or approved by customer"
            }
        }
    }

@router.post("/payments/verify")
async def verify_payment(data: dict, current_user: dict = Depends(get_current_user)):
    """Verify payment signature"""
    payment_id = data.get("payment_id")
    order_id = data.get("order_id")
    signature = data.get("signature")
    
    verified = razorpay_escrow.verify_payment(payment_id, order_id, signature)
    
    return {"success": verified, "message": "Payment verified" if verified else "Verification failed"}

@router.post("/payments/paypal-create")
async def create_paypal_order(data: dict, current_user: dict = Depends(get_current_user)):
    from core.payments.paypal_payments import paypal_payments
    order = paypal_payments.create_order(data.get("amount", 0))
    return {"success": True, "data": order}

# ========== WhatsApp Routes ==========

@router.post("/whatsapp/send")
async def send_whatsapp(data: dict, current_user: dict = Depends(get_current_user)):
    """Send a WhatsApp message"""
    phone = data.get("phone", "")
    message = data.get("message", "")
    
    result = whatsapp_bot.send_message(phone, message)
    
    return {"success": True, "data": result}

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """Receive incoming WhatsApp messages"""
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        message_body = form_data.get("Body", "")
        
        result = whatsapp_bot.process_incoming(from_number, message_body)
        
        if result["action"] == "help":
            whatsapp_bot.send_message(from_number, whatsapp_bot.get_help_message())
        elif result["action"] == "create_contract":
            whatsapp_bot.send_message(
                from_number, 
                f"Creating contract from: '{result['message']}'. Use the Dokets app!"
            )
        
        return {"success": True, "action": result["action"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ========== Notification Routes ==========

@router.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    """Get user notifications"""
    user_notifs = notifications.get_user_notifications(current_user["user_id"])
    return {"success": True, "data": user_notifs, "total": len(user_notifs)}

@router.put("/notifications/{notif_id}/read")
async def mark_read(notif_id: str, current_user: dict = Depends(get_current_user)):
    """Mark notification as read"""
    notifications.mark_read(notif_id)
    return {"success": True, "message": "Marked as read"}

