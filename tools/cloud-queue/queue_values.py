"""Exact semantic acceptance for the lab's approved upload/download limits."""
import re

def exact_queue_limits(value):
    match = re.fullmatch(r"(\d+)([kM]?)/(\d+)([kM]?)", value)
    if not match:
        raise ValueError("Invalid limit pair")
    factors = {"":1, "k":1000, "M":1000000}
    pair = (int(match[1])*factors[match[2]], int(match[3])*factors[match[4]])
    if pair != (64000,128000):
        raise ValueError("Unexpected GUI-entered upload/download limits")
    return pair
