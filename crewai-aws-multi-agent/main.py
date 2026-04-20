"""
CrewAI + AWS Bedrock: Multi-Agent Research System
Three agents (Researcher, Writer, Reviewer) working together on AWS Bedrock.
"""

import os
from crewai import Agent, Task, Crew, Process, LLM

# --- AWS Bedrock LLM Setup ---
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

bedrock_llm = LLM(
    model="bedrock/us.anthropic.claude-sonnet-4-20250514-v1:0",
    temperature=0.7,
    max_tokens=4096,
)

# --- Agent Definitions ---
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find and synthesize the most relevant, accurate, and up-to-date information on the given topic",
    backstory=(
        "You are a senior research analyst with 10 years of experience in "
        "synthesizing complex topics into clear, factual summaries. You focus on "
        "primary sources, recent developments, and verifiable claims. You never "
        "make things up — if you don't know something, you say so."
    ),
    verbose=True,
    llm=bedrock_llm,
    max_iter=10,
)

writer = Agent(
    role="Technical Writer",
    goal="Transform research findings into a well-structured, engaging, and informative report",
    backstory=(
        "You are a technical writer who specializes in making complex topics "
        "accessible to a broad audience. You write in a clear, professional tone "
        "with proper structure — headings, bullet points, and concise paragraphs. "
        "You never add information that wasn't in the research brief."
    ),
    verbose=True,
    llm=bedrock_llm,
    max_iter=10,
)

reviewer = Agent(
    role="Editorial Reviewer",
    goal="Review the report for accuracy, clarity, structure, and completeness",
    backstory=(
        "You are a senior editor with expertise in fact-checking and quality "
        "assurance. You review reports for logical flow, factual accuracy, "
        "grammar, and completeness. You provide specific, actionable feedback "
        "and produce a polished final version."
    ),
    verbose=True,
    llm=bedrock_llm,
    max_iter=10,
)

# --- Task Definitions ---
research_task = Task(
    description=(
        "Research the following topic thoroughly: {topic}\n\n"
        "Gather key facts, recent developments, major players, and emerging trends. "
        "Organize your findings into clear categories. Include specific examples, "
        "statistics, and dates where possible."
    ),
    expected_output=(
        "A structured research brief with categorized findings, key facts, "
        "recent developments, and notable examples. At least 500 words."
    ),
    agent=researcher,
)

write_task = Task(
    description=(
        "Using the research findings provided, write a comprehensive report on: {topic}\n\n"
        "The report should have:\n"
        "- A compelling introduction\n"
        "- 3-5 main sections with clear headings\n"
        "- Specific examples and data points from the research\n"
        "- A conclusion with key takeaways"
    ),
    expected_output=(
        "A well-structured report of 800-1200 words with clear headings, "
        "an introduction, main sections, and a conclusion."
    ),
    agent=writer,
    context=[research_task],
)

review_task = Task(
    description=(
        "Review the report for:\n"
        "1. Factual accuracy — flag anything that seems unsupported\n"
        "2. Structure and flow — ensure logical progression\n"
        "3. Clarity — simplify any overly complex sentences\n"
        "4. Completeness — identify any gaps\n\n"
        "Produce the final polished version of the report."
    ),
    expected_output=(
        "The final polished report with all corrections applied. "
        "Include a brief editorial note at the end summarizing what was changed."
    ),
    agent=reviewer,
    context=[write_task],
)

# --- Crew Assembly ---
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, write_task, review_task],
    process=Process.sequential,
    verbose=True,
)

# --- Run ---
if __name__ == "__main__":
    result = crew.kickoff(
        inputs={"topic": "How AI agents are changing software development in 2025"}
    )
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result)
