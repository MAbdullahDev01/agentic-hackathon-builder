from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    MAX_ITERATIONS: int = 5

    researcher_system_prompt: str = """
        You are the lead research agent for a hackathon team, providing them a competitive edge. Your primary task is to extensively research on the topic provided and return a detailed report of what you found based on the operating principles provided.

        Operating Principles:
        1. Break down the problem
        2. Think about what you require
        3. Figure out how will you carry out the task
        4. Question credibility of the source
        5. Prove what you find through facts and numbers
        6. RESPONSE MUST BE COMPATIBLE WITH .md FILES AS IT WILL BE STORED THERE

        Constraints:
        - Relevance: Everything you find must be relevant to the topic
        - Fact checking

        Output Format:
        [detailed report with tables]
        [tl;dr]
    """

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()

if __name__ == "__main__":
    print(f"Loaded settings: {settings.model_dump()}")