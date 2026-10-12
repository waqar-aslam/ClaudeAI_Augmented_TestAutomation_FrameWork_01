"""Card values taken from test_data/payment.json, used to check that reports never contain them."""
import json
from pathlib import Path

_PAYMENT_JSON = Path(__file__).resolve().parent.parent / "test_data" / "payment.json"


def card_values() -> dict[str, str]:
    """Card numbers (with and without spaces) from the test data. CVV/name are too short to scan reliably."""
    data = json.loads(_PAYMENT_JSON.read_text())
    numbers = [data["valid"]["card_number"], data["distinct_card_values"]["card_number"]]
    out = {}
    for n in numbers:
        out[f"card number {n[:4]}…"] = n
        out[f"card number {n[:4]}… (no spaces)"] = n.replace(" ", "")
    return out
