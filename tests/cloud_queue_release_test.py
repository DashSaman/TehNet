"""Exact publication boundary for the new single-owner Queue package."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("queue_release", ROOT / "ops/release-growth-content.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
SCOPE = "tehnet-winbox-queue-cloud-20261108-v1"
DIRECTORY = "content/queue-winbox-cloud-2026-11-08"
MEDIA = "site/mu-plugins/tehnet-technical-resources/learning-media/queue-cloud-20261108/"
NAMES = ["01-connected-baseline","02-queues-window","03-new-dialog","04-name-target",
         "05-upload-download-limits","06-applied-general","07-active-statistics",
         "08-disabled-general","09-reenabled-general","10-reenabled-statistics",
         "11-final-queue-row","12-owned-rule-removed"]

class QueueReleaseBoundary(unittest.TestCase):
    def test_operator_has_only_the_fixed_files_and_one_body(self):
        files, extra, guarded = release.scope_spec(SCOPE)
        self.assertEqual(files, [MEDIA+n+".png" for n in NAMES] +
                         ["site/themes/tehnet/assets/css/visual-refresh.css"])
        self.assertEqual(extra, [DIRECTORY+"/manifest.json", DIRECTORY+"/queues-troubleshooting.html",
                                 "ops/migrate-growth-content.php"])
        self.assertTrue(set(release.NETWORK_TRIAGE_FILES).issubset(guarded))
        self.assertTrue(set(release.CONCEPTUAL_ROUTING_FILES).issubset(guarded))
        self.assertTrue(set(files).isdisjoint(guarded))

    def test_new_scope_retains_runtime_and_checksum_protections(self):
        self.assertIn(SCOPE, release.GUARDED_SCOPES)

    def test_manifest_changes_only_existing_owner67_body(self):
        m = json.loads((ROOT/DIRECTORY/"manifest.json").read_text())
        self.assertEqual(m["key"], SCOPE)
        self.assertEqual(m["target"]["id"], 67)
        self.assertEqual(m["target"]["change_fields"], ["post_content"])
        self.assertEqual(m["target"]["url"], "https://tehnet.ir/learn/mikrotik/mtcna/queues-troubleshooting/")
        self.assertNotIn("targets", m)
        self.assertEqual(hashlib.sha256((ROOT/DIRECTORY/m["content_file"]).read_bytes()).hexdigest(),
                         m["content_sha256_lf"])

    def test_twelve_reviewed_originals_match_bytes_and_geometry(self):
        c = json.loads((ROOT/DIRECTORY/"captures.json").read_text())
        self.assertEqual([p["name"] for p in c["captures"]], NAMES)
        for p in c["captures"]:
            f=ROOT/MEDIA/(p["name"]+".png")
            self.assertFalse(f.is_symlink())
            data=f.read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II",data[16:24]), (1536,960))
            self.assertEqual(hashlib.sha256(data).hexdigest(),p["sha256"])
            self.assertTrue(p["original_ui_pixels"] and p["visual_reviewed"])
            x,y,w,h=p["callout_rect_px"]
            self.assertTrue(0<=x and 0<=y and w>0 and h>0 and x+w<=1536 and y+h<=960)

    def test_earlier_core_scope_is_unchanged(self):
        files,_,_=release.scope_spec(release.WINBOX_CORE_SCOPE)
        self.assertEqual(len(files),40)
        self.assertFalse(any("queue-cloud-20261108" in p for p in files))

if __name__ == "__main__":
    unittest.main()
