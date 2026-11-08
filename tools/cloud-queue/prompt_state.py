"""Prompt selection for real RouterOS serial responses; no device I/O."""
import re

def select_prompt(text, patterns):
    matches = []
    for index, (key, pattern) in enumerate(patterns.items()):
        for match in re.finditer(pattern, text, re.I):
            matches.append((match.end(), -index, key))
    # Responses may contain an echoed old prompt followed by the actual state.
    # Prefer the latest complete prompt; preserve explicit repeat/new priority.
    return max(matches)[2] if matches else None
