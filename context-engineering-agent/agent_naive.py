"""Naive agent — no context manager, no task context, generic system prompt.

Run this side-by-side with `agent.py` to see how a poorly managed context
makes the model hedge, ask for info it should already have, and miss the point.
"""
import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Vague generic prompt — no role, no rules, no constraints
SYSTEM_PROMPT = "You are a helpful assistant."

# Bloated/stale conversation history. This is what "no context manager" looks like:
# random unrelated turns from earlier in the session leaking into every new request.
conversation_history = [
    {"role": "user", "content": "What time is it in Sydney?"},
    {"role": "assistant", "content": "Sydney is in the AEST/AEDT timezone (UTC+10/+11)."},
    {"role": "user", "content": "Cool. Can you also explain how SSL certificates work?"},
    {"role": "assistant", "content": "Sure! SSL certificates use public-key cryptography to establish encrypted connections..."},
    {"role": "user", "content": "Got it. What's a good Italian restaurant in NYC?"},
    {"role": "assistant", "content": "Some popular Italian restaurants in NYC include Carbone, Don Angie, L'Artusi, and Via Carota..."},
    {"role": "user", "content": "Tell me a joke."},
    {"role": "assistant", "content": "Why did the developer go broke? Because he used up all his cache."},
    {"role": "user", "content": "Hi, I had a question about the return window."},
    {"role": "assistant", "content": "Sure! Most products can be returned within a reasonable time after delivery."},
    {"role": "user", "content": "Actually nevermind, that's resolved."},
    {"role": "assistant", "content": "No problem at all. Let me know if there's anything else I can help with."},
    {"role": "user", "content": "Forget that, I just want to ask about my order."},
    {"role": "assistant", "content": "Of course, I'd be happy to help with your order. What would you like to know?"},
]


def run_naive(user_message: str) -> str:
    conversation_history.append({"role": "user", "content": user_message})
    response = client.invoke_model(
        modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": conversation_history,
        }),
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


if __name__ == "__main__":
    print(run_naive("Where is my order from last week?"))
