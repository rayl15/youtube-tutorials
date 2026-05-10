from crewai import Agent, Task, Crew
from crewai.tools import tool
import subprocess

@tool("read_file")
def read_file(path: str) -> str:
    """Read the full contents of a file from disk."""
    return open(path).read()

@tool("run_command")
def run_command(cmd: str) -> str:
    """Execute a shell command and return stdout."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

researcher = Agent(
    role="File Inspector",
    goal="Read files and summarize them for the user",
    backstory="You are a careful engineer who inspects files on disk.",
    tools=[read_file, run_command],
    llm="gpt-4o",
)

task = Task(
    description="Read the file config.yaml and summarize it.",
    expected_output="A short paragraph summarizing the file.",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[task])
print(crew.kickoff())
