"""Prompt selection for real RouterOS serial responses; no device I/O."""
import re

def select_prompt(text, patterns):
    for key, pattern in patterns.items():
        if re.search(pattern, text, re.I):
            return key
    return None
