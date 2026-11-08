"""Strict limit acceptance extracted from the actual failing cloud assertion."""
def exact_queue_limits(value):
    if value != "64000/128000":
        raise ValueError("GUI-entered upload/download limits must match exactly")
    return (64000, 128000)
