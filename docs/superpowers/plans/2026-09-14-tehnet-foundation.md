# TehNet Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a safe, editable TehNet WordPress foundation without changing or colliding with any existing server port or non-TehNet project.

**Architecture:** Keep the existing TehNet Docker stack and localhost port `18082`. Add a presentation-only custom theme and a separate `tehnet-core` plugin for domain logic/settings. Deploy only theme/plugin files into the existing WordPress volume after backup and port/container regression checks.

**Tech Stack:** WordPress 7.x, PHP 8.3, WooCommerce-ready theme conventions, Gutenberg, Docker Compose, MariaDB, Redis, Nginx, Bash contract tests.

**Spec:** `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`

## Global Constraints
- Never alter ports for TehNet or any other project in this plan.
- Do not stop/restart unrelated containers.
- Do not commit `.env`, DB dumps, credentials, or private keys.
- Theme contains presentation only; business settings/domain logic belong in `tehnet-core`.
- Routine phone/address/social/CTA changes must be editable in WordPress admin.
- Persian RTL and blue/turquoise/white are the visual baseline.
- Production changes require a pre-change backup and post-change container/port regression check.

---

### Task 1: Production baseline and recovery evidence

**Files:**
- Create: `ops/PRODUCTION_BASELINE.md`
- Create: `ops/BACKUP_RECOVERY.md`
- Create: `tests/production-isolation-contract.sh`

**Interfaces:**
- Consumes: existing `/opt/tehnet/compose.yaml`, Nginx site config, Docker inventory.
- Produces: documented TehNet identifiers and a contract proving no forbidden port/container changes.

- [ ] **Step 1: Write failing isolation contract**

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
BASELINE=ops/PRODUCTION_BASELINE.md
grep -q '127.0.0.1:18082' "$BASELINE"
grep -q 'tehnet-wordpress' "$BASELINE"
grep -q 'tehnet-db' "$BASELINE"
grep -q 'tehnet-redis' "$BASELINE"
```

- [ ] **Step 2: Run and verify RED**

Run: `bash tests/production-isolation-contract.sh`
Expected: FAIL because baseline documentation does not exist yet.

- [ ] **Step 3: Capture sanitized production facts and backup procedure**

Record current TehNet containers, compose path, localhost binding, Docker network/volumes, Nginx site path and a no-secret backup/restore procedure. Create a real timestamped backup under `/root/tehnet-backups/` but never commit backup bytes.

- [ ] **Step 4: Run and verify GREEN**

Run: `bash tests/production-isolation-contract.sh`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add ops tests/production-isolation-contract.sh
git commit -m "docs: record TehNet production isolation baseline"
```

### Task 2: Theme foundation

**Files:**
- Create: `site/themes/tehnet/style.css`
- Create: `site/themes/tehnet/theme.json`
- Create: `site/themes/tehnet/functions.php`
- Create: `site/themes/tehnet/index.php`
- Create: `site/themes/tehnet/header.php`
- Create: `site/themes/tehnet/footer.php`
- Create: `tests/theme-contract.sh`

**Interfaces:**
- Consumes: WordPress theme APIs and `tehnet-core` settings via `get_option()` only.
- Produces: RTL-ready presentation layer with centralized design tokens and no business logic.

- [ ] **Step 1: Write failing theme contract**

Test for a valid theme header, `add_theme_support('title-tag')`, RTL support, `theme.json`, and absence of payment/ticket/license implementation symbols in theme files.

- [ ] **Step 2: Run and verify RED**

Run: `bash tests/theme-contract.sh`
Expected: FAIL because theme files are absent.

- [ ] **Step 3: Implement minimal theme foundation**

Use CSS custom properties for `--tn-blue`, `--tn-turquoise`, `--tn-white`; register navigation menus; enable title-tag, thumbnails, HTML5, responsive embeds and WooCommerce theme support. Keep templates minimal and editable through blocks.

