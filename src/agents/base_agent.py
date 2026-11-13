from groq import Groq, GroqError
from groq.types.chat import ChatCompletionMessage
import json
from src.config import settings
from src.tools.registry import tools, tool_registry

if settings.GROQ_API_KEY == "":
    raise ValueError("API key not found.")

try:
    client = Groq(api_key=settings.GROQ_API_KEY)
except GroqError as e:
    print(f"Failed to create groq client: {e}")

class Agent:
    def __init__(self, name: str, system_prompt: str) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_registry = tool_registry
        self.messages: list[dict[str, str | ChatCompletionMessage]] = [{"role": "system", "content": self.system_prompt}]

    def save(self, response) -> None:
        with open("research.md", "w", encoding="utf-8") as file:
            file.write(response)
        print("Research successfully saved.")

    def add_message(self, role: str, message: str | ChatCompletionMessage):
        self.messages.append({"role": role, "content": message})
    
    def run(self, task: str) -> ChatCompletionMessage:

        print(f"{self.name} is running...")

        self.add_message("user", task)

        for iteration in range(settings.MAX_ITERATIONS):
            # For logging while running
            # print("Model called")
            response = client.chat.completions.create(
                messages=self.messages,
                model="openai/gpt-oss-20b",
                max_tokens=4096,
                tools=self.tools,
            ).choices[0].message

            # Check whether the model requested tools
            if response.tool_calls:

                # Preserve the assistant's tool-call message
                self.messages.append(response.model_dump(exclude_none=True))


                for tool_call in response.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Validate the requested tool
                    if tool_name not in self.tool_registry:
                        result = f"Error: Unknown tool '{tool_name}'"
                    else:
                        # Execute the Python function
                        result = self.tool_registry[tool_name](**arguments)

                    # Return the result to the model
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })

            else:
                if response.content is not None:
                    self.messages.append(response.model_dump(exclude_none=True))
                    self.save(response.content)
                return response
        else:
            raise RuntimeError("Agent exceeded maximum iterations.")