CREATE TABLE sources (
 visibility TEXT NOT NULL DEFAULT 'restricted' CHECK(visibility IN ('public','restricted')),
 id TEXT PRIMARY KEY, provider TEXT NOT NULL, ecosystem TEXT NOT NULL,
 base_url TEXT NOT NULL, suite_map_json TEXT NOT NULL DEFAULT '{}',
 allowed_hosts_json TEXT NOT NULL, config_json TEXT NOT NULL,
 routing_enabled INTEGER NOT NULL DEFAULT 0 CHECK(routing_enabled IN (0,1)),
 permission_state TEXT NOT NULL DEFAULT 'unreviewed',
 domestic_state TEXT NOT NULL DEFAULT 'unverified',
 failure_domain TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE snapshots (
 id TEXT PRIMARY KEY, suite TEXT NOT NULL, inrelease_sha256 TEXT NOT NULL,
 release_date TEXT NOT NULL, valid_until TEXT, acquired_at TEXT NOT NULL,
 origin_source_id TEXT NOT NULL REFERENCES sources(id),
 local_relpath TEXT NOT NULL, status TEXT NOT NULL,
 UNIQUE(suite,inrelease_sha256)
);
CREATE TABLE artifacts (
 visibility TEXT NOT NULL DEFAULT 'restricted' CHECK(visibility IN ('public','restricted')),
 sha256 TEXT PRIMARY KEY CHECK(length(sha256)=64), size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),
 ecosystem TEXT NOT NULL, name TEXT NOT NULL, version TEXT NOT NULL,
 architecture TEXT NOT NULL, filename TEXT NOT NULL, license_state TEXT NOT NULL,
 critical INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL
);
CREATE TABLE artifact_paths (
 snapshot_id TEXT NOT NULL REFERENCES snapshots(id), path TEXT NOT NULL,
 sha256 TEXT NOT NULL REFERENCES artifacts(sha256),
 PRIMARY KEY(snapshot_id,path)
);
CREATE TABLE probes (
 id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id),
 sha256 TEXT REFERENCES artifacts(sha256), path TEXT NOT NULL,
 checked_at TEXT NOT NULL, vantage TEXT NOT NULL, outcome TEXT NOT NULL,
 http_status INTEGER, range_supported INTEGER, tls_verified INTEGER,
 latency_ms REAL, body_bytes INTEGER, full_hash_verified INTEGER NOT NULL DEFAULT 0,
 error_code TEXT, retry_after_seconds INTEGER, evidence_relpath TEXT
);
CREATE TABLE locations (
 source_id TEXT NOT NULL REFERENCES sources(id), sha256 TEXT NOT NULL REFERENCES artifacts(sha256),
 path TEXT NOT NULL, state TEXT NOT NULL, verified_at TEXT, expires_at TEXT,
 evidence_probe_id INTEGER REFERENCES probes(id), PRIMARY KEY(source_id,sha256,path)
);
CREATE TABLE storage_objects (
 sha256 TEXT NOT NULL REFERENCES artifacts(sha256), backend TEXT NOT NULL,
 object_key TEXT NOT NULL, status TEXT NOT NULL, verified_at TEXT,
 PRIMARY KEY(sha256,backend)
);
CREATE TABLE profiles (
 visibility TEXT NOT NULL DEFAULT 'restricted' CHECK(visibility IN ('public','restricted')),
 id TEXT PRIMARY KEY, definition_json TEXT NOT NULL, manifest_json TEXT NOT NULL,
 baseline_digest TEXT, accepted_at TEXT, acceptance_evidence_relpath TEXT
);
CREATE TABLE jobs (
 id INTEGER PRIMARY KEY, dedupe_key TEXT NOT NULL UNIQUE, kind TEXT NOT NULL,
 payload_json TEXT NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
 not_before TEXT NOT NULL, locked_at TEXT, last_error TEXT
);
CREATE TABLE audit_events (
 id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, actor TEXT NOT NULL,
 action TEXT NOT NULL, target TEXT NOT NULL, detail_json TEXT NOT NULL
);
CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY,sha256 TEXT NOT NULL);
CREATE INDEX source_visibility ON sources(visibility,id);
CREATE INDEX artifact_visibility ON artifacts(visibility,name);
