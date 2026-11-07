from config import settings
from groq import Groq
import time

client = Groq(api_key=settings.GROQ_API_KEY)

class Agent:
    def __init__(self, name: str, system_prompt: str) -> None:
        self.name = name
        self.system_prompt = system_prompt

    def __save(self, response) -> None:
            with open("research.md", "w", encoding="utf-8") as file:
                file.write(response)
            print("Research successfully saved.")

    def run(self, task: str) -> None:
        print(f"{self.name} is running...")

        time.sleep(2)

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": task
                }
            ],
            model="openai/gpt-oss-20b",
            max_tokens=4096,
        )
        print(response.choices[0].message.content)
        self.__save(response.choices[0].message.content)

file_path: str = input("Provide file path for task: ")
with open(file_path, "r", encoding="utf-8") as file:
    task = file.read()

research_agent = Agent("Research Agent", settings.researcher_system_prompt)
research_agent.run(task)