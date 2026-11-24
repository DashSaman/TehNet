"""Build reviewed WordPress bodies in memory from the four specified public baselines."""
import hashlib
import json
import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent

def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def insert_after(body, marker, offset, html):
    position = body.index(marker, offset) + len(marker)
    return body[:position] + "\n\n" + html + body[position:]

def prepare(baselines):
    specs = json.loads((PACKAGE / "service-acceptance.json").read_text(encoding="utf-8"))
    table = (PACKAGE / "branch-handoff.html").read_bytes().decode("utf-8")
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    inbound = json.loads((PACKAGE / "inbound-link.json").read_text(encoding="utf-8"))
    if digest(table) != manifest["payload_sha256"]:
        raise ValueError("unexpected handoff payload")
    results = {}
    for spec in specs:
        path = spec["path"]
        body = baselines[path]
        if digest(body) != spec["base_body_sha256"]:
            raise ValueError("baseline changed: " + path)
        if "row_evidence" in spec:
            notes = iter(spec["row_evidence"])
            def add_evidence(match):
                return "<br><strong>مدرک و تأییدکننده</strong><br>" + next(notes) + match.group()
            if table.count("</td></tr>") != len(spec["row_evidence"]) or len(spec["row_evidence"]) != 4:
                raise ValueError("unexpected acceptance row count")
            table = re.sub("</td></tr>", add_evidence, table)
            body = insert_after(body, "<!-- /wp:list -->", body.index(manifest["after_heading"]), table.strip())
        if spec.get("replace_service_link"):
            old = inbound["replace_once"]["before"]
            if body.count(old) != 1:
                raise ValueError("unexpected inbound link count")
            body = body.replace(old, inbound["replace_once"]["after"])
        heading = ">" + spec["after_heading"] + "<"
        if body.count(heading) != 1:
            raise ValueError("expected one heading: " + path)
        paragraphs = re.findall(r"<p>.*?</p>", spec["html"], re.S)
        if not paragraphs or "".join(paragraphs) != spec["html"]:
            raise ValueError("invalid paragraph fragment")
        blocks = "\n\n".join("<!-- wp:paragraph -->\n" + p + "\n<!-- /wp:paragraph -->" for p in paragraphs)
        results[path] = insert_after(body, "<!-- /wp:heading -->", body.index(heading), blocks)
    return results
