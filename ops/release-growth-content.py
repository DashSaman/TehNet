"""Bounded TehNet service or existing-lesson release with a private config/bundle.

No credentials, endpoint inventory or raw WordPress state belongs in Git. The
production authorization marker identifies scope; it does not grant owner consent.
Normal protected integration, recovery qualification and owner gates remain external.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import subprocess
import sys
import time
import traceback

FILES = [
    'site/mu-plugins/tehnet-technical-resources/network-readiness.php',
    'site/mu-plugins/tehnet-technical-resources/network-readiness.js',
    'site/mu-plugins/tehnet-technical-resources/network-readiness.css',
    'site/plugins/tehnet-store/includes/class-tickets.php',
    'site/plugins/tehnet-store/includes/class-quotes.php',
    'site/mu-plugins/tehnet-technical-resources.php',
]
EXTRA = ['content/growth-2026-10-31/manifest.json', 'ops/migrate-growth-content.php']
SCOPE = 'tehnet-growth-20261031-v1'
EDITORIAL_SCOPE = 'tehnet-editorial-routeros-20261101-v1'
ROUTING_SCOPE = 'tehnet-editorial-routing-20261101-v1'
METADATA_SCOPE = 'tehnet-metadata-role-20261101-v1'
SERVICE_METADATA_SCOPE = 'tehnet-metadata-service-role-20261101-v1'
SUPPORT_SCOPE = 'tehnet-service-network-support-20261101-v1'
IP_DHCP_DNS_SCOPE = 'tehnet-editorial-ip-dhcp-dns-20261101-v1'
NETWORK_SETUP_SCOPE = 'tehnet-service-network-setup-20261101-v1'
REMOTE_SUPPORT_SCOPE = 'tehnet-service-remote-support-20261101-v1'
MIKROTIK_SERVICE_SCOPE = 'tehnet-service-mikrotik-20261101-v1'
LESSON_SCOPES = {
    EDITORIAL_SCOPE: ('content/growth-editorial-2026-11-01', 'routeros-winbox.html', '/tmp/tn-editorial-release-'),
    ROUTING_SCOPE: ('content/routing-editorial-2026-11-01', 'static-routing.html', '/tmp/tn-routing-release-'),
    IP_DHCP_DNS_SCOPE: ('content/ip-dhcp-dns-editorial-2026-11-01', 'ip-dhcp-dns.html', '/tmp/tn-ip-dhcp-dns-release-'),
}
CONTENT_SCOPES = {**LESSON_SCOPES,
    SUPPORT_SCOPE: ('content/network-support-2026-11-01', 'network-support.html', '/tmp/tn-network-support-release-'),
    NETWORK_SETUP_SCOPE: ('content/network-setup-2026-11-01', 'network-setup.html', '/tmp/tn-network-setup-release-'),
    REMOTE_SUPPORT_SCOPE: ('content/remote-support-2026-11-01', 'remote-support.html', '/tmp/tn-remote-support-release-'),
    MIKROTIK_SERVICE_SCOPE: ('content/mikrotik-service-2026-11-01', 'mikrotik-service.html', '/tmp/tn-mikrotik-service-release-'),
}
GUARDED_SCOPES = [*CONTENT_SCOPES, METADATA_SCOPE, SERVICE_METADATA_SCOPE]


def scope_spec(scope):
    if scope == SCOPE:
        return list(FILES), list(EXTRA), []
    if scope in CONTENT_SCOPES:
        directory, body, _ = CONTENT_SCOPES[scope]
        return [], [directory + '/manifest.json',
                    directory + '/' + body,
                    'ops/migrate-growth-content.php'], FILES + ['site/plugins/tehnet-store/tehnet-store.php'] + (
                        ['site/mu-plugins/tehnet-search-metadata.php'] if scope in (SUPPORT_SCOPE, IP_DHCP_DNS_SCOPE, NETWORK_SETUP_SCOPE, REMOTE_SUPPORT_SCOPE, MIKROTIK_SERVICE_SCOPE) else [])
    if scope == METADATA_SCOPE:
        return ['site/mu-plugins/tehnet-search-metadata.php'], [
            'content/metadata-role-2026-11-01/manifest.json', 'ops/check-metadata-state.php'
        ], FILES + ['site/plugins/tehnet-store/tehnet-store.php']
    if scope == SERVICE_METADATA_SCOPE:
        return ['site/mu-plugins/tehnet-search-metadata.php'], [
            'content/metadata-service-role-2026-11-01/manifest.json', 'ops/check-service-metadata-state.php'
        ], FILES + ['site/plugins/tehnet-store/tehnet-store.php']
    raise ValueError('Unapproved release scope')


def staging_ports_safe(bindings, allow_loopback=False):
    if not bindings:
        return True
    rows = [row for values in bindings.values() for row in (values or [])]
    return bool(allow_loopback and rows and all(row.get('HostIp') in ('127.0.0.1', '::1') for row in rows))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def member(root, name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or not p.parts:
        raise ValueError('Unsafe bundle member')
    path = root
    for part in p.parts:
        path = path / part
        if path.is_symlink():
            raise RuntimeError('Symlink member refused')
    if not path.resolve().is_relative_to(root.resolve()):
        raise RuntimeError('Member escapes root')
    return path


def atomic_write(path, data, mode, uid, gid):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp.' + secrets.token_hex(6))
    try:
        with tmp.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        tmp.chmod(mode)
        if uid is not None:
            os.chown(tmp, uid, gid)
        os.replace(tmp, path)
        directory = os.open(path.parent, os.O_RDONLY) if os.name != 'nt' else None
        if directory is not None:
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if tmp.exists():
            tmp.unlink()


def file_digest(path):
    return digest(path.read_bytes()) if path.is_file() else None


def validate_restore(root, entries):
    # Validate the complete set BEFORE restoring the first file.
    for rel, row in entries.items():
        path = member(root, rel)
        if path.exists() and not path.is_file():
            raise RuntimeError('Unexpected file type; preserve foreign state')
        if file_digest(path) not in (row['old'], row['new']):
            raise RuntimeError('File drift; preserve foreign edit')


def build_bundle(repo, output, source, baseline, scope=SCOPE):
    files, extra, runtime = scope_spec(scope)
    for commit in (source, baseline):
        if not re.fullmatch('[a-f0-9]{40}', commit):
            raise ValueError('Full immutable commit IDs required')
    if output.exists() or output.is_symlink():
        raise RuntimeError('Bundle destination must be new')
    # Resolve before any I/O: on Windows a relative cwd/../ spelling can exceed
    # MAX_PATH although its normalized destination is short. Reject links first
    # so normalization cannot adopt a dangling/redirected destination.
    reject_link_path(output)
    output = output.resolve()
    output.mkdir(mode=0o700, parents=True)

    def blob(commit, path, optional=False):
        p = subprocess.run(['git', 'show', commit + ':' + path], cwd=repo, capture_output=True)
        if p.returncode:
            if optional and subprocess.run(['git', 'cat-file', '-e', commit], cwd=repo, capture_output=True).returncode == 0:
                listing = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', commit, '--', path], cwd=repo)
                if not listing:
                    return None
            raise RuntimeError('Git object unavailable')
        return p.stdout

    metadata = {'schema': 1, 'scope': scope, 'source_commit': source, 'baseline_commit': baseline, 'files': {}, 'members': {}}
    for path in files + extra:
        data = blob(source, path)
        target = member(output / 'payload', path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        metadata['members'][path] = digest(data)
        if path in files:
            old = blob(baseline, path, True)
            metadata['files'][path] = {'old': None if old is None else digest(old), 'new': digest(data)}
    if runtime:
        metadata['runtime_guard'] = {path: digest(blob(source, path)) for path in runtime}
    tool = blob(source, 'ops/release-growth-content.py')
    (output / 'release-growth-content.py').write_bytes(tool)
    metadata['tool_sha256'] = digest(tool)
    (output / 'bundle.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    return {'status': 'BUNDLED', 'source_commit': source, 'files': len(files)}


def reject_link_path(path):
    for candidate in [path, *path.parents]:
        if candidate.is_symlink() or getattr(candidate, 'is_junction', lambda: False)():
            raise RuntimeError('Linked output path refused')


def private_diagnostics_directory(path):
    """Validate an explicit existing private destination; never create it implicitly."""
    if not path.is_absolute():
        raise RuntimeError('Absolute private diagnostics directory required')
    reject_link_path(path)
    path = path.resolve(strict=True)
    if not path.is_dir() or any((p / '.git').exists() or (p / 'wp-config.php').exists() for p in [path, *path.parents]):
        raise RuntimeError('Diagnostics must be outside repositories and WordPress roots')
    if os.name == 'nt':
        # chmod does not establish a private Windows DACL. Inspect actual allow
        # rules using SIDs; raw account names/paths never leave this subprocess.
        script = r'''$ErrorActionPreference='Stop'
$acl=[System.IO.Directory]::GetAccessControl($env:TN_RELEASE_DIAGNOSTICS_ROOT)
$allowed=@([System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value,'S-1-5-18','S-1-5-32-544')
# Python's private temporary directories can grant OWNER RIGHTS rather than the
# account SID. Accept that rule only when the actual owner is already allowed.
if($allowed -notcontains $acl.GetOwner([System.Security.Principal.SecurityIdentifier]).Value){exit 1}
$allowed+='S-1-3-4'
$rules=@($acl.GetAccessRules($true,$true,[System.Security.Principal.SecurityIdentifier]) | Where-Object { $_.AccessControlType -eq 'Allow' })
if($rules.Count -eq 0){exit 1}
foreach($rule in $rules){
 if($allowed -contains $rule.IdentityReference.Value){continue}
 # Creator-owner inheritance resolves to this process for a newly owned log.
 if($rule.IdentityReference.Value -eq 'S-1-3-0' -and ($rule.PropagationFlags -band [System.Security.AccessControl.PropagationFlags]::InheritOnly)){continue}
 exit 1
}
exit 0'''
        import base64
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', base64.b64encode(script.encode('utf-16le')).decode()],
                                env={**os.environ, 'TN_RELEASE_DIAGNOSTICS_ROOT': str(path)}, capture_output=True, timeout=20,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if result.returncode:
            raise RuntimeError('Restricted Windows diagnostics ACL required')
    elif path.stat().st_mode & 0o077:
        raise RuntimeError('Restricted diagnostics permissions required')
    return path


def save_failure(directory, detail):
    name = 'failure-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + secrets.token_hex(6) + '.log'
    # Directory was validated before execution; recheck before a failure write.
    directory = private_diagnostics_directory(directory)
    atomic_write(directory / name, detail.encode('utf-8'), 0o600, None, None)


class Release:
    def __init__(self, config_path, bundle):
        import fcntl
        os.umask(0o077)
        if config_path.is_symlink() or config_path.stat().st_mode & 0o077:
            raise RuntimeError('Private config required')
        self.c = json.loads(config_path.read_text())
        self.b = bundle.resolve()
        self.m = json.loads(member(self.b, 'bundle.json').read_text())
        c, m = self.c, self.m
        self.scope = m['scope']
        self.files, self.extra, runtime = scope_spec(self.scope)
        if self.scope in GUARDED_SCOPES and digest(member(self.b, 'bundle.json').read_bytes()) != c.get('bundle_manifest_sha256'):
            raise RuntimeError('Approved editorial bundle metadata checksum required')
        if m['schema'] != 1 or set(m['members']) != set(self.files + self.extra) or list(m['files']) != self.files or set(m.get('runtime_guard', {})) != set(runtime):
            raise RuntimeError('Unexpected bundle scope')
        if any(not re.fullmatch('[a-f0-9]{64}', value) for value in m.get('runtime_guard', {}).values()):
            raise RuntimeError('Runtime guard requires complete digests')
        if m['source_commit'] != c['source_commit'] or m['baseline_commit'] != c['baseline_commit']:
            raise RuntimeError('Approved source/baseline mismatch')
        if digest(Path(__file__).read_bytes()) != m['tool_sha256']:
            raise RuntimeError('Release tool differs from immutable bundle')
        for path, expected in m['members'].items():
            if file_digest(member(self.b / 'payload', path)) != expected:
                raise RuntimeError('Bundle checksum mismatch')
        for path, row in m['files'].items():
            if row['new'] != m['members'][path]:
                raise RuntimeError('Bundle identity mismatch')
        if c['environment'] not in ('production', 'staging') or not re.fullmatch('[a-f0-9]{64}', c['app_id']) or not re.fullmatch('[a-f0-9]{64}', c['db_id']):
            raise RuntimeError('Target identity required')
        self.directory = Path(c['release_dir'])
        if not self.directory.is_absolute() or self.directory.is_symlink() or self.directory.exists():
            if not self.directory.is_absolute() or self.directory.is_symlink() or not self.directory.is_dir():
                raise RuntimeError('Private release directory required')
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.directory.stat().st_mode & 0o077:
            raise RuntimeError('Private release permissions required')
        self.lock = (self.directory.parent / '.tn-growth-release.lock').open('a+b')
        os.chmod(self.lock.name, 0o600)
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.log = (self.directory / 'commands-private.log').open('ab')
        self.receipt_path = self.directory / 'release-private.json'
        self.state = json.loads(self.receipt_path.read_text()) if self.receipt_path.exists() else None
        if self.state and (self.state['source_commit'] != m['source_commit'] or self.state['app_id'] != c['app_id'] or self.state['db_id'] != c['db_id']):
            raise RuntimeError('Release journal identity mismatch')
        prefix = '/tmp/tn-metadata-service-role-' if self.scope == SERVICE_METADATA_SCOPE else ('/tmp/tn-metadata-role-' if self.scope == METADATA_SCOPE else (CONTENT_SCOPES[self.scope][2] if self.scope in CONTENT_SCOPES else '/tmp/tn-growth-release-'))
        self.container_stage = prefix + m['source_commit']
        self.manifest_digest = m['members'][self.extra[0]]
        self.root = None

    def run(self, args, data=None, timeout=180, cwd=None):
        p = subprocess.run(args, input=data, capture_output=True, timeout=timeout, cwd=cwd)
        self.log.write(p.stdout + p.stderr)
        self.log.flush()
        if p.returncode:
            raise RuntimeError('Command failed; inspect private release log')
        return p.stdout

    def inspect(self, identity):
        return json.loads(self.run(['docker', 'inspect', identity]))[0]

    def target(self):
        app, db = self.inspect(self.c['app']), self.inspect(self.c['db'])
        if app['Id'] != self.c['app_id'] or db['Id'] != self.c['db_id'] or not app['State']['Running'] or not db['State']['Running']:
            raise RuntimeError('Target runtime drift')
        roots = [p['Source'] for p in app['Mounts'] if p['Destination'] == '/var/www/html']
        if len(roots) != 1:
            raise RuntimeError('Ambiguous WordPress mount')
        self.root = Path(roots[0]) / 'wp-content'
        if self.directory.resolve().is_relative_to(Path(roots[0]).resolve()):
            raise RuntimeError('Private journal must be outside the web root')
        if self.c['environment'] == 'production':
            if self.c.get('authorization') != self.scope or self.c['app'] != 'tehnet-wordpress' or self.c['db'] != 'tehnet-db':
                raise RuntimeError('Unapproved production scope')
            if self.run(['docker', 'port', self.c['app'], '80/tcp']).decode().strip() != '127.0.0.1:18082':
                raise RuntimeError('Production routing drift')
        else:
            networks = app['NetworkSettings']['Networks']
            loopback = self.scope in GUARDED_SCOPES
            if set(networks) != {self.c['network']} or set(db['NetworkSettings']['Networks']) != set(networks) or not staging_ports_safe(app['HostConfig']['PortBindings'], loopback) or not staging_ports_safe(db['HostConfig']['PortBindings']):
                raise RuntimeError('Staging network/port isolation missing')
            if loopback and app['HostConfig']['PortBindings'] != self.c.get('staging_app_bindings'):
                raise RuntimeError('Existing loopback preview binding drift')
            net = json.loads(self.run(['docker', 'network', 'inspect', self.c['network']]))[0]
            if not net['Internal']:
                raise RuntimeError('Staging network is not internal')
        for rel in self.files + list(self.m.get('runtime_guard', {})):
            member(self.root, rel.removeprefix('site/'))

    def stage(self):
        self.run(['docker', 'exec', self.c['app'], 'mkdir', '-p', self.container_stage + '/journal'])
        self.run(['docker', 'exec', self.c['app'], 'chmod', '700', self.container_stage, self.container_stage + '/journal'])
        staged = [(self.extra[0], 'manifest.json'), (self.extra[-1], 'migration.php')]
        if self.scope in CONTENT_SCOPES:
            staged.append((self.extra[1], CONTENT_SCOPES[self.scope][1]))
        for source, name in staged:
            self.run(['docker', 'cp', str(member(self.b / 'payload', source)), self.c['app'] + ':' + self.container_stage + '/' + name])
        # Syntax-check every PHP artifact before the first live file write.
        for path in [p for p in self.files if p.endswith('.php')]:
            self.run(['docker', 'exec', '-i', self.c['app'], 'php', '-l'], member(self.b / 'payload', path).read_bytes())
        self.run(['docker', 'exec', self.c['app'], 'php', '-l', self.container_stage + '/migration.php'])

    def native(self, mode, journal='journal'):
        env = {'TN_GROWTH_MANIFEST': self.container_stage + '/manifest.json', 'TN_GROWTH_DIGEST': self.manifest_digest,
               'TN_GROWTH_JOURNAL_DIR': self.container_stage + '/' + journal, 'TN_GROWTH_MODE': mode}
        if self.c['environment'] == 'production':
            env['TN_GROWTH_AUTHORIZED_RELEASE'] = self.scope
        args = ['docker', 'exec']
        for key, value in env.items():
            args += ['-e', key + '=' + value]
        raw = self.run(args + [self.c['app'], 'php', self.c['wp_cli'], '--allow-root', '--path=/var/www/html', '--user=' + self.c['wp_user'], 'eval-file', self.container_stage + '/migration.php'])
        result = json.loads(raw)
        if journal == 'journal' and mode != 'check':
            self.run(['docker', 'cp', self.c['app'] + ':' + self.container_stage + '/journal/journal.json', str(self.directory / 'content-journal-private.json')])
            os.chmod(self.directory / 'content-journal-private.json', 0o600)
        return result

    def save(self):
        self.state['updated_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        atomic_write(self.receipt_path, json.dumps(self.state, indent=2).encode(), 0o600, None, None)

    def runtime_guard(self):
        for rel, expected in self.m.get('runtime_guard', {}).items():
            if file_digest(member(self.root, rel.removeprefix('site/'))) != expected:
                raise RuntimeError('Protected runtime drift; preserve other code')

    def file_guard(self, after=False):
        self.runtime_guard()
        for rel, entry in self.m['files'].items():
            path = member(self.root, rel.removeprefix('site/'))
            if path.exists() and not path.is_file() or file_digest(path) != entry['new' if after else 'old']:
                raise RuntimeError('Managed-file drift gate failed')

    def backup(self):
        if self.c['environment'] == 'production':
            script = Path('/opt/tehnet/bin/store-backup.sh')
            if digest(script.read_bytes()) != self.c['backup_script_sha256'] or not self.c.get('recovery_qualified_utc'):
                raise RuntimeError('Reviewed backup/recovery qualification required')
            started = time.time()
            self.run(['systemctl', 'start', 'tehnet-store-backup.service'], timeout=600)
            backup = max(Path('/root/tehnet-backups').glob('*-store-review'), key=lambda p: p.stat().st_mtime)
            if backup.stat().st_mtime < started - 2:
                raise RuntimeError('Fresh production backup missing')
            self.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=backup)
            self.state['backup_private'] = str(backup)
            self.state['backup_checksum_verified'] = True
        else:
            sql = self.run(['docker', 'exec', self.c['db'], 'sh', '-c', 'exec mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" --single-transaction --quick "$MARIADB_DATABASE"'])
            atomic_write(self.directory / 'before-private.sql', sql, 0o600, None, None)
            self.state['backup_checksum_verified'] = file_digest(self.directory / 'before-private.sql') == digest(sql)
        entries = {}
        for rel, row in self.m['files'].items():
            path = member(self.root, rel.removeprefix('site/'))
            old = path.read_bytes() if path.exists() else None
            if (None if old is None else digest(old)) != row['old']:
                raise RuntimeError('File changed before backup')
            stat = path.stat() if path.exists() else None
            entries[rel.removeprefix('site/')] = dict(row, mode=stat.st_mode & 0o777 if stat else 0o644, uid=stat.st_uid if stat else 33, gid=stat.st_gid if stat else 33)
            if old is not None:
                target = member(self.directory / 'before', rel.removeprefix('site/'))
                atomic_write(target, old, 0o600, None, None)
        self.state['files'] = entries
        self.save()

    def restore_files(self):
        validate_restore(self.root, self.state['files'])
        for rel, row in self.state['files'].items():
            if row['old'] is not None and file_digest(member(self.directory / 'before', rel)) != row['old']:
                raise RuntimeError('Private file backup checksum mismatch')
        for rel in reversed(self.files):
            rel = rel.removeprefix('site/')
            row, path = self.state['files'][rel], member(self.root, rel)
            if file_digest(path) not in (row['old'], row['new']):
                raise RuntimeError('Concurrent file edit during restoration')
            if row['old'] is None:
                if path.exists():
                    path.unlink()
            else:
                old = member(self.directory / 'before', rel).read_bytes()
                if digest(old) != row['old']:
                    raise RuntimeError('Private file backup checksum mismatch')
                atomic_write(path, old, row['mode'], row['uid'], row['gid'])
        self.file_guard()

    def rollback(self):
        if not self.state or self.state['status'] not in ('APPLIED', 'ROLLED_BACK'):
            raise RuntimeError('Explicit reconciliation required before rollback')
        validate_restore(self.root, self.state['files'])
        if self.scope in GUARDED_SCOPES:
            self.runtime_guard()
        # If content restoration is refused, leave modules available and retain all evidence.
        result = self.native('rollback')
        self.restore_files()
        self.state['status'] = 'ROLLED_BACK'
        self.state['rollback'] = result
        self.save()
        return {'status': 'ROLLED_BACK', 'files_restored': len(self.files), 'content': result}

    def execute(self, mode):
        self.target()
        self.stage()
        if mode == 'rollback':
            return self.rollback()
        if self.state:
            if self.state['status'] != 'APPLIED':
                raise RuntimeError('Existing release requires reconciliation or explicit rollback')
            self.file_guard(after=True)
            return {'status': 'APPLIED', 'files_changed': 0, 'content': self.native('check')}
        self.file_guard()
        check = self.native('check')
        if check['status'] != 'READY':
            raise RuntimeError('Clean content baseline required')
        if mode == 'check':
            return {'status': 'READY', 'files_pending': len(self.files), 'content': check}
        self.state = {'schema': 1, 'status': 'PREPARED', 'source_commit': self.m['source_commit'], 'app_id': self.c['app_id'], 'db_id': self.c['db_id'], 'preflight': check}
        self.save()
        self.backup()
        self.target()
        self.file_guard()
        if self.native('check') != check:
            raise RuntimeError('Content/protected state changed during backup')
        try:
            for rel in self.files:
                row = self.state['files'][rel.removeprefix('site/')]
                self.file_guard_partial(rel)
                destination = member(self.root, rel.removeprefix('site/'))
                if not destination.parent.exists():
                    destination.parent.mkdir(mode=0o755)
                    destination.parent.chmod(0o755)
                    os.chown(destination.parent, row['uid'], row['gid'])
                atomic_write(destination, member(self.b / 'payload', rel).read_bytes(), row['mode'], row['uid'], row['gid'])
            self.file_guard(after=True)
            self.state['status'] = 'FILES_APPLIED'
            self.save()
            applied = self.native('apply')
            self.file_guard(after=True)
            if applied['status'] != 'APPLIED' or applied['protected_digest'] != check['protected_digest']:
                raise RuntimeError('Protected state changed across file/content release')
            repeated = self.native('check')
            if repeated['status'] != 'APPLIED' or not repeated['protected_state_unchanged']:
                raise RuntimeError('Post-release native check failed')
            self.state['status'], self.state['content'] = 'APPLIED', applied
            self.save()
            return {'status': 'APPLIED', 'files_changed': len(self.files), 'content': applied}
        except BaseException:
            self.state['status'] = 'NEEDS_RECONCILIATION'
            self.save()
            # Never guess whether a database COMMIT succeeded. Only proven states permit undo.
            try:
                if self.scope in GUARDED_SCOPES:
                    self.runtime_guard()
                raw = self.run(['docker', 'exec', self.c['app'], 'sh', '-c', 'if test -f ' + self.container_stage + '/journal/journal.json; then cat ' + self.container_stage + '/journal/journal.json; else printf null; fi'])
                journal = json.loads(raw)
                if journal and journal['status'] == 'APPLIED':
                    self.native('rollback')
                elif journal is None or journal['status'] == 'FAILED':
                    fresh = self.container_stage + '/failure-check'
                    self.run(['docker', 'exec', self.c['app'], 'mkdir', '-m', '700', fresh])
                    if self.native('check', 'failure-check') != check:
                        raise RuntimeError('Cannot prove unchanged content after failure')
                else:
                    raise RuntimeError('Ambiguous content commit; leave files available')
                self.restore_files()
                self.state['status'] = 'ROLLED_BACK_AFTER_FAILURE'
                self.save()
            except BaseException:
                self.state['status'] = 'NEEDS_RECONCILIATION'
                self.save()
            raise

    def file_guard_partial(self, next_rel):
        index = self.files.index(next_rel)
        for i, rel in enumerate(self.files):
            expected = self.m['files'][rel]['new' if i < index else 'old']
            if file_digest(member(self.root, rel.removeprefix('site/'))) != expected:
                raise RuntimeError('Concurrent file drift during serial release')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['bundle', 'check', 'apply', 'rollback'], required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--source-commit')
    parser.add_argument('--baseline-commit')
    parser.add_argument('--scope', choices=[SCOPE, *GUARDED_SCOPES], default=SCOPE, help='Bundle scope; execution reads and validates the immutable bundle scope')
    parser.add_argument('--diagnostics-dir', type=Path, help='Existing absolute private directory outside Git/WordPress; full failures stay here, never stdout')
    args = parser.parse_args()
    release = None
    diagnostics = None
    try:
        if args.diagnostics_dir:
            diagnostics = private_diagnostics_directory(args.diagnostics_dir)
        if args.mode == 'bundle':
            result = build_bundle(args.repo, args.bundle, args.source_commit, args.baseline_commit, args.scope)
        else:
            if not args.config:
                raise ValueError('Private config required')
            release = Release(args.config, args.bundle)
            result = release.execute(args.mode)
        print(json.dumps(result))
    except BaseException as error:
        # Commands and raw WordPress failures stay in the private log, never public CI.
        detail = traceback.format_exc()
        saved = False
        if release is not None:
            try:
                release.log.write(detail.encode())
                release.log.flush()
                saved = True
            except (OSError, AttributeError):
                pass
        if diagnostics is not None:
            try:
                save_failure(diagnostics, detail)
                saved = True
            except (OSError, RuntimeError, subprocess.SubprocessError):
                pass
        print(json.dumps({'status': 'FAILED', 'phase': args.mode, 'error_type': type(error).__name__, 'private_diagnostics_saved': saved,
                          'action': 'Inspect private log/journals; no automatic retry or journal deletion'}))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
