"""
Dokets VouchAI - Geographic Auto-Detection
"""

import logging

logger = logging.getLogger("dokets.geo")

# Default currency by country code
COUNTRY_DEFAULTS = {
    "IN": {"currency": "INR", "language": "hi", "locale": "en-IN"},
    "US": {"currency": "USD", "language": "en", "locale": "en-US"},
    "GB": {"currency": "GBP", "language": "en", "locale": "en-GB"},
    "BR": {"currency": "BRL", "language": "pt", "locale": "pt-BR"},
    "ID": {"currency": "IDR", "language": "id", "locale": "id-ID"},
    "NG": {"currency": "NGN", "language": "en", "locale": "en-NG"},
    "PH": {"currency": "PHP", "language": "en", "locale": "en-PH"},
    "MX": {"currency": "MXN", "language": "es", "locale": "es-MX"},
    "AE": {"currency": "AED", "language": "ar", "locale": "ar-AE"},
    "SA": {"currency": "SAR", "language": "ar", "locale": "ar-SA"},
    "BD": {"currency": "BDT", "language": "bn", "locale": "bn-BD"},
    "PK": {"currency": "PKR", "language": "ur", "locale": "ur-PK"},
    "DE": {"currency": "EUR", "language": "de", "locale": "de-DE"},
    "FR": {"currency": "EUR", "language": "fr", "locale": "fr-FR"},
    "ES": {"currency": "EUR", "language": "es", "locale": "es-ES"},
}

def detect_from_phone(phone_number):
    """Detect country from phone number"""
    if phone_number.startswith("+91"): return "IN"
    if phone_number.startswith("+1"): return "US"
    if phone_number.startswith("+44"): return "GB"
    if phone_number.startswith("+55"): return "BR"
    if phone_number.startswith("+62"): return "ID"
    if phone_number.startswith("+234"): return "NG"
    if phone_number.startswith("+63"): return "PH"
    if phone_number.startswith("+52"): return "MX"
    if phone_number.startswith("+971"): return "AE"
    if phone_number.startswith("+966"): return "SA"
    if phone_number.startswith("+880"): return "BD"
    if phone_number.startswith("+92"): return "PK"
    if phone_number.startswith("+49"): return "DE"
    if phone_number.startswith("+33"): return "FR"
    if phone_number.startswith("+34"): return "ES"
    return "IN"  # Default India

def get_country_defaults(country_code):
    return COUNTRY_DEFAULTS.get(country_code, COUNTRY_DEFAULTS["IN"])

def get_smart_defaults(customer_phone, provider_phone):
    """Smart defaults based on both parties"""
    cust_country = detect_from_phone(customer_phone)
    prov_country = detect_from_phone(provider_phone)
    
    # Use provider's currency (they receive payment)
    defaults = get_country_defaults(prov_country)
    
    return {
        "currency": defaults["currency"],
        "language": defaults["language"],
        "customer_country": cust_country,
        "provider_country": prov_country,
        "auto_detected": True
    }