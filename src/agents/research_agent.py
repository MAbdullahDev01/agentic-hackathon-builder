from src.agents.base_agent import Agent
from src.config import settings

file_path: str = input("Provide file path for task: ")
with open(file_path, "r", encoding="utf-8") as file:
    task = file.read()

research_agent = Agent("Research Agent", settings.researcher_system_prompt)
research_agent.run(task)