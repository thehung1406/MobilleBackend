def charge(amount: float, method: str) -> tuple[bool, str]:
    # Tích hợp Stripe/PayOS thật ở đây; hiện mock success
    return True, f"TXN-{int(amount*100)}"
