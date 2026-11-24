"""Prepare the reviewed WordPress edits from a private raw-content export."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(body):
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def prepare(originals, destination):
    manifest = json.loads((HERE / "manifest.json").read_bytes())
    prepared = {}
    for path, spec in manifest["bodies"].items():
        before = originals[path]
        if digest(before) != spec["before"]:
            raise ValueError(f"Changed source: {path}")
        marker = spec["before_block"]
        if before.count(marker) != 1:
            raise ValueError(f"Ambiguous insertion: {path}")
        offset = before.rfind("<!-- wp:", 0, before.index(marker) + 1)
        if offset < 0:
            raise ValueError(f"Missing block: {path}")
        fragment = (HERE / spec["fragment"]).read_bytes().decode("utf-8").strip()
        after = before[:offset] + "<!-- wp:html -->\n" + fragment + "\n<!-- /wp:html -->\n\n" + before[offset:]
        if digest(after) != spec["after"]:
            raise ValueError(f"Unexpected output: {path}")
        slug = path.split("/")[-1]
        prepared[slug + ".before.html"] = before
        prepared[slug + ".after.html"] = after
    destination.mkdir(exist_ok=False)
    for name, body in prepared.items():
        (destination / name).write_bytes(body.encode("utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("originals", type=Path, help="JSON mapping page paths to raw post_content")
    parser.add_argument("output", type=Path, help="New private directory")
    args = parser.parse_args()
    prepare(json.loads(args.originals.read_bytes()), args.output)
