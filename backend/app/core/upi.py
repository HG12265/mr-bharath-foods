import urllib.parse
from decimal import Decimal


def generate_upi_link(upi_id: str, amount: Decimal, order_number: str, payee_name: str = "Bharath Delight Foods") -> str:
    """
    Generates a UPI deep link in the format:
    upi://pay?pa=<UPI_ID>&pn=<payee_name>&am=<amount>&cu=INR&tn=<order_number>
    """
    amount_str = f"{amount:.2f}"
    pn_encoded = urllib.parse.quote(payee_name)
    return f"upi://pay?pa={upi_id}&pn={pn_encoded}&am={amount_str}&cu=INR&tn={order_number}"
