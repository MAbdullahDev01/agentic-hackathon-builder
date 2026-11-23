from google import genai
from google.genai import types
from src.config import settings
from src.tools.registry import tool_registry

if settings.GEMINI_API_KEY == "":
    raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

# Initialize the official Google GenAI client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class Agent:
    def __init__(self, name: str, system_prompt: str) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry
        
        # Extract the actual Python functions from your registry to pass as tools
        self.tools_list = list(self.tool_registry.values())
        
        # Initialize a Gemini chat session which manages conversation history automatically
        self.chat = client.chats.create(
            model="gemini-4-hydrogen",
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                tools=self.tools_list,
                max_output_tokens=settings.MAX_OUTPUT_TOKENS,
            )
        )

    def save(self, file_path: str, response_text: str) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response_text)
        print("Research successfully saved.")

    def run(self, task: str, file_path: str):
        print(f"{self.name} is running...")

        # Send initial user task to the chat session
        response = self.chat.send_message(task)

        for iteration in range(settings.MAX_ITERATIONS):
            print("Model called")

            # Check if Gemini requested any tool/function calls
            if response.function_calls:
                for function_call in response.function_calls:
                    tool_name = function_call.name
                    # Arguments are returned as a standard dictionary
                    arguments = dict(function_call.args)

                    print(f"Executing tool: {tool_name} with args: {arguments}")

                    # Validate and execute the requested tool
                    if tool_name not in self.tool_registry:
                        result = f"Error: Unknown tool '{tool_name}'"
                    else:
                        result = self.tool_registry[tool_name](**arguments)

                    # Send the tool execution result back to Gemini through the chat session
                    response = self.chat.send_message(
                        types.Part.from_function_response(
                            name=tool_name,
                            response={"result": result}
                        )
                    )
            else:
                # No more tools called; we have our final text output
                if response.text is not None:
                    self.save(file_path, response.text)
                return response
        else:
            raise RuntimeError("Agent exceeded maximum iterations.")