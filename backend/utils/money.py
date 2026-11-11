"""Money helpers. The database stores whole paise; screens show rupees with 2 decimals."""
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def rupees_to_paise(value):
    """'1250.50' -> 125050. Raises ValueError if the text is not a valid amount."""
    try:
        amount = Decimal(str(value).replace(",", "").strip())
    except InvalidOperation:
        raise ValueError("Invalid amount")
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def paise_to_display(paise):
    """125050 -> '₹1,250.50'  (Indian digit grouping: ₹1,00,000.00)."""
    sign = "-" if paise < 0 else ""
    rupees, rest = divmod(abs(int(paise)), 100)
    digits = str(rupees)
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        digits = ",".join(groups + [tail])
    return f"{sign}₹{digits}.{rest:02d}"