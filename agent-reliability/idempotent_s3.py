"""Layer 2 — check-before-create (idempotency pattern #2).

When your tool creates something — an S3 bucket, a Lambda function,
a row in a database — don't just call ``create`` blind. Check if it
already exists. If it does, return success without doing anything.
The LLM gets the same success message either way; it doesn't need to
know which path was taken.
"""
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3", region_name="us-east-1")


def create_or_update_bucket(name: str) -> str:
    """Create the bucket — or return success if it already exists.
    Calling this twice does the same thing as calling it once."""
    # 1. Check if it already exists
    try:
        s3.head_bucket(Bucket=name)
        return f"OK: bucket '{name}' already exists"
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code != "404":
            # Anything other than 404 is a real problem (auth, region, etc.)
            return f"ERROR: cannot check bucket: {code}"

    # 2. Create it
    s3.create_bucket(Bucket=name)
    return f"OK: created bucket '{name}'"
