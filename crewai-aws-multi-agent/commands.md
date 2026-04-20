# CLI Commands — CrewAI + AWS Lambda Deployment

Follow these commands in order during the video recording.
All commands tested and verified working on 2026-04-17.

---

## Part 1: Local Setup & Run

```bash
# Create project folder
mkdir crewai-aws-multi-agent && cd crewai-aws-multi-agent

# Install CrewAI
pip install crewai

# Run locally (after writing main.py)
python main.py
```

---

## Part 2: Docker Build

```bash
# Build Docker image for Lambda
# --platform linux/amd64  → because we're on Mac (ARM), Lambda needs x86
# --provenance=false       → Lambda doesn't support manifest lists with attestations
docker build --platform linux/amd64 --provenance=false -t crewai-lambda .
```

---

## Part 3: Test Lambda Locally

```bash
# Run the container locally (Lambda Runtime Interface Emulator)
docker run --platform linux/amd64 -d --name crewai-test \
  -p 9000:8080 \
  -e AWS_ACCESS_KEY_ID="$(aws configure get aws_access_key_id)" \
  -e AWS_SECRET_ACCESS_KEY="$(aws configure get aws_secret_access_key)" \
  -e AWS_DEFAULT_REGION="us-east-1" \
  crewai-lambda:latest

# Trigger it with curl
curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"topic": "How AI agents are changing software development in 2026"}' | python3 -m json.tool

# Cleanup local test
docker stop crewai-test && docker rm crewai-test
```

---

## Part 4: Push to ECR

```bash
# Set variables (replace AWS_ACCOUNT_ID with your own)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1
REPO_NAME=crewai-lambda

# Create ECR repository
aws ecr create-repository \
  --repository-name $REPO_NAME \
  --region $AWS_REGION

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag the image
docker tag crewai-lambda:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest
```

---

## Part 5: Create IAM Role for Lambda

```bash
# Create the trust policy
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name crewai-lambda-role \
  --assume-role-policy-document file://trust-policy.json

# Attach basic Lambda execution policy (for CloudWatch logs)
aws iam attach-role-policy \
  --role-name crewai-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach Bedrock access policy
aws iam attach-role-policy \
  --role-name crewai-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Wait for IAM to propagate
sleep 10
```

---

## Part 6: Create Lambda Function

```bash
# Create the Lambda function from container image
# --timeout 300       → 5 minutes (crew takes 1-3 min to run)
# --memory-size 1024  → 1GB RAM (CrewAI needs it)
# --environment       → HOME=/tmp because Lambda filesystem is read-only
#                        except /tmp. CrewAI tries to write config on import.
aws lambda create-function \
  --function-name crewai-research-crew \
  --package-type Image \
  --code ImageUri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/crewai-lambda-role \
  --timeout 300 \
  --memory-size 1024 \
  --environment 'Variables={HOME=/tmp,CREWAI_STORAGE_DIR=/tmp/crewai}' \
  --region $AWS_REGION

# Wait for function to become active
aws lambda wait function-active-v2 --function-name crewai-research-crew
echo "Lambda is ACTIVE and ready!"
```

---

## Part 7: Trigger Lambda on AWS (The Money Shot)

```bash
# Invoke the Lambda function
# Note: payload must be base64 encoded for AWS CLI v2
aws lambda invoke \
  --function-name crewai-research-crew \
  --payload "$(echo '{"topic": "How AI agents are changing software development in 2026"}' | base64)" \
  --cli-read-timeout 300 \
  output.json

# View the result (pretty printed)
cat output.json | python3 -m json.tool

# Or extract just the report text
python3 -c "
import json
with open('output.json') as f:
    data = json.load(f)
body = json.loads(data['body'])
print(body['report'])
"
```

---

## Cleanup (after recording)

```bash
# Delete Lambda function
aws lambda delete-function --function-name crewai-research-crew

# Delete ECR repository (--force removes all images)
aws ecr delete-repository --repository-name crewai-lambda --force --region $AWS_REGION

# Delete IAM role (must detach policies first)
aws iam detach-role-policy --role-name crewai-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name crewai-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam delete-role --role-name crewai-lambda-role

# Remove local files
rm trust-policy.json output.json
```

---

## Gotchas We Hit (mention in video)

1. **`--provenance=false` on Docker build** — Without this, Docker creates a manifest list with attestations that Lambda doesn't support. You'll get "image manifest media type not supported."

2. **`HOME=/tmp` environment variable** — CrewAI tries to write to the home directory on import (for its RAG/knowledge storage). Lambda's filesystem is read-only except `/tmp`. Without this, you get "Read-only file system" on the first invoke.

3. **Base64 payload** — AWS CLI v2 expects the `--payload` to be base64 encoded. Raw JSON will give you a weird parsing error with special characters.

4. **5-minute timeout** — The default Lambda timeout is 3 seconds. A three-agent crew takes 1-3 minutes. Set `--timeout 300`.

5. **1024MB memory** — CrewAI with all its dependencies needs more than the default 128MB. 1024MB works well.
