"""Build exact release bodies off-host, from a private path-to-raw-post_content JSON."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from prepare_acceptance import digest, insert_after, prepare

UPLOADS = "/wp-content/uploads/tehnet-worksheets/"
WORKSHEETS = {
    "services/network-setup-tehran": ("branch-handoff-checklist", "branch-acceptance", "برگهٔ پذیرش شعبه"),
    "services/network-support-tehran": ("support-handoff-sample", "monthly-support", "فرم گزارش ماهانهٔ پشتیبانی"),
}


def prepare_release(original):
    bodies = prepare(original)
    for path, (heading, asset, title) in WORKSHEETS.items():
        body = bodies[path]
        anchor = f'id="{heading}"'
        if body.count(anchor) != 1 or UPLOADS in body:
            raise ValueError(f"Unexpected worksheet location on {path}")
        links = (f'<a href="{UPLOADS}{asset}.html">{title}</a> · '
                 f'<a href="{UPLOADS}{asset}.pdf">نسخهٔ چاپی (PDF)</a>')
        if asset == "branch-acceptance":
            links += ' · <a href="/services/?tn_service_context=network-setup#service-request">درخواست بررسی راه‌اندازی شبکه</a>'
        block = "<!-- wp:paragraph -->\n<p>" + links + "</p>\n<!-- /wp:paragraph -->"
        bodies[path] = insert_after(body, "<!-- /wp:table -->", body.index(anchor), block)

    spec = json.loads((HERE / "mikrotik-article-link.json").read_bytes())
    path = spec["path"]
    old, new = (spec["replace_once"][k] for k in ("before", "after"))
    if digest(bodies[path]) != spec["apply_after_body_sha256"] or bodies[path].count(old) != 1:
        raise ValueError("Unexpected MikroTik source")
    bodies[path] = bodies[path].replace(old, new)
    if digest(bodies[path]) != spec["after_body_sha256"]:
        raise ValueError("Unexpected MikroTik result")
    return bodies


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("output", type=Path, help="Private new directory, outside the web root")
    args = parser.parse_args()
    original = json.loads(args.original.read_bytes())
    result = prepare_release(original)
    hashes = json.loads((HERE / "manifest.json").read_bytes())["bodies"]
    if set(result) != set(hashes):
        raise ValueError("Unexpected release scope")
    for path, body in result.items():
        if digest(body) != hashes[path]["after"] or digest(original[path]) != hashes[path]["before"]:
            raise ValueError(f"Body mismatch on {path}")
    args.output.mkdir(exist_ok=False)
    for path, body in result.items():
        slug = path.rsplit("/", 1)[-1]
        (args.output / (slug + ".before.html")).write_bytes(original[path].encode())
        (args.output / (slug + ".after.html")).write_bytes(body.encode())


if __name__ == "__main__":
    main()
