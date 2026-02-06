import os
import json
from typing import Optional, Dict, Any, List
from google import genai

class LLMClient:
    """Gemini LLM wrapper (FREE & supported in 2026)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")

        self.client = genai.Client(api_key=self.api_key)
        
        # RECOMMENDED: Use 'gemini-2.5-flash' for balanced speed and intelligence
        # Or 'gemini-3-flash-preview' for the latest experimental capabilities
        self.model = "gemini-2.5-flash" 

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 2048,
        json_mode: bool = False
    ) -> str:
        # For the new SDK, system instructions can be passed in config
        config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "system_instruction": system_prompt if system_prompt else None
        }

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )

        # Ensure the response has text before accessing it
        if not response.text:
            raise ValueError("LLM returned an empty response.")
            
        text = response.text.strip()

        if json_mode:
            text = self._extract_json(text)

        return text

    # ... keep remaining methods (generate_structured, batch_generate, _extract_json) as is
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:

        instruction = "\n\nReturn ONLY valid JSON."
        if schema:
            instruction += "\nSchema:\n" + json.dumps(schema, indent=2)

        raw = self.generate(
            prompt + instruction,
            system_prompt,
            temperature,
            json_mode=True
        )

        return json.loads(raw)

    def batch_generate(self, prompts, system_prompt=None, temperature=0.4):
        return [self.generate(p, system_prompt, temperature) for p in prompts]

    def _extract_json(self, text):
        try:
            json.loads(text)
            return text
        except:
            pass

        if "```" in text:
            text = text.split("```")[1]

        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            return text[start:end]

        raise ValueError("No valid JSON found in LLM output")
