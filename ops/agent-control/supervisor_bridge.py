#!/usr/bin/env python3
"""Z Code -> Codex supervisor bridge.

Invokes the official `codex exec` non-interactive interface in read-only
sandbox mode, captures the verdict, and atomically records the decision.

Fail-closed contract:
- nonzero Codex exit  -> BRIDGE_FAILED, no decision recorded
- zero or multiple conflicting DECISION lines -> BRIDGE_FAILED
- DECISION parsed only from the FINAL response block (echo-resistant)

Writes are confined to <repo>/ops/agent-control (the enforced output
boundary); receipts are persisted via atomic replace with fsync.

Codex is a supervisor only: it NEVER writes application code, deploys
production, or performs routine content creation. Engineering approval is
distinct from owner authorization.

Usage:
  python supervisor_bridge.py --evidence-file <packet.md> --topic "<topic>"
      [--repo <path>]

The evidence packet is a SHORT markdown summary with file references; never
attach whole repositories or raw logs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

VALID = {"APPROVE", "NEEDS_CHANGES", "REJECT", "NEEDS_OWNER"}
DECISION_RE = re.compile(r"DECISION:\s*(APPROVE|NEEDS_CHANGES|REJECT|NEEDS_OWNER)", re.I)

PROMPT_TEMPLATE = """You are the independent senior supervisor for the TehNet project (https://tehnet.ir, repo DashSaman/TehNet).
Z Code is the primary executor. Your job is REVIEW ONLY - you must not modify files.

Examine the evidence packet below and decide whether Z Code:
- is pursuing the correct objective,
- is repeating failed work,
- is introducing technical or security risks,
- is violating repository isolation or release gates,
- has appropriate backups and rollback,
- is producing legitimate (not fabricated) evidence,
- is drifting from business priorities or misusing resources.

Answer in EXACTLY this format as the FINAL part of your reply (no extra prose after it):
DECISION: <APPROVE|NEEDS_CHANGES|REJECT|NEEDS_OWNER>
EVIDENCE: <2-5 bullet evidence points, cite file paths or facts from the packet>
CORRECTION: <actionable correction or "none">
ACCEPTANCE: <acceptance conditions to re-verify or "none">

--- EVIDENCE PACKET ---
{packet}
"""


def atomic_write(path: Path, data: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-decision-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as h:
            h.write(data)
            h.flush()
            os.fsync(h.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def atomic_append(path: Path, line: str) -> None:
    """Append under an exclusive lock, then persist via atomic replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(path.suffix + ".lock")
    data = path.read_text(encoding="utf-8") if path.exists() else ""
    data += line
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-append-")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as h:
        h.write(data)
        h.flush()
        os.fsync(h.fileno())
    os.chmod(tmp, 0o644)
    lock_fd = os.open(str(lock), os.O_CREAT | os.O_RDWR)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lock_fd, msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
        os.replace(tmp, path)
    finally:
        try:
            if os.name == "nt":
                import msvcrt
                os.lseek(lock_fd, 0, os.SEEK_SET)
                msvcrt.locking(lock_fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(lock_fd)


def parse_verdict(text: str) -> dict:
    """Parse the FINAL response block only; fail on conflicting verdicts."""
    matches = list(DECISION_RE.finditer(text))
    if not matches:
        return {"decision": None, "reason": "no DECISION line", "raw_tail": text[-1500:]}
    last = matches[-1]
    values = {m.group(1).upper() for m in matches}
    if len(values) > 1:
        return {"decision": None, "reason": f"conflicting verdicts {sorted(values)}", "raw_tail": text[-1500:]}
    start = last.start()
    return {"decision": last.group(1).upper(), "body": text[start:start + 6000]}


def run_codex(prompt: str, repo: Path, timeout: int) -> tuple[int, str]:
    cmd = ["codex", "exec", "-s", "read-only", "-C", str(repo), "--skip-git-repo-check", prompt]
    env = {**os.environ, "CODEX_SANDBOX": "read-only"}
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env)
    return proc.returncode, (proc.stdout or b"").decode("utf-8", "replace") + (proc.stderr or b"").decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-file", required=True, help="Short markdown evidence packet")
    ap.add_argument("--topic", required=True, help="Short review topic label")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    # Enforced output boundary: always <repo>/ops/agent-control.
    outdir = repo / "ops" / "agent-control"
    outdir.mkdir(parents=True, exist_ok=True)

    packet = Path(args.evidence_file).resolve().read_text(encoding="utf-8")
    if len(packet) > 20000:
        raise SystemExit("Evidence packet too large; keep it short (references, not dumps)")

    prompt = PROMPT_TEMPLATE.format(packet=packet.strip())
    rc, output = run_codex(prompt, repo, args.timeout)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest = hashlib.sha256(packet.encode("utf-8")).hexdigest()[:12]

    # Fail closed on execution errors.
    if rc != 0:
        record = {"schema": 1, "topic": args.topic, "decided_utc": stamp,
                  "packet_sha256_12": digest, "codex_exit": rc, "decision": None,
                  "detail": output[-2000:]}
        atomic_write(outdir / ".last-supervisor-invocation.json",
                     json.dumps(record, ensure_ascii=False, indent=1) + "\n")
        print(json.dumps({"status": "BRIDGE_FAILED", "reason": "codex nonzero exit",
                          "codex_exit": rc}, ensure_ascii=False))
        return 2

    verdict = parse_verdict(output)
    record = {"schema": 1, "topic": args.topic, "decided_utc": stamp,
              "packet_sha256_12": digest, "codex_exit": rc,
              "decision": verdict["decision"],
              "detail": (verdict.get("body") or verdict.get("raw_tail", ""))[:4000]}
    atomic_write(outdir / ".last-supervisor-invocation.json",
                 json.dumps(record, ensure_ascii=False, indent=1) + "\n")

    if verdict["decision"] is None:
        print(json.dumps({"status": "BRIDGE_FAILED", "reason": verdict["reason"],
                          "codex_exit": rc}, ensure_ascii=False))
        return 2

    line = (f"| {stamp} | {args.topic} | {verdict['decision']} | {digest} | "
            f"{verdict.get('body', '')[:400].replace('|', '/')} |\n")
    decisions = outdir / "SUPERVISOR_DECISIONS.md"
    if not decisions.exists():
        atomic_write(decisions, "# Supervisor decisions\n\n| UTC | Topic | Decision | Packet | Detail |\n|---|---|---|---|---|\n")
    atomic_append(decisions, line)
    atomic_append(outdir / "RUN_HISTORY.md",
                  f"- {stamp} bridge ok exit={rc} decision={verdict['decision']} topic={args.topic}\n")
    print(json.dumps({"status": "BRIDGE_OK", "decision": verdict["decision"], "codex_exit": rc}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
