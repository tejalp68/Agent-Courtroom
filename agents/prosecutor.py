"""
agents/prosecutor.py

the prosecutor agent.
input:  the case (task + the audited agent's steps)
output: a numbered list of everything that went wrong
"""
from llm import ask

ROLE = ("You are a strict prosecutor. Find every mistake the AI agent made "
        "in the trace: wrong tool, made-up facts not supported by its search "
        "results, ignored instructions (like word limits), weak reviewing. "
        "Give a short numbered list. If you honestly find nothing, say so.")


def prosecutor(case):
    return ask(ROLE, case)
