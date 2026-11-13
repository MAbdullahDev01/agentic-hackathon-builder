from src.agents.base_agent import Agent
from src.config import settings

research_agent = Agent("Research Agent", settings.researcher_system_prompt)

file_path: str = input("Provide file path for task: ")
with open(file_path, "r", encoding="utf-8") as file:
    task = file.read()

response = research_agent.run(task)
print(response)