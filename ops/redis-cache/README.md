# Redis Object Cache — 2026-10-27

Live state: WordPress object cache backed by the existing `tehnet-redis` container, **DB 1** dedicated, salt `tehnet-ir`, official drop-in from the `redis-cache` plugin **3.0.0** (`includes/object-cache.php`, sha256 `2e1758eb3049e0dd0d4e310cef4cfe2dd4359cf1c4c8bef47b65a80cacbed59d`).

## Layout
- `wp-content/object-cache.php` — guard loader (this repo: `object-cache-guard.php`): uses the Redis drop-in when the `redis` PHP extension is present, else falls back to core `wp-includes/cache.php`. This makes extension loss non-fatal.
- `wp-content/object-cache-redis.php` — official drop-in (not committed; verified by sha256 above).
- `wp-config.php` — added block: `WP_REDIS_HOST=tehnet-redis`, `WP_REDIS_PORT=6379`, `WP_REDIS_DATABASE=1`, `WP_CACHE_KEY_SALT=tehnet-ir`, `WP_REDIS_MAXTTL=86400`.

## Verification (2026-10-27)
- Probe key visible in redis DB 1; dbsize grew from 0 to ~30 keys under load.
- `docker restart tehnet-redis`: site stayed HTTP 200 throughout (graceful fallback), keys repopulated after restart.
- Rollback: `rm wp-content/object-cache.php wp-content/object-cache-redis.php` (core cache resumes) and remove the wp-config block.

## Persistence caveat (important)
The `redis` extension was compiled with `pecl install redis-6.1.0 && docker-php-ext-enable redis` **inside the running stock WordPress container** — it does not survive container recreation. The guard makes that event safe (automatic fallback), but after any recreate, re-run the pecl step or bake the extension into the image at the next deploy window.
