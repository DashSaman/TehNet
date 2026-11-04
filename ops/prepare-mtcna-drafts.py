#!/usr/bin/env python3
"""Build private Gutenberg working drafts and an evidence-gated course manifest.

This offline tool never writes to WordPress or marks a lesson ready to publish.
"""
from __future__ import annotations
import hashlib
import html
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "content/mtcna"
FIRST = datetime(2026, 11, 7, 9, tzinfo=ZoneInfo("Asia/Tehran"))
INITIAL_GATES = {"technical_review": "PENDING", "lab": "NOT_RUN", "screenshots": "MISSING", "editor_save": "NOT_VERIFIED", "release_qualification": "NOT_RUN"}


def ensure_initial_draft_state(previous):
    """Refuse to erase any qualified evidence or publication state on rebuild."""
    if previous.get("course_id") != "tehnet-mtcna-routeros7-20261104":
        raise ValueError("Refusing to overwrite a different course manifest")
    for lesson in previous.get("lessons", []):
        if (lesson.get("state") != "DRAFT_NOT_READY" or lesson.get("gates") != INITIAL_GATES
                or lesson.get("publication_receipt") or lesson.get("lab_evidence")
                or lesson.get("tested_versions") or lesson.get("original_screenshot_files")
                or lesson.get("video_segment_evidence")):
            raise ValueError("Qualified evidence exists; merge source updates without regenerating release state")


def esc(value):
    return html.escape(str(value), quote=True)


def inline(nodes):
    out = []
    for node in nodes:
        kind, value = node["t"], node.get("c")
        if kind == "Str": out.append(esc(value))
        elif kind in ("Space", "SoftBreak"): out.append(" ")
        elif kind == "LineBreak": out.append("<br>")
        elif kind in ("Strong", "Emph", "Strikeout"):
            tag = {"Strong": "strong", "Emph": "em", "Strikeout": "s"}[kind]
            out.append(f"<{tag}>{inline(value)}</{tag}>")
        elif kind == "Code": out.append(f"<code>{esc(value[1])}</code>")
        elif kind == "Link":
            href = value[2][0]
            if not (href.startswith(("https://", "http://", "/", "#"))):
                raise ValueError(f"Unsupported link: {href}")
            out.append(f'<a href="{esc(href)}">{inline(value[1])}</a>')
        elif kind == "Quoted": out.append("«" + inline(value[1]) + "»")
        elif kind == "Span": out.append(inline(value[1]))
        else: raise ValueError(f"Unsupported inline node: {kind}")
    return "".join(out)


def block(name, body, attrs=None):
    attribute = " " + json.dumps(attrs, ensure_ascii=False, separators=(",", ":")) if attrs else ""
    return f"<!-- wp:{name}{attribute} -->\n{body}\n<!-- /wp:{name} -->"


def cell_text(blocks):
    values = []
    for child in blocks:
        if child["t"] not in ("Plain", "Para"):
            raise ValueError(f"Unsupported table cell: {child['t']}")
        values.append(inline(child["c"]))
    return "<br>".join(values)


def table_row(row, header=False):
    tag = "th" if header else "td"
    cells = []
    for cell in row[1]:
        if cell[2:4] != [1, 1]: raise ValueError("Merged table cells need manual review")
        cells.append(f"<{tag}>{cell_text(cell[4])}</{tag}>")
    return "<tr>" + "".join(cells) + "</tr>"


def render(node):
    kind, value = node["t"], node.get("c")
    if kind in ("Para", "Plain"):
        return block("paragraph", "<p>" + inline(value) + "</p>")
    if kind == "Header":
        level = max(2, value[0])
        attrs = {"level": level} if level != 2 else None
        return block("heading", f'<h{level} class="wp-block-heading">{inline(value[2])}</h{level}>', attrs)
    if kind == "CodeBlock":
        return block("code", '<pre class="wp-block-code"><code>' + esc(value[1]) + "</code></pre>")
    if kind == "BlockQuote":
        # Editorial draft notes remain editable paragraphs; no simulated quotation.
        return "\n\n".join(render(x) for x in value)
    if kind in ("BulletList", "OrderedList"):
        ordered = kind == "OrderedList"
        items = value[1] if ordered else value
        attrs = {"ordered": True} if ordered else None
        start = value[0][0] if ordered else 1
        if start != 1: attrs["start"] = start
        tag = "ol" if ordered else "ul"
        start_html = f' start="{start}"' if start != 1 else ""
        contents = []
        for item in items:
            parts = []
            for child in item:
                if child["t"] in ("Para", "Plain"): parts.append(inline(child["c"]))
                elif child["t"] in ("BulletList", "OrderedList"): parts.append(render(child))
                else: raise ValueError(f"Unsupported list child: {child['t']}")
            contents.append(block("list-item", "<li>" + "<br>".join(parts) + "</li>"))
        return block("list", f'<{tag}{start_html} class="wp-block-list">' + "\n".join(contents) + f"</{tag}>", attrs)
    if kind == "Table":
        header_rows = value[3][1]
        body_rows = [row for body in value[4] for row in body[2] + body[3]]
        footer_rows = value[5][1]
        table = "<table>"
        if header_rows: table += "<thead>" + "".join(table_row(x, True) for x in header_rows) + "</thead>"
        table += "<tbody>" + "".join(table_row(x) for x in body_rows) + "</tbody>"
        if footer_rows: table += "<tfoot>" + "".join(table_row(x) for x in footer_rows) + "</tfoot>"
        table += "</table>"
        return block("table", '<figure class="wp-block-table">' + table + "</figure>", {"hasFixedLayout": False})
    if kind == "HorizontalRule": return ""
    raise ValueError(f"Unsupported block: {kind}")


