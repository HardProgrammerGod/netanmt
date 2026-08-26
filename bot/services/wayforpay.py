import hmac
import hashlib
import time
from typing import Dict, Any
from bot.config import (
    WAYFORPAY_MERCHANT_ACCOUNT,
    WAYFORPAY_SECRET_KEY,
    WAYFORPAY_DOMAIN,
    WEBHOOK_BASE_URL,
)

def generate_signature(string_to_hash: str) -> str:
    """Генерує HMAC-MD5 підпис для WayForPay."""
    return hmac.new(
        WAYFORPAY_SECRET_KEY.encode('utf-8'),
        string_to_hash.encode('utf-8'),
        hashlib.md5
    ).hexdigest()

def create_payment_link(order_id: str, amount: float, product_name: str) -> str:
    """Генерує посилання на оплату або форму WayForPay."""
    order_date = int(time.time())
    currency = "UAH"
    
    # Рядок для генерації merchantSignature згідно з документацією WayForPay
    # merchantAccount;merchantDomainName;orderReference;orderDate;amount;currency;productName;productCount;productPrice
    signature_data = f"{WAYFORPAY_MERCHANT_ACCOUNT};{WAYFORPAY_DOMAIN};{order_id};{order_date};{amount};{currency};{product_name};1;{amount}"
    merchant_signature = generate_signature(signature_data)

    # Вебхук, куди WayForPay надішле результат
    service_url = f"{WEBHOOK_BASE_URL.rstrip('/')}/payment/callback"

    # Сформоване посилання на оплату
    # (Можна також генерувати HTML-форму із редіректом)
    payment_url = (
        f"https://secure.wayforpay.com/pay?"
        f"merchantAccount={WAYFORPAY_MERCHANT_ACCOUNT}&"
        f"merchantDomainName={WAYFORPAY_DOMAIN}&"
        f"orderReference={order_id}&"
        f"orderDate={order_date}&"
        f"amount={amount}&"
        f"currency={currency}&"
        f"productName={product_name}&"
        f"productCount=1&"
        f"productPrice={amount}&"
        f"merchantSignature={merchant_signature}&"
        f"serviceUrl={service_url}"
    )
    return payment_url

def verify_callback_signature(data: Dict[str, Any]) -> bool:
    """Перевіряє підпис відповді від WayForPay (Callback)."""
    # Поля для генерації підпису відповіді:
    # merchantAccount;orderReference;amount;currency;authCode;cardPan;transactionStatus;reasonCode;createdDate
    keys = [
        "merchantAccount", "orderReference", "amount", "currency",
        "authCode", "cardPan", "transactionStatus", "reasonCode", "createdDate"
    ]
    sign_str = ";".join([str(data.get(k, "")) for k in keys])
    expected_signature = generate_signature(sign_str)
    
    return data.get("merchantSignature") == expected_signature
