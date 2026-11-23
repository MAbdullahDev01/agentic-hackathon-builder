from src.agents.base_agent import Agent
from src.config import settings

if __name__ == "__main__":
    research_agent = Agent("Research Agent", settings.researcher_system_prompt)

    task_file_path: str = input("Provide file path for task: ")
    with open(task_file_path, "r", encoding="utf-8") as file:
        task = file.read()

    file_path: str = input("Provide file path to save research report: ")
    
    response = research_agent.run(task, file_path)
    print(response)