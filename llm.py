"""
llm.py

one shared helper that every agent uses to talk to Gemini.
to switch models, change MODEL here (or in .env).
"""
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads GOOGLE_API_KEY and MODEL from .env

MODEL = os.getenv("MODEL", "gemini-3.5-flash-lite")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def ask(role_instructions, message, as_json=False):
    """Send one message to Gemini with a role, return its text answer."""
    config = types.GenerateContentConfig(
        system_instruction=role_instructions,
        response_mime_type="application/json" if as_json else "text/plain",
    )
    reply = client.models.generate_content(model=MODEL, contents=message, config=config)
    return reply.text
