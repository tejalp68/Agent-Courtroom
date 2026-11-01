# Agent Courtroom

**A multi-agent system that puts AI agents on trial.**

AI agents often fail without anyone noticing: they use the wrong tool, make up facts, or ignore instructions. Agent Courtroom reads the log of an agent's run (a _trace_) and audits it automatically. Four AI agents act out a trial: a prosecutor accuses, a defender replies, a judge gives a verdict, and a reporter summarizes the patterns.

---

## Why I built this

While working with multi-agent systems, I noticed that they can fail quietly and I had no easy way to catch it. Reading long logs by hand does not scale, so I built a system where AI agents check other AI agents. The design, the agent roles, the trace format and the evaluation setup are my own work.

---

## The problem

Companies run AI agents such as support bots, research assistants and booking agents. Each run leaves a long log, and nobody can read thousands of logs by hand. Mistakes slip through: a made-up answer here, a skipped instruction there.

**Agent Courtroom is an automatic auditor for those logs.**

---

## How it works

```
 agent's trace (task + steps)
            │
            ▼
      ┌────────────┐
      │ Prosecutor │  lists everything that went wrong
      └─────┬──────┘
            ▼
      ┌────────────┐
      │  Defender  │  replies, admits the true charges
      └─────┬──────┘
            ▼              ← prosecutor vs defender = the DEBATE
      ┌────────────┐
      │   Judge    │  reads both sides
      └─────┬──────┘
            ▼
   VERDICT: GUILTY / NOT GUILTY, score /10,
            failure type, reason
            │
            ▼
      ┌────────────┐
      │  Reporter  │  summarizes all trials (many traces)
      └────────────┘
```

### Debate and verdict, in simple words

- **Debate:** two agents argue opposite sides about the same agent run. One AI judging alone can be too harsh or too lenient, so two sides give a more balanced view.
- **Verdict:** the judge's final decision after hearing both sides: GUILTY or NOT GUILTY, a score from 1 to 10, the type of failure, and a one-line reason.

### Failure types the judge uses

`wrong_tool` · `hallucination` · `ignored_instruction` · `none`

---

## Project structure

````
agent-courtroom/
├── courtroom.py          runs the trial (prosecutor → defender → judge → reporter)
├── mcp_server.py         MCP server exposing the courtroom as tools
├── app.py                Flask web UI
├── templates/index.html  the UI page
├── llm.py                shared Gemini helper used by every agent
├── agents/
│   ├── prosecutor.py     finds what went wrong
│   ├── defender.py       argues back
│   ├── judge.py          gives the verdict as JSON
│   └── reporter.py       summarizes all verdicts
├── traces/               agent runs to audit (JSON files)
├── screenshots/          output screenshots used in this README
├── report.json           saved verdicts (created when you run it)
├── pyproject.toml        dependencies (uv)
├── uv.lock
└── .env.example          template for your API key

---

## Setup

Uses [uv](https://docs.astral.sh/uv/).

```bash
git clone <your-repo-url>
cd agent-courtroom
uv sync
cp .env.example .env        # on Windows: copy .env.example .env
````

Open `.env` and fill in:

```
GOOGLE_API_KEY=your_key_here     # free key: https://aistudio.google.com/apikey
MODEL=gemini-3.5-flash-lite      # use a model name your key supports
```

Never commit `.env`. It holds your key.

---

## Usage

Audit every trace in `traces/`:

```bash
uv run courtroom.py
```

Audit one trace:

```bash
uv run courtroom.py traces/Rag.json
```

The output shows the prosecutor's charges, the defender's reply, the judge's verdict, and a reporter summary. All verdicts are saved to `report.json`.

Free Gemini keys have rate limits. If you get a 429 or quota error, wait a minute or audit one trace at a time.

### Input format (a trace)

A trace is a small JSON file in `traces/`:

```json
{
  "name": "Weather agent used the wrong tool",
  "task": "What is the weather in Pune right now?",
  "steps": [
    "Thought: I need the weather for Pune.",
    "Tool call: calculator('Pune weather')",
    "Tool result: Error - cannot calculate 'Pune weather'",
    "Final answer: It is probably sunny and 28C in Pune today."
  ]
}
```

| Field   | Meaning                                                                   |
| ------- | ------------------------------------------------------------------------- |
| `name`  | label for the case                                                        |
| `task`  | what the agent was asked to do                                            |
| `steps` | what the agent did, in order: thoughts, tool calls, results, final answer |

Included samples: a wrong-tool run, a perfect run, and a run that ignored an instruction.

---

## Using this in the real world

1. A company's agent runs all day and saves each run as a trace.
2. Each night the courtroom audits a sample, or only the runs flagged as risky.
3. The reporter produces a summary such as "12% of runs used the wrong tool, mostly on refund requests".
4. A human reviews only the GUILTY cases and fixes the agent's prompts or tools.

Changes needed beyond this capstone:

- **Input:** read traces from a logging tool or database instead of JSON files, with a small converter.
- **Cost:** each trial makes several LLM calls, so audit a sample or use a cheaper model for the debate.
- **Privacy:** remove names, phone numbers and other customer data before logs reach the courtroom.
- **Trust:** treat a verdict as a flag for a human, not an automatic decision.

---

## Limitations

- The judge is an LLM and can be wrong. This is why the project measures its agreement with human labels.
- Verdicts can vary between runs of the same trace.
- The courtroom only sees what the trace contains. If tool results are not logged, it cannot detect made-up answers.
- Free-tier API limits slow down large batches.

---

## Author

**Tejal Pagar** · tejalpagar29@gmail.com

## Tech stack

Python · Gemini (`google-genai`) · LangGraph (audited system) · Tavily (audited system's search) · MCP (optional) · Flask (optional) · uv
