# Supported currencies with conversion rates (would use live API in production)
CURRENCIES = {
    "INR": {"symbol": "₹", "name": "Indian Rupee", "rate": 1},
    "USD": {"symbol": "$", "name": "US Dollar", "rate": 0.012},
    "EUR": {"symbol": "€", "name": "Euro", "rate": 0.011},
    "GBP": {"symbol": "£", "name": "British Pound", "rate": 0.0095},
    "BRL": {"symbol": "R$", "name": "Brazilian Real", "rate": 0.058},
    "IDR": {"symbol": "Rp", "name": "Indonesian Rupiah", "rate": 190},
    "NGN": {"symbol": "₦", "name": "Nigerian Naira", "rate": 18},
    "PHP": {"symbol": "₱", "name": "Philippine Peso", "rate": 0.67},
    "MXN": {"symbol": "MX$", "name": "Mexican Peso", "rate": 0.20},
    "AED": {"symbol": "د.إ", "name": "UAE Dirham", "rate": 0.044},
    "SAR": {"symbol": "﷼", "name": "Saudi Riyal", "rate": 0.045},
}

def get_supported_currencies():
    return [{"code": k, **v} for k, v in CURRENCIES.items()]

def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    from_rate = CURRENCIES[from_currency]["rate"]
    to_rate = CURRENCIES[to_currency]["rate"]
    return round(amount * (to_rate / from_rate), 2)