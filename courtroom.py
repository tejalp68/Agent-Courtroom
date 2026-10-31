"""
courtroom.py

runs the trial. the 4 agents live in agents/ (one file each).
  prosecutor -> defender (the DEBATE) -> judge (the VERDICT) -> reporter (summary)

run:  python courtroom.py                    (all files in traces/)
      python courtroom.py traces/Rag.json    (one file)
      or with uv:  uv run courtroom.py traces/Rag.json
"""
import glob
import json
import os
import sys

from agents.defender import defender
from agents.judge import judge
from agents.prosecutor import prosecutor
from agents.reporter import reporter


def trial(trace):
    """Run one trial on a trace (a dict). Returns everything as a dict."""
    case = "TASK: " + trace["task"] + "\nAGENT STEPS:\n" + "\n".join(trace["steps"])
    prosecution = prosecutor(case)
    defense = defender(case, prosecution)        # the debate
    result = judge(case, prosecution, defense)   # the verdict
    result["case"] = trace.get("name", "unnamed")
    return {"prosecution": prosecution, "defense": defense, "result": result}


def run_trial(path):
    with open(path, encoding="utf-8") as f:
        trace = json.load(f)

    print("\n" + "=" * 60)
    print("CASE:", trace["name"])
    print("=" * 60)

    out = trial(trace)
    result = out["result"]
    print("\n[PROSECUTOR]\n" + out["prosecution"])
    print("\n[DEFENDER]\n" + out["defense"])
    print("\n[JUDGE VERDICT]")
    print("  Verdict :", result["verdict"])
    print("  Score   :", result["score"], "/ 10")
    print("  Failure :", result["failure_type"])
    print("  Reason  :", result["reason"])
    return result


def main():
    files = sys.argv[1:] or sorted(glob.glob("traces/*.json"))
    verdicts = [run_trial(p) for p in files]

    print("\n" + "=" * 60)
    print("REPORTER SUMMARY")
    print("=" * 60)
    print(reporter(verdicts))

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(verdicts, f, indent=2)
    print("\nSaved all verdicts to report.json")


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        sys.exit("No GOOGLE_API_KEY found. Put it in a .env file here, or set it in the terminal.")
    main()
