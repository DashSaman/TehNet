# TehNet WordPress Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Safely finalize WordPress for tehnet.ir, activate the already-deployed TehNet theme/core plugin, and create an editable Gutenberg page foundation without changing host port 18082, Nginx routing, or unrelated containers.

**Architecture:** Use the existing Dockerized WordPress/MariaDB/Redis stack. Run WordPress CLI from an ephemeral container sharing only TehNet's WordPress volume and Docker network. Keep bootstrap credentials in a root-only server file outside Git. Keep the site noindex until SEO/content launch gates are passed.

**Tech Stack:** WordPress 7.x, PHP 8.3, Docker, official wordpress:cli image, custom TehNet theme, TehNet Core plugin, Gutenberg.

**Spec:** `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`

## Global Constraints

- Do not change `127.0.0.1:18082`.
- Do not modify unrelated containers, networks, volumes, or host ports.
- Do not store passwords, tokens, DB credentials, or generated admin credentials in Git.
- WordPress remains `blog_public=0` until launch readiness is explicitly approved.
- Theme owns presentation; TehNet Core owns business/domain logic.
- Gutenberg/core blocks are preferred over page-builder dependencies.
- Bootstrap must be idempotent and safe to re-run.

---
## File Structure

- `tests/wp-bootstrap-contract.sh` — static/safety contract for bootstrap script.
- `tests/gutenberg-foundation-contract.sh` — validates editable block-pattern/page foundation.
- `ops/wp-bootstrap.sh` — idempotent production bootstrap/activation script.
- `ops/wp-seed-foundation.sh` — idempotent page/menu/homepage seeding script.
- `site/themes/tehnet/inc/block-patterns.php` — TehNet Gutenberg pattern registration.
- `content/pages/home.html` — editable Gutenberg homepage starter content.
- `content/pages/about.html` — starter about copy.
- `content/pages/contact.html` — starter contact copy.
- `ops/WORDPRESS_BOOTSTRAP_EVIDENCE.md` — verified execution evidence without secrets.
- `PROGRESS.md`, `HANDOFF.md`, `TASKS.md` — coordination state.

### Task 1: Bootstrap Safety Contract

**Files:**
- Create: `tests/wp-bootstrap-contract.sh`
- Create: `ops/wp-bootstrap.sh`

**Interfaces:**
- Consumes: existing container `tehnet-wordpress`, its network and volume.
- Produces: installed WordPress with stable URL/title/locale/timezone, noindex enabled, TehNet theme/plugin activated.

- [x] **Step 1: Write a failing contract test**

The test must require explicit checks for container name, unchanged `127.0.0.1:18082`, root-only secret storage, `blog_public=0`, and no Docker compose/down/restart commands.
- [x] **Step 2: Run the contract and verify RED**

Run: `tests/wp-bootstrap-contract.sh`
Expected: `FAIL: bootstrap script missing`.

- [x] **Step 3: Implement the minimal bootstrap script**

The script must:
```bash
TARGET_CONTAINER=tehnet-wordpress
EXPECTED_BINDING='127.0.0.1:18082->80/tcp'
SECRETS_DIR=/root/tehnet-secrets
```
Detect TehNet's Docker network from the running container, export only `WORDPRESS_*` variables to a temporary mode-600 env file, and use an ephemeral `wordpress:cli` container with `--volumes-from tehnet-wordpress` and that network.

If WordPress is not installed, generate a strong password and persist only this root-only file:
`/root/tehnet-secrets/wp-admin-bootstrap.env`.

Install with canonical URL `https://tehnet.ir`, title `تهران نتورک | TehNet`, bootstrap admin `tehnetmgr`, email `admin@tehnet.ir`, and `--skip-email`. Then set `blog_public=0`, timezone `Asia/Tehran`, Persian locale where available, permalink structure `/%postname%/`, activate `tehnet` and `tehnet-core`, and flush rewrite rules.

- [x] **Step 4: Run contract and PHP/shell syntax checks**

Run: `bash -n ops/wp-bootstrap.sh && tests/wp-bootstrap-contract.sh`
Expected: PASS.

- [x] **Step 5: Commit**

`git commit -am 'ops: add safe WordPress bootstrap'` plus newly created files.
### Task 2: Editable Gutenberg Foundation

**Files:**
- Create: `tests/gutenberg-foundation-contract.sh`
- Create: `site/themes/tehnet/inc/block-patterns.php`
- Modify: `site/themes/tehnet/functions.php`
- Create: `content/pages/home.html`
- Create: `content/pages/about.html`
- Create: `content/pages/contact.html`
- Create: `ops/wp-seed-foundation.sh`

**Interfaces:**
- Consumes: active TehNet theme/core plugin and WordPress CLI wrapper from bootstrap script.
- Produces: editable core-block patterns and idempotently seeded top-level pages.

- [x] **Step 1: Write failing Gutenberg contract**

Require pattern category `tehnet`, patterns for hero/journeys/contact CTA, standard core blocks only, Persian starter content, and a seed script that creates/updates by slug rather than duplicating pages.

- [x] **Step 2: Verify RED**

Run: `tests/gutenberg-foundation-contract.sh`
Expected: FAIL because pattern/page files are absent.

- [x] **Step 3: Implement minimal patterns and starter pages**

Register patterns with `register_block_pattern_category()` and `register_block_pattern()`. Keep all business values editable and avoid hard-coded payment/product logic in the theme.

Seed slugs: `home`, `learn`, `lab`, `services`, `shop`, `about`, `contact`. Set `home` as static front page. Do not publish thin SEO articles or city doorway pages.

- [x] **Step 4: Verify GREEN and PHP lint**

Run: `tests/gutenberg-foundation-contract.sh && find site -name '*.php' -print0 | xargs -0 -n1 php -l`
Expected: all PASS/no syntax errors.
- [x] **Step 5: Commit**

`git add site/themes/tehnet content/pages ops/wp-seed-foundation.sh tests/gutenberg-foundation-contract.sh && git commit -m 'feat: add editable Gutenberg foundation'`

### Task 3: Production Bootstrap, Evidence, and Coordination

**Files:**
- Create: `ops/WORDPRESS_BOOTSTRAP_EVIDENCE.md`
- Modify: `PROGRESS.md`
- Modify: `HANDOFF.md`
- Modify: `TASKS.md`

**Interfaces:**
- Consumes: Tasks 1–2 and the existing production TehNet volume on port 18082.
- Produces: installed/activated WordPress, seeded editable pages, evidence, and exact next-step state.

- [x] **Step 1: Capture pre-run runtime fingerprint**

Record TehNet binding, container IDs/status/ports, and a separate sorted fingerprint of unrelated running containers. Do not alter any unrelated service.

- [x] **Step 2: Deploy theme/plugin/content scripts and run bootstrap**

Use the existing safe file-deploy mechanism. Run `ops/wp-bootstrap.sh`, then `ops/wp-seed-foundation.sh`.

- [x] **Step 3: Verify production**

Verify WordPress reports installed, active theme is `tehnet`, plugin `tehnet-core` is active, `blog_public=0`, front page is `home`, canonical site URL is `https://tehnet.ir`, and binding remains `127.0.0.1:18082->80/tcp`.

Verify public HTTP no longer redirects to `/wp-admin/install.php`. Confirm unrelated container fingerprint was not changed by TehNet execution.

- [x] **Step 4: Run full repository suite**

Run all executable tests under `tests/` plus PHP lint. Expected: zero failures.

- [x] **Step 5: Write evidence and coordination state, then commit**

Evidence must contain no credentials. Update progress/handoff/tasks with verified facts only and set the next phase to SEO/content architecture.