- [ ] **Step 4: Run PHP lint and GREEN contract**

Run: `find site/themes/tehnet -name '*.php' -print0 | xargs -0 -n1 php -l && bash tests/theme-contract.sh`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add site/themes/tehnet tests/theme-contract.sh
git commit -m "feat: add TehNet WordPress theme foundation"
```

### Task 3: TehNet Core settings foundation

**Files:**
- Create: `site/plugins/tehnet-core/tehnet-core.php`
- Create: `site/plugins/tehnet-core/includes/class-settings.php`
- Create: `site/plugins/tehnet-core/includes/class-content-types.php`
- Create: `tests/core-plugin-contract.sh`

**Interfaces:**
- Produces options: `tehnet_phone`, `tehnet_address`, `tehnet_youtube_url`, `tehnet_telegram_url`, `tehnet_instagram_url`, `tehnet_primary_cta`.
- Produces content types: `tn_service`, `tn_lab`.
- Theme may read these options but must not register/administer them.

- [ ] **Step 1: Write failing plugin contract**

Test plugin header, settings keys, capability checks, sanitization callbacks, and `tn_service`/`tn_lab` registration.

- [ ] **Step 2: Run and verify RED**

Run: `bash tests/core-plugin-contract.sh`
Expected: FAIL because plugin implementation is absent.

- [ ] **Step 3: Implement minimal settings/content models**

Add a TehNet Settings admin page using Settings API. Default phone is `021-91018746`; default address is `تهران، آیت‌الله کاشانی، شاهین جنوبی`. Register Services and Lab as public REST-enabled custom post types.

- [ ] **Step 4: Lint and verify GREEN**

Run: `find site/plugins/tehnet-core -name '*.php' -print0 | xargs -0 -n1 php -l && bash tests/core-plugin-contract.sh`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add site/plugins/tehnet-core tests/core-plugin-contract.sh
git commit -m "feat: add TehNet Core settings and content models"
```

### Task 4: Safe deploy without port changes

**Files:**
- Create: `ops/deploy-theme-plugin.sh`
- Create: `tests/deploy-contract.sh`
- Modify: `HANDOFF.md`
- Modify: `PROGRESS.md`
- Modify: `TASKS.md`

**Interfaces:**
- Consumes: existing `tehnet-wordpress` container and WordPress volume.
- Produces: deployed theme/plugin files only; no compose or Nginx changes.

- [ ] **Step 1: Write failing deploy contract**

Require deploy script to target only `tehnet-wordpress`, copy only `site/themes/tehnet` and `site/plugins/tehnet-core`, and reject modification of `/opt/tehnet/compose.yaml` or Nginx files.

- [ ] **Step 2: Run and verify RED**

Run: `bash tests/deploy-contract.sh`
Expected: FAIL because deploy script is absent.

- [ ] **Step 3: Implement deploy script**

The script verifies container identity, records before/after published ports for all containers, copies theme/plugin into `/var/www/html/wp-content/...`, applies `www-data` ownership, runs PHP lint inside the container, and fails if the global container/port inventory changes.

- [ ] **Step 4: Run tests then production deploy**

Run: `bash tests/deploy-contract.sh && sudo bash ops/deploy-theme-plugin.sh`
Expected: PASS; TehNet remains on `127.0.0.1:18082`; unrelated containers remain unchanged.

- [ ] **Step 5: Update coordination and commit**

```bash
git add ops site tests HANDOFF.md PROGRESS.md TASKS.md
git commit -m "ops: deploy isolated TehNet foundation safely"
```

## Self-review
- Spec coverage for this plan: safe foundation, editable settings, theme/plugin separation, RTL/design baseline, production isolation.
- Intentionally deferred to separate plans: SEO query architecture, YouTube migration, WooCommerce workflows, licensing, ticket/Telegram sync, NoPayments/rial gateways, full account dashboard.
- No implementation in this plan may change a host port or unrelated service.
