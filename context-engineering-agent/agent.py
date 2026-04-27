"""Customer-support agent that uses ContextManager for clean, lean context."""
import boto3
import json
from context_manager import ContextManager

client = boto3.client("bedrock-runtime", region_name="us-east-1")

SYSTEM_PROMPT = """You are a customer support specialist for an e-commerce company.

YOUR KNOWLEDGE:
- Return window: 30 days from delivery
- Standard shipping: 5-7 business days

YOUR BEHAVIOR:
- Greet the customer by their first name when you have it.
- If the task context contains the relevant order, answer directly using those details — do not ask the customer to repeat what you already know.
- Never guess. Never make up order numbers or dates.
- Be concise. One clear answer per response."""

ctx = ContextManager(system_prompt=SYSTEM_PROMPT, max_history_turns=10)


def run_agent(user_message: str, customer_data: dict) -> str:
    # Inject fresh task context — no stale data
    ctx.set_task_context(customer_data)
    ctx.add_turn("user", user_message)

    # Build context — controlled, lean, relevant
    messages = ctx.build_context()
    system = ctx.build_system_prompt()

    response = client.invoke_model(
        modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": system,
            "messages": messages,
        }),
    )
    result = json.loads(response["body"].read())
    text = result["content"][0]["text"]
    ctx.add_turn("assistant", text)
    return text


if __name__ == "__main__":
    customer = {
        "customer_id": "C-48291",
        "name": "Priya Sharma",
        "recent_orders": "Order #98432 — Laptop Stand — Delivered April 18",
    }
    print(run_agent("Where is my order from last week?", customer))
