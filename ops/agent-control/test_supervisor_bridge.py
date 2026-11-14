#!/usr/bin/env python3
"""Behavioral regression checks for the supervisor bridge (no Codex calls).

Run: python test_supervisor_bridge.py   (exit 0 = all pass)

Covers the supervisor acceptance items: echo-only prompt reply must not
produce a verdict; duplicate verdict lines (even same-value) fail; quoted or
bare 'APPROVED' never matches; incomplete blocks fail; transcript isolation
works; writes are atomic and confined.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("sb", HERE / "supervisor_bridge.py")
sb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sb)

failures: list[str] = []


def check(name: str, cond: bool) -> None:
    print(("PASS" if cond else "FAIL"), name)
    if not cond:
        failures.append(name)


GOOD = "DECISION: APPROVE\nEVIDENCE: file facts\nCORRECTION: none\nACCEPTANCE: none"

# 1. Echo-only reply (model died before answering): the transcript's last
#    segment is the echoed PROMPT. Its template line reads
#    "DECISION: <one-of: ...>" and must NOT match the verdict regex.
echo_only = sb.PROMPT_TEMPLATE.format(packet="pkt")  # full prompt echo
v = sb.parse_verdict(sb.isolate_final_reply("codex\n" + echo_only))
check("echo-only prompt reply yields NO verdict", v["decision"] is None)

# 2. Same-value duplicate verdict lines are ambiguous -> fail.
dup = "DECISION: APPROVE\nEVIDENCE: a\nCORRECTION: none\nACCEPTANCE: none\nDECISION: APPROVE\nEVIDENCE: b\nCORRECTION: none\nACCEPTANCE: none"
check("duplicate same-value verdicts fail", sb.parse_verdict(dup)["decision"] is None)

# 3. Conflicting values fail.
check("conflicting verdicts fail",
      sb.parse_verdict("DECISION: APPROVE\n--\nDECISION: REJECT")["decision"] is None)

# 4. Missing/quoted/bare-word forms never match.
check("missing verdict fails", sb.parse_verdict("no verdict here")["decision"] is None)
check("quoted verdict fails", sb.parse_verdict('DECISION: "APPROVE"')["decision"] is None)
check("bare APPROVED (not a verdict line) does not parse alone",
      sb.parse_verdict("we APPROVED it")["decision"] is None)

# 5. Incomplete block (no three fields) fails.
check("incomplete verdict block fails", sb.parse_verdict("DECISION: APPROVE")["decision"] is None)

# 6. Transcript isolation: user segment containing a verdict line must be
#    ignored; only the final codex segment counts.
transcript = ("user\nDECISION: REJECT (example)\ncodex\n" + GOOD)
check("isolation ignores earlier segments",
      sb.parse_verdict(sb.isolate_final_reply(transcript))["decision"] == "APPROVE")

# 7. Atomic persistence: write + two appends preserve order.
d = Path(tempfile.mkdtemp())
p = d / "decisions.md"
sb.atomic_write(p, "| header |\n")
sb.atomic_append(p, "row1\n")
sb.atomic_append(p, "row2\n")
check("atomic write+append order", p.read_text(encoding="utf-8") == "| header |\nrow1\nrow2\n")

# 8. Valid single verdict parses to the right value.
check("valid verdict parses", sb.parse_verdict(GOOD)["decision"] == "APPROVE")

print("FAILED:", failures if failures else "none")
sys.exit(1 if failures else 0)
