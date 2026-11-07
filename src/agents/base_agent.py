from src.config import settings
from groq import Groq, GroqError

if not settings.GROQ_API_KEY:
    print("API key not found.")

try:
    client = Groq(api_key=settings.GROQ_API_KEY)
except GroqError as e:
    print(f"Failed to create groq client: {e}")

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

        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        response = client.chat.completions.create(
            messages= messages,
            model="openai/gpt-oss-20b",
            max_tokens=4096,
        )
        print(response.choices[0].message.content)
        self.__save(response.choices[0].message.content)