def diagram_block(diagram):
    url = diagram.get("wordpress_url") or diagram.get("source_url")
    if not url: return ""  # No broken placeholders are sent to WordPress.
    media_id = diagram.get("wordpress_media_id")
    attrs = {"sizeSlug": "full", "linkDestination": "none"}
    image_class = ""
    if media_id:
        attrs["id"] = media_id
        image_class = f' class="wp-image-{media_id}"'
    body = f'<figure class="wp-block-image size-full"><img src="{esc(url)}" alt="{esc(diagram["alt"])}"{image_class}/><figcaption class="wp-element-caption">نمودار آموزشی: {esc(diagram["caption"])} این تصویر اسکرین‌شات نرم‌افزار یا نتیجهٔ آزمون نیست.</figcaption></figure>'
    return block("image", body, attrs)


OWNERS = {
    1: (40, "", "merge_existing_owner"),
    2: (62, "routeros-winbox", "merge_existing_owner"),
    3: (62, "routeros-winbox", "merge_existing_owner"),
    4: (62, "routeros-winbox", "merge_existing_owner"),
    5: (None, "backup-export-restore", "publish_new_topic"),
    6: (None, "routeros-upgrade-packages-routerboot", "publish_new_topic"),
    7: (63, "ip-dhcp-dns", "merge_existing_owner"),
    8: (63, "ip-dhcp-dns", "merge_existing_owner"),
    9: (63, "ip-dhcp-dns", "merge_existing_owner"),
    10: (None, "bridge-rstp", "publish_new_topic"),
    11: (64, "static-routing", "merge_existing_owner"),
    12: (64, "static-routing", "merge_existing_owner"),
    13: (65, "nat-masquerade", "merge_existing_owner"),
    14: (65, "nat-masquerade", "merge_existing_owner"),
    15: (66, "firewall-basics", "merge_existing_owner"),
    16: (66, "firewall-basics", "merge_existing_owner"),
    17: (None, "wifi-wireless-packages", "publish_new_topic"),
    18: (None, "wifi-wireless-packages", "merge_predecessor_owner"),
    19: (67, "queues-troubleshooting", "merge_existing_owner"),
    20: (67, "queues-troubleshooting", "merge_existing_owner"),
    21: (None, "pppoe-lab", "publish_new_topic"),
    22: (None, "tunnel-concepts-modern-options", "publish_new_topic"),
    23: (None, "monitoring-troubleshooting-tools", "publish_new_topic"),
    24: (None, "final-branch-network-project", "publish_new_topic"),
}


