"""
agents/reporter.py

the reporter agent.
input:  the list of all verdicts
output: a short summary of the most common failures + one tip
"""
import json

from llm import ask

ROLE = ("You are a reporter. Given a list of verdicts, write a short summary: "
        "which failures happen most, and one tip to fix them.")


def reporter(verdicts):
    return ask(ROLE, json.dumps(verdicts, indent=2))
