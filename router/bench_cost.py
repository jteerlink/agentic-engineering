"""Cost and speed of subagent runs with and without the Router. Opt-in: makes real `claude -p` calls
(billed) and gateway requests. Not part of the offline gate.

Runs the same tasks, interleaved: baseline (JEV_ROUTER_OFF=1, every subagent takes the main model)
and router (Jev picks). Results go to .scratch/bench/<time>.json.

Usage: python3 router/bench_cost.py --runs 5
"""
import argparse, json, os, statistics, subprocess, time
from pathlib import Path

LOG = Path.home() / ".local/state/jev-router/decisions.jsonl"
OUT = Path(__file__).resolve().parent.parent / ".scratch" / "bench"
WRAP = ("Use the Agent tool exactly once, with subagent_type general-purpose and no model parameter, "
        "to do this task: {task} Then reply with the subagent's answer in one sentence.")
TASKS = [  # haiku-shaped and opus-shaped, interleaved
    "List every .py file under router/ and tests/.",
    "Review the design of the Router hook in router/jev_router.py: name the risks of calling the gateway synchronously in a PreToolUse hook.",
    "Find where ANTHROPIC_BASE_URL is mentioned in this repo.",
    "Verify router/jev_router.py against the Done when list in .scratch/jev-router/spec.md and say which items fail.",
]


def log_lines():
    return LOG.read_text().splitlines() if LOG.exists() else []


def run(task, router_on):
    env = dict(os.environ)
    env.pop("JEV_ROUTER_OFF", None)
    if not router_on:
        env["JEV_ROUTER_OFF"] = "1"
    before = len(log_lines())
    t0 = time.time()
    p = subprocess.run(["claude", "-p", WRAP.format(task=task), "--output-format", "json"],
                       capture_output=True, text=True, env=env, timeout=900)
    wall = time.time() - t0
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        out = {"error": p.stderr[-500:] or p.stdout[-500:]}
    picks = [json.loads(l) for l in log_lines()[before:]]
    return {"task": task, "router": router_on, "wall_s": round(wall, 1), "exit": p.returncode,
            "cost_usd": out.get("total_cost_usd"), "duration_ms": out.get("duration_ms"),
            "model_usage": out.get("modelUsage"), "router_decisions": [
                {"action": d.get("action"), "model": d.get("model")} for d in picks],
            "error": out.get("error") if "error" in out else None}


def summarize(runs):
    rows = {}
    for cond in (False, True):
        rs = [r for r in runs if r["router"] == cond and r["cost_usd"] is not None]
        if not rs:
            continue
        costs = [r["cost_usd"] for r in rs]
        durs = [r["duration_ms"] / 1000 for r in rs if r["duration_ms"] is not None]
        rows["router" if cond else "baseline"] = {
            "n": len(rs), "mean_cost_usd": round(statistics.mean(costs), 4),
            "total_cost_usd": round(sum(costs), 4),
            "mean_duration_s": round(statistics.mean(durs), 1) if durs else None,
            "median_duration_s": round(statistics.median(durs), 1) if durs else None,
        }
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3, help="repetitions of each task per condition")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    runs = []
    for _ in range(args.runs):
        for task in TASKS:
            for router_on in (False, True):
                r = run(task, router_on)
                runs.append(r)
                print(f"{'router  ' if router_on else 'baseline'} cost={r['cost_usd']} "
                      f"dur={r['duration_ms']} picks={[d['model'] for d in r['router_decisions']]} "
                      f"err={r['error'] is not None}", flush=True)
    summary = summarize(runs)
    path = OUT / f"{time.strftime('%Y%m%dT%H%M%S')}.json"
    path.write_text(json.dumps({"summary": summary, "runs": runs}, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"raw: {path}")
    print("Note: each run includes the main session (opus) too; compare the two conditions, not the absolute cost.")


if __name__ == "__main__":
    main()
