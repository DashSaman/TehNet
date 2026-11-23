"""Identify the exact installed file pair and verify the patch selected for it."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select(plugin):
    manifest = json.loads((HERE / "versions.json").read_bytes())
    current = {name: sha(plugin / name) for name in manifest["original"]}
    for version in ("final", "split", "original"):
        if current == manifest[version]:
            if version == "final":
                return version, None
            spec = manifest["patches"][version]
            patch = HERE / spec["name"]
            if sha(patch) != spec["sha256"]:
                raise ValueError("Patch digest mismatch")
            return version, patch
    raise ValueError("Unrecognized installed JS/PHP pair")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin", type=Path)
    version, patch = select(parser.parse_args().plugin)
    print(version, patch.name if patch else "already installed")
