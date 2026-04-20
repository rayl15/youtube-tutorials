# CrewAI + AWS Lambda — Multi-Agent Research System

Companion code for the YouTube tutorial: *Multi-Agent AI on AWS Lambda with CrewAI + Claude Sonnet 4*.

Three AI agents (Researcher → Writer → Reviewer) running on AWS Bedrock, containerized with Docker, deployed as an AWS Lambda function. Trigger it from the terminal and get a full structured research report back.

> 🎥 **Video:** *link when published*

## What's in this folder

| File | Purpose |
|---|---|
| `main.py` | Defines the 3 agents, 3 tasks, and the Crew. Wires CrewAI to AWS Bedrock. |
| `lambda_handler.py` | 6-line Lambda entry point — imports the crew and runs it on an incoming event. |
| `requirements.txt` | `crewai` + `boto3` — the only two packages needed. |
| `Dockerfile` | Container image definition for Lambda (based on `public.ecr.aws/lambda/python:3.12`). |
| `commands.md` | Every AWS CLI command used in the video, in order. |
| `.env.example` | Template for local AWS config. |

## Prerequisites

- Python 3.12
- Docker
- AWS CLI configured with credentials (`aws configure`)
- AWS account with Bedrock access to **Claude Sonnet 4** in `us-east-1`
  (request access in the Bedrock console if you don't have it)

## Quickstart — run locally

```bash
# 1. clone + enter
git clone https://github.com/rayl15/youtube-tutorials.git
cd youtube-tutorials/crewai-aws-multi-agent

# 2. create virtualenv + install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. make sure AWS credentials are configured
aws configure           # or export AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY

# 4. run the crew
python main.py
```

The crew takes 1–3 minutes to run. You'll see each agent's reasoning stream to the terminal, then the final polished report.

## Deploy to AWS Lambda

Full sequence of commands is in [`commands.md`](./commands.md). High-level:

1. Build the container image (`--platform linux/amd64 --provenance=false` if on Apple Silicon)
2. Test the container locally using the Lambda Runtime Interface Emulator
3. Create an ECR repository and push the image
4. Create an IAM role with `AWSLambdaBasicExecutionRole` + `AmazonBedrockFullAccess`
5. Create the Lambda function pointing at the ECR image
6. Invoke it from the terminal

## Pro tips (save yourself hours)

1. **`HOME=/tmp`** — CrewAI writes to `$HOME` on import, but Lambda's filesystem is read-only except `/tmp`. Set this in the Lambda env or you get "Read-only file system" errors.
2. **`--provenance=false`** — without it, Docker on Mac emits a manifest list format Lambda rejects ("image manifest media type not supported").
3. **`--platform=linux/amd64`** — Lambda runs x86; Apple Silicon builds ARM by default.
4. **Memory 1024 MB + timeout 300s** — the defaults (128 MB / 3s) will kill the crew instantly.
5. **AWS CLI v2 wants base64 `--payload`** when invoking Lambda. Pipe your JSON through `base64`.

## Stack

- **CrewAI** 1.14+ — multi-agent framework
- **AWS Bedrock** — Claude Sonnet 4 via cross-region inference (`us.anthropic.claude-sonnet-4-20250514-v1:0`)
- **AWS Lambda** — container image deployment (up to 10 GB)
- **Amazon ECR** — container registry
- **Docker** — `public.ecr.aws/lambda/python:3.12` base image

## License

MIT — see the [top-level LICENSE](../LICENSE).
