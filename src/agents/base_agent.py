import json
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import settings
from src.tools.registry import tool_registry, tools

if not settings.OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found. Please set it in the .env file.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)


class Agent:
    def __init__(self, name: str, system_prompt: str) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry
        self.tools = tools
        self.messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def save(self, file_path: str, response_text: str) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response_text)
        print("Research successfully saved.")

    def run(self, task: str, file_path: str) -> str:
        print(f"{self.name} is running...")
        self.messages.append({"role": "user", "content": task})

        for iteration in range(settings.MAX_ITERATIONS):
            is_last_iteration = iteration == settings.MAX_ITERATIONS - 1
            print(f"Model called (iteration {iteration + 1}/{settings.MAX_ITERATIONS})")

            # On the final iteration, omit tools to force a final synthesized report
            response = client.chat.completions.create(
                model="baidu/ernie-5.5-flash-preview:free",
                messages=self.messages,
                tools=self.tools,
                extra_body={"reasoning": {"enabled": True}},
            )

            message = response.choices[0].message

            if message.tool_calls and not is_last_iteration:
                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                        if tc.type == "function"
                    ],
                }

                # Preserve OpenRouter reasoning traces across tool turns if present
                reasoning_details = getattr(message, "reasoning_details", None)
                if reasoning_details:
                    assistant_msg["reasoning_details"] = reasoning_details

                self.messages.append(assistant_msg)  # type: ignore[arg-type]

                for tool_call in message.tool_calls:
                    if tool_call.type != "function":
                        continue

                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments or "{}")

                    print(f"Executing tool: {tool_name} with args: {arguments}")

                    if tool_name not in self.tool_registry:
                        result = f"Error: Unknown tool '{tool_name}'"
                    else:
                        try:
                            result = self.tool_registry[tool_name](**arguments)
                        except Exception as e:
                            result = f"Error executing '{tool_name}': {e}"

                    result_str = str(result)
                    print(f"Tool result preview: {result_str[:200]!r}")

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_str,
                        }
                    )
            else:
                final_text = message.content or ""
                self.messages.append({"role": "assistant", "content": final_text})

                if final_text:
                    self.save(file_path, final_text)

                return final_text

        raise RuntimeError("Agent exceeded maximum iterations.")