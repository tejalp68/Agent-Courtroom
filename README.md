# Agent Courtroom

An evaluation project that puts AI agents on trial. Four Gemini agents
(Prosecutor, Defender, Judge, Reporter) audit an agent's run and score it.

Topics combined: Agentic AI (multi-agent, LangGraph) + LLM evaluation (LLM-as-judge).

## Run

    pip install -r requirements.txt     (or: uv add google-genai python-dotenv)
    copy .env.example .env              then paste your GOOGLE_API_KEY in .env
    python courtroom.py

Put agent traces (name, task, steps) as JSON files in `traces/`.
Results are saved to `report.json`.
