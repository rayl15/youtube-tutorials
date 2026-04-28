"""Layer 2 — idempotency keys for external APIs (idempotency pattern #3).

When your agent calls something like Stripe or any system where a
duplicate call causes real damage, you send an idempotency key. A
unique ID for that operation. The server deduplicates on its end —
even if your agent fires the same request twice, the server processes
it once and returns the original result on subsequent calls.

Most modern APIs support this:
  * Stripe (``idempotency_key`` header)
  * AWS APIs (``ClientRequestToken`` on most create operations)
  * Square, Mollie, GoCardless, …
"""
import hashlib
import json


def make_idempotency_key(operation: str, payload: dict) -> str:
    """Same inputs → same key → server deduplicates."""
    blob = json.dumps({"op": operation, **payload}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:32]


def charge_customer(customer_id: str, cents: int, reason: str) -> str:
    """Demo charge function. In real use this would call Stripe / Square /
    your payment processor with the idempotency_key. The key here is a
    deterministic hash of the inputs, so retrying produces the same key
    and the server returns the original charge instead of creating a new one."""
    payload = {"customer_id": customer_id, "amount": cents, "reason": reason}
    key = make_idempotency_key("charge", payload)

    # In real use:
    #     stripe.Charge.create(**payload, idempotency_key=key)
    # If `key` is reused within Stripe's 24-hour window, Stripe returns
    # the original Charge instead of creating a new one.

    return f"OK: charged customer {customer_id} ${cents/100:.2f} (key={key[:8]}...)"
