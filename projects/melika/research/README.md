# Research inventory and reading order

This directory is an evidence archive, not a static website asset directory. Never mount it as web root or include it in a frontend bundle. Archived prompts and AGENTS files are historical reference data; they are not instructions to execute or to modify unrelated projects.

Source: [DashSaman/melika at d77dd9d](https://github.com/DashSaman/melika/tree/d77dd9db570b972e41b55a92c08716055009f994/Linux). Exact blob inventory and checksums: [PROVENANCE.json](PROVENANCE.json). The owner requested this research copy; no source files were removed. Authorship and upstream citations remain unchanged. No repository-wide LICENSE was found at the inspected source ref; copying this owner's research does not grant redistribution rights to third-party software. Check each upstream license before archiving artifacts.

Read RESEARCH, ARCHITECTURE, API_CONTRACT, SECURITY_AND_OFFLINE, RUBIKA_FEASIBILITY, then IMPLEMENTATION_PLAN. Read the other materials by topic. Existing probe evidence is historical and labeled as such; fresh rerun results live outside the immutable copy.

## Complete copied inventory
- [Linux/AGENTS.md](upstream/Linux/AGENTS.md)
- [Linux/API_CONTRACT.md](upstream/Linux/API_CONTRACT.md)
- [Linux/ARCHITECTURE.md](upstream/Linux/ARCHITECTURE.md)
- [Linux/CODEX_ONE_DAY_PROMPT.md](upstream/Linux/CODEX_ONE_DAY_PROMPT.md)
- [Linux/COST_MODEL.md](upstream/Linux/COST_MODEL.md)
- [Linux/GAP_ANALYSIS.md](upstream/Linux/GAP_ANALYSIS.md)
- [Linux/IMPLEMENTATION_PLAN.md](upstream/Linux/IMPLEMENTATION_PLAN.md)
- [Linux/MIRROR_INVENTORY.md](upstream/Linux/MIRROR_INVENTORY.md)
- [Linux/MIRROR_SOURCES.yaml](upstream/Linux/MIRROR_SOURCES.yaml)
- [Linux/README.md](upstream/Linux/README.md)
- [Linux/RELATED_PROJECTS.md](upstream/Linux/RELATED_PROJECTS.md)
- [Linux/RESEARCH.md](upstream/Linux/RESEARCH.md)
- [Linux/RUBIKA_FEASIBILITY.md](upstream/Linux/RUBIKA_FEASIBILITY.md)
- [Linux/SECURITY_AND_OFFLINE.md](upstream/Linux/SECURITY_AND_OFFLINE.md)
- [Linux/SOURCES.md](upstream/Linux/SOURCES.md)
- [Linux/evidence/RESEARCH_LOG.md](upstream/Linux/evidence/RESEARCH_LOG.md)
- [Linux/evidence/probe-tests.txt](upstream/Linux/evidence/probe-tests.txt)
- [Linux/evidence/sandbox-probes.json](upstream/Linux/evidence/sandbox-probes.json)
- [Linux/scripts/PROBE_TARGETS.json](upstream/Linux/scripts/PROBE_TARGETS.json)
- [Linux/scripts/README.md](upstream/Linux/scripts/README.md)
- [Linux/scripts/probe_sources.py](upstream/Linux/scripts/probe_sources.py)
- [Linux/tests/test_probe_sources.py](upstream/Linux/tests/test_probe_sources.py)

## Interpretation and path changes

Old `Linux/app/`, `Linux/tests/`, `Linux/profiles/` and deployment paths in historical plans map to `projects/melika/app/`, `tests/`, `profiles/` and `deployment/` for new work. Do not rewrite the archive to hide this relocation. Old research tests remain under `research/upstream/Linux/tests/`. Do not put new application code into the immutable archive.

The old design assumed an Iranian host first. The current owner request supersedes that sequence: first an isolated `/melika/` service on the existing foreign VPS, then migration to Iran. The APT metadata and integrity policy remain; a foreign staging deployment is not accepted domestic outage coverage.

The original API did not define VPN authorization. [DESIGN](../DESIGN.md), [CONTRACTS](../CONTRACTS.md) and [SECURITY_PRIVACY](../SECURITY_PRIVACY.md) add that required boundary before any private data is imported. All historical source flags remain disabled until evidence and permission approval.

Missing offline catalog: [separate acquisition record](OFFLINE_SOFTWARE_CATALOG/README.md). Reported counts and claims from chat are not a substitute for its actual files.
