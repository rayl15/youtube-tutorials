"""
AWS Lambda handler for the CrewAI Research Crew.
Deploy this as a Lambda function with Bedrock permissions.
"""

import json
from main import crew


def handler(event, context):
    topic = event.get("topic", "Latest trends in AI agents")
    result = crew.kickoff(inputs={"topic": topic})
    return {
        "statusCode": 200,
        "body": json.dumps({"topic": topic, "report": str(result)}),
    }
