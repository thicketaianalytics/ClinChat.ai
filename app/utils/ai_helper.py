import reflex as rx
import os
import logging
from typing import Literal, Optional
import anthropic
import google.generativeai as genai

_ai_cache = {}


class AIClient:
    """A wrapper for AI clients to support multiple providers."""

    def __init__(self):
        self.claude_client = None
        self.gemini_client = None
        self.current_provider: Optional[Literal["gemini", "claude"]] = None
        try:
            gemini_api_key = "AIzaSyDyL784qFG7gIhfa0pIRfriE7Kqw8wy6Z4"
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
            genai.configure(api_key=gemini_api_key)
            self.gemini_client = genai.GenerativeModel("gemini-1.5-flash")
            self.current_provider = "gemini"
            logging.info("Initialized Google Gemini client.")
        except Exception as e:
            logging.exception(f"Failed to initialize Gemini client: {e}")
        if self.current_provider is None:
            try:
                anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
                if anthropic_api_key:
                    self.claude_client = anthropic.Anthropic(api_key=anthropic_api_key)
                    self.current_provider = "claude"
                    logging.info("Initialized Anthropic Claude client as fallback.")
            except Exception as e:
                logging.exception(f"Failed to initialize Claude client: {e}")

    def get_provider(self) -> Optional[str]:
        return self.current_provider

    def generate_content(self, prompt: str, cache_key: Optional[str] = None) -> str:
        if cache_key and cache_key in _ai_cache:
            logging.info(f"Returning cached response for key: {cache_key}")
            return _ai_cache[cache_key]
        if not self.current_provider:
            return "Error: No AI provider is configured. Please set GOOGLE_API_KEY or ANTHROPIC_API_KEY."
        try:
            if self.current_provider == "gemini" and self.gemini_client:
                response = self.gemini_client.generate_content(prompt)
                result = response.text
            elif self.current_provider == "claude" and self.claude_client:
                message = self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}],
                )
                result = message.content[0].text
            else:
                return "Error: AI client not properly initialized."
            if cache_key:
                _ai_cache[cache_key] = result
            return result
        except Exception as e:
            logging.exception(
                f"AI content generation failed for provider {self.current_provider}: {e}"
            )
            if "quota" in str(e).lower():
                return f"Error: API quota exceeded for {self.current_provider.capitalize()}. Please check your plan and billing details."
            return f"Error: An unexpected error occurred with the {self.current_provider.capitalize()} API."


ai_client = AIClient()