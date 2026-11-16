# -*- coding: utf-8 -*-
"""Preview-only HTTP server for render evidence: serves the content tree with
explicit UTF-8 charset (mimicking the WordPress theme header). NOT part of the
deliverables. Run: python -I preview-server.py [port]"""
import http.server, sys
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8137
ROOT = '../../content/seo-device-guides-20261116'

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def guess_type(self, path):
        t = super().guess_type(path)
        if t == 'text/html':
            return 'text/html; charset=utf-8'
        if path.endswith('.svg'):
            return 'image/svg+xml; charset=utf-8'
        return t

http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
