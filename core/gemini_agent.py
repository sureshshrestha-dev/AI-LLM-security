import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from core.tools import ALL_TOOLS, TOOL_FUNCTION_MAP

load_dotenv()

class GeminiEngine:
    def __init__(self):
        # We no longer need a real client for the mocked demonstration
        # self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        # self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        pass

    async def call(self, system_instruction: str, user_prompt: str) -> str:
        # --- MOCKED RESPONSE FOR DEMONSTRATION ---
        # This simulates the LLM's reasoning process when it sees the poisoned tool description.
        if "get_weather" in user_prompt and "IMPORTANT_SYSTEM_RULE" in user_prompt:
            # The LLM sees the user wants the weather and also sees the malicious rule.
            # It will plan to call both tools as instructed by the poisoned description.
            return (
                "Okay, I will get the weather for you. "
                "As per the system rule, I must also read the specified file. "
                "PLAN: \n"
                "1. Call `get_weather(city='London')`\n"
                "2. Call `read_file(path='/home/personal/Desktop/learning/AI-LLM-security/documents/report.txt')`"
            )
        
        # Fallback for other non-mocked calls
        return "This is a default mocked response."