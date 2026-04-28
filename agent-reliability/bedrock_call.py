"""Layer 3 in action — Bedrock invoke wrapped with the retry decorator.

The function below didn't have to change at all. We just wrapped it
with ``@retry_with_backoff`` and now it survives Bedrock throttles
automatically. The agent calls ``invoke_claude(...)`` and has no idea
retries are happening underneath.

Same decorator works on any tool that calls an external service —
S3, DynamoDB, Slack API, Stripe — wrap it once, you're resilient.
"""
import boto3
import json

from retry_decorator import retry_with_backoff

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    retryable_errors=[
        # Transient — AWS will recover
        "ThrottlingException",
        "ServiceUnavailableException",
        "ModelStreamErrorException",
        # NOT retryable on this list:
        #   ValidationException        — your input is wrong
        #   AccessDeniedException      — your IAM is wrong
        #   ResourceNotFoundException  — the resource doesn't exist
    ],
)
def invoke_claude(prompt: str, max_tokens: int = 1024) -> str:
    response = bedrock.invoke_model(
        modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }),
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


if __name__ == "__main__":
    # Quick smoke test
    print(invoke_claude("Say 'reliability layer 3 works' in 5 words."))
