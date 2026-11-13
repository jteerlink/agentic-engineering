"""Router: a Claude Code PreToolUse hook on Agent that asks Jev, through the AI gateway, which model a subagent runs on.

It rewrites only `model` and only when nobody chose one; on any skip or failure it prints nothing,
so the subagent runs on its default model.
"""
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

MODELS = ["haiku", "sonnet", "opus"]  # cheapest first; low confidence moves one step right
BUMP_BELOW = 0.5
TIMEOUT = 3
MAX_PROMPT = 4000
LOG = Path(".local", "state", "jev-router", "decisions.jsonl")  # under $HOME

QUESTION = {
    "type": "choice",
    "instructions": "Choose the least costly model that can complete the task in `prompt` correctly.",
    "criteria": {
        "haiku": "Searches, finding files, listing or summarizing what exists; no code changes or judgments.",
        "sonnet": "Implementing or editing code with a clear target, running tests, routine reviews.",
        "opus": "Design, root-cause debugging, verifying work against a spec, unclear or high-stakes tasks.",
    },
}

SECRET_NAME = r"[A-Za-z_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)[A-Za-z_]*"
# ponytail: pattern-based; a new secret format slips through. The egress test covers the known ones.
REDACTIONS = [
    (re.compile(r"(?i)(bearer\s+)\S+"), r"\1[REDACTED]"),
    (re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+"), "[REDACTED]"),
    (re.compile(r"\b(?:sk|pk|rk)-[\w-]{16,}|\bgh[pousr]_\w{20,}|\bgithub_pat_\w{20,}|\bxox[abpr]-[\w-]{10,}|\bAKIA[0-9A-Z]{16}\b|\bAIza[\w-]{35}"), "[REDACTED]"),
    (re.compile(r"(\w+://[^:/\s]+:)[^@\s]+@"), r"\1[REDACTED]@"),
    (re.compile(r"((?:^|\s)(?:-u|--user)[\s=]+[^:\s]+:)\S+"), r"\1[REDACTED]"),
    (re.compile(rf"(?i)\b({SECRET_NAME}=)(\"[^\"]*\"|'[^']*'|\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(--?[\w-]*(?:password|passwd|token|secret|api-key)[\w-]*=)\S+"), r"\1[REDACTED]"),
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "[REDACTED]"),
    (re.compile(r"(?=[\w+=-]*\d)(?=[\w+=-]*[A-Za-z])[\w+=-]{40,}"), "[REDACTED]"),
]


def redact(text):
    for pattern, repl in REDACTIONS:
        text = pattern.sub(repl, text)
    return text


def agent_sets_model(subagent_type, cwd):
    # ponytail: assumes the file is named after the agent, as Claude Code's /agents writes it.
    for d in (Path(cwd, ".claude", "agents"), Path.home() / ".claude" / "agents"):
        try:
            text = (d / f"{subagent_type}.md").read_text()
        except OSError:
            continue
        front = re.match(r"---\n(.*?)\n---", text, re.S)
        return bool(front and re.search(r"(?m)^model:\s*\S", front.group(1)))
    return False


def skip_reason(task, agent, cwd):
    if task.get("model"):
        return "call sets model"
    if agent == "fork":
        return "fork"
    if ":" in agent:
        return "plugin agent"
    if agent_sets_model(agent, cwd):
        return "agent file sets model"
    return None


def ask_jev(agent, prompt, base, key):
    body = json.dumps({"model": "jev", "state": {"subagent_type": agent, "prompt": prompt},
                       "questions": {"model": QUESTION}}).encode()
    req = urllib.request.Request(f"{base.rstrip('/')}/v1/decisions", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        answer = json.load(resp)["answers"]["model"]
    if answer["choice"] not in MODELS:
        raise ValueError(f"unknown choice {answer['choice']!r}")
    return answer["choice"], float(answer["confidence"]), answer.get("probabilities")


def log(entry):
    try:
        path = Path.home() / LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **entry}) + "\n")
    except OSError:
        pass


def decide(event):
    if event.get("tool_name") != "Agent":
        return None
    task = event.get("tool_input") or {}
    agent = task.get("subagent_type") or "general-purpose"
    cwd = event.get("cwd") or os.getcwd()
    entry = {"cwd": cwd, "subagent_type": agent}
    reason = skip_reason(task, agent, cwd)
    # Claude Code's ANTHROPIC_BASE_URL is the gateway base. Its key is a personal key, which the gateway
    # refuses for decisions from our own code, so the key must be a service key in AIGW_API_KEY.
    base = os.environ.get("AIGW_BASE") or os.environ.get("ANTHROPIC_BASE_URL")
    key = os.environ.get("AIGW_API_KEY")
    if not reason and os.environ.get("JEV_ROUTER_OFF"):  # benchmark baseline
        reason = "disabled by JEV_ROUTER_OFF"
    if not reason and not (base and key):
        reason = "no gateway config"
    if reason:
        log({**entry, "action": "skip", "reason": reason})
        return None
    try:
        pick, confidence, probabilities = ask_jev(agent, redact(task.get("prompt") or "")[:MAX_PROMPT], base, key)
    except Exception as e:  # outage, timeout, bad response: no decision
        log({**entry, "action": "error", "reason": type(e).__name__})
        return None
    model = MODELS[min(MODELS.index(pick) + 1, len(MODELS) - 1)] if confidence < BUMP_BELOW else pick
    log({**entry, "action": "route", "pick": pick, "model": model, "confidence": confidence, "probabilities": probabilities})
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": f"Jev router: {model} (picked {pick}, confidence {confidence:.2f}).",
        "updatedInput": {**task, "model": model},
    }}


def main():
    try:
        out = decide(json.load(sys.stdin))
    except Exception:
        out = None
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