def main():
    manifest_path = COURSE / "course-manifest.json"
    if manifest_path.exists():
        ensure_initial_draft_state(json.loads(manifest_path.read_text()))
    metadata = {}
    for path in sorted((COURSE / "lessons").glob("*.json")):
        item = json.loads(path.read_text())
        number = item["number"]
        if number in metadata: raise ValueError(f"Duplicate metadata for lesson {number}")
        metadata[number] = (path, item)
    if set(metadata) != set(range(1, 25)): raise ValueError(f"Incomplete lesson metadata: {sorted(metadata)}")
    diagrams = json.loads((COURSE / "assets/diagrams.json").read_text())
    generated = COURSE / "wordpress"
    generated.mkdir(exist_ok=True)
    receipts_path = COURSE / "wordpress-receipts.json"
    receipts = json.loads(receipts_path.read_text()) if receipts_path.exists() else []
    receipt_by_number = {x["number"]: x for x in receipts}
    lessons = []
    for number in range(1, 25):
        meta_path, meta = metadata[number]
        source_path = next((COURSE / "lessons").glob(f"{number:02}-*.md"))
        markdown = source_path.read_text()
        assert "TehranTurk" not in markdown and "تهران‌تورک" not in markdown
        assert len(markdown.split()) >= 500, (number, "Draft is too short")
        assert meta["lab_status"] == "NOT_RUN" and meta["screenshot_status"] == "MISSING"
        assert meta["source_urls"] and meta["capture_plan"]
        ast = json.loads(subprocess.check_output(["pandoc", "--from=gfm", "--to=json", str(source_path)], text=True))
        related_diagrams = [x for x in diagrams if number in x["parts"]]
        body_blocks = []
        for node in ast["blocks"]:
            if node["t"] == "Header" and node["c"][0] == 1:
                continue
            if node["t"] == "CodeBlock" and "mermaid" in node["c"][0][1]:
                if number != 24 or not any(d["id"] == "final-project-lab" and d.get("source_url") for d in related_diagrams):
                    raise ValueError("Mermaid source requires its reviewed rendered diagram before WordPress export")
                continue
            body_blocks.append(render(node))
        introduction = block("paragraph", f'<p><strong>تهنت؛ تهران نتورک</strong> — فصل {meta["chapter"]}، قسمت {number} از ۲۴. آموزش نوشتاری مستقل؛ <a href="https://www.youtube.com/@tehran.network021">کانال تهران نتورک</a>.</p>')
        visual_blocks = [diagram_block(x) for x in related_diagrams]
        content = "\n\n".join(x for x in [introduction] + body_blocks[:2] + visual_blocks + body_blocks[2:] if x) + "\n"
        assert content.count("<!-- wp:") == content.count("<!-- /wp:")
        assert "<script" not in content.lower() and "javascript:" not in content.lower()
        slug = f"mtcna-draft-{number:02}-{meta['slug']}"
        payload = {"title": f"MTCNA | قسمت {number}: {meta['title']}", "slug": slug, "status": "draft", "parent": 40, "content": content, "excerpt": meta["summary"]}
        (generated / f"{number:02}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        (generated / f"{number:02}.html").write_text(content)
        due = FIRST + timedelta(days=3 * (number - 1))
        owner_id, owner_slug, action = OWNERS[number]
        receipt = receipt_by_number.get(number, {})
        lessons.append({
            "number": number, "chapter": meta["chapter"], "title": meta["title"],
            "source_path": str(source_path.relative_to(ROOT)), "metadata_path": str(meta_path.relative_to(ROOT)),
            "wordpress_payload_path": str((generated / f"{number:02}.json").relative_to(ROOT)),
            "source_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
            "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "draft_slug": slug, "wordpress_draft_id": receipt.get("id"),
            "canonical_action": action, "canonical_owner_id": owner_id,
            "canonical_owner_from_lesson": 17 if number == 18 else None,
            "canonical_url": "https://tehnet.ir/learn/mikrotik/mtcna/" + (owner_slug + "/" if owner_slug else ""),
            "public_slug": owner_slug, "section_anchor": f"mtcna-lesson-{number:02}",
            "nominal_release_at": due.isoformat(), "nominal_release_utc": due.astimezone(timezone.utc).isoformat(),
            "prerequisites": [number - 1] if number > 1 else [],
            "diagram_ids": [x["id"] for x in related_diagrams],
            "state": "DRAFT_NOT_READY", "content_relationship": "INDEPENDENT_WRITTEN_LESSON",
            "gates": dict(INITIAL_GATES),
            "hardware_required": number in (6, 17, 18),
            "tested_versions": None, "lab_evidence": None, "original_screenshot_files": [],
            "video_segment_evidence": [], "publication_receipt": None,
        })
    manifest = {
        "schema_version": 1, "course_id": "tehnet-mtcna-routeros7-20261104",
        "brand": {"short": "TehNet / تهنت", "fa": "تهران نتورک", "en": "Tehran Network", "youtube": "https://www.youtube.com/@tehran.network021"},
        "lesson_count": 24, "chapter_count": 9, "wordpress_parent_id": 40,
        "timezone": "Asia/Tehran", "first_release_window": FIRST.isoformat(), "cadence_days": 3,
        "release_policy": {"maximum_lessons_per_window": 1, "window_id": "Asia/Tehran ISO timestamp: first window + floor((now-first)/72h)*72h", "require_unconsumed_window": True, "strict_order": True, "catch_up_batches": False, "stop_after_verified_releases": 24, "preserve_existing_noindex": True, "blocked_lesson_stays_next": True, "no_automatic_future_status": True, "require_existing_release_qualification": True},
        "source_version_baseline": {"observed_on": "2026-11-04", "routeros_stable": "7.25.1", "winbox": "4.5", "actually_tested": False},
        "lessons": lessons,
    }
    (COURSE / "course-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    assert len({x["draft_slug"] for x in lessons}) == 24
    assert set(x["chapter"] for x in lessons) == set(range(1, 10))
    assert all((datetime.fromisoformat(b["nominal_release_at"]) - datetime.fromisoformat(a["nominal_release_at"])).total_seconds() == 259200 for a, b in zip(lessons, lessons[1:]))
    print(json.dumps({"lessons": len(lessons), "chapters": len({x['chapter'] for x in lessons}), "first": lessons[0]["nominal_release_at"], "last_nominal_slot": lessons[-1]["nominal_release_at"], "ready": 0, "private_payloads_built": 24, "uploaded_diagrams": sum(bool(x.get('wordpress_url')) for x in diagrams)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
