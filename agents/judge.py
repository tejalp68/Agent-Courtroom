"""
agents/judge.py

the judge agent.
input:  the case + prosecution + defense
output: the verdict, as a dict: score, verdict, failure_type, reason
"""
import json

from llm import ask

ROLE = ("You are a fair judge. Read both sides and decide. Reply ONLY with JSON: "
        '{"score": <1-10, 10 = perfect agent>, '
        '"verdict": "GUILTY" or "NOT GUILTY", '
        '"failure_type": "wrong_tool" or "hallucination" or "ignored_instruction" or "none", '
        '"reason": "<one sentence>"}')


def judge(case, prosecution, defense):
    text = ask(ROLE, case + "\n\nPROSECUTION:\n" + prosecution + "\n\nDEFENSE:\n" + defense,
               as_json=True)
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)
