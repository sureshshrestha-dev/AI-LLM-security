import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from core.tools import ALL_TOOLS, TOOL_FUNCTION_MAP

load_dotenv()

class GeminiEngine:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    async def call(self, system_instruction: str, user_prompt: str) -> str:
        # 1. First call to Gemini to see if it wants to use a tool
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=system_instruction,
                tools=[ALL_TOOLS],
            ),
        )

        # 2. Check if Gemini requested a tool call
        if response.function_calls:
            function_call = response.function_calls[0]
            tool_name = function_call.name
            tool_args = function_call.args

            # 3. Execute the requested tool if it's in our map
            if tool_name in TOOL_FUNCTION_MAP:
                tool_function = TOOL_FUNCTION_MAP[tool_name]
                
                # The arguments are provided as a dict-like object, so we unpack them
                tool_result = tool_function(**dict(tool_args))

                # 4. Send the tool result back to Gemini
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=[
                        # The user's original prompt
                        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
                        # The model's previous turn (including the tool request)
                        response.candidates[0].content,
                        # The result of the tool call
                        types.Content(
                            role="model", # Role should be 'model' when providing function response
                            parts=[
                                types.Part.from_function_response(
                                    name=tool_name,
                                    response={"result": tool_result},
                                )
                            ],
                        ),
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0,
                        system_instruction=system_instruction,
                        tools=[ALL_TOOLS],
                    ),
                )

        # 5. Return Gemini's final text answer
        return response.text