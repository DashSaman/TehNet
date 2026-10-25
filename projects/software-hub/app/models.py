"""Frozen W0 v1 contracts. Models are not evidence of implemented capabilities."""
from datetime import datetime
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

Visibility = Literal['public', 'restricted']
Mode = Literal['ONLINE', 'DOMESTIC_ONLY', 'MAINTENANCE']
Digest = str


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


class Artifact(Contract):
    sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    size_bytes: int = Field(ge=0)
    name: str
    version: str
    architecture: str
    filename: str
    visibility: Visibility = 'restricted'


class PublicDTO(Contract):
    sha256: str
    size_bytes: int
    name: str
    version: str
    architecture: str
    filename: str


def public_projection(record: Artifact) -> PublicDTO | None:
    if record.visibility != 'public':
        return None
    return PublicDTO(**record.model_dump(exclude={'visibility'}))


class SourceConfig(Contract):
    id: str = Field(pattern=r'^[a-z0-9][a-z0-9-]{0,79}$')
    provider: str
    ecosystem: str
    base_url: str | None = None
    allowed_hosts: tuple[str, ...] = ()
    visibility: Visibility = 'restricted'
    routing_enabled: bool = False
    permission_state: Literal['unreviewed', 'approved', 'denied'] = 'unreviewed'
    domestic_state: Literal['unverified', 'provider_claimed', 'verified'] = 'unverified'
    approval_evidence: str | None = None
    failure_domain: str | None = None

    @model_validator(mode='after')
    def require_approval(self):
        if self.routing_enabled and (self.permission_state != 'approved' or self.domestic_state != 'verified' or not self.approval_evidence):
            raise ValueError('Routing needs separately recorded permission/domestic/evidence approval')
        return self


class ProbeBudget(Contract):
    concurrency: int = Field(default=4, ge=1, le=4)
    per_host: int = Field(default=1, ge=1, le=1)
    timeout_seconds: int = Field(default=10, ge=1, le=10)
    sample_bytes: int = Field(default=4096, ge=1, le=4096)
    requests_per_day: int = Field(default=1000, ge=0, le=1000)
    full_bytes_per_day: int = Field(default=1073741824, ge=0)


class ValidatedTarget(Contract):
    url: str
    hostname: str
    connected_ip: str
    port: int


class HttpObservation(Contract):
    checked_at: datetime
    status: int | None = None
    connected_ip: str | None = None
    tls_verified: bool | None = None
    body_bytes: int = 0
    error_code: str | None = None


class ProbeResult(Contract):
    source_id: str
    state: Literal['present_verified','present_unverified','absent','unknown','quarantined']
    checked_at: datetime
    full_hash_verified: bool = False
    observation: HttpObservation


class VerifiedRelease(Contract):
    suite: str
    inrelease_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    release_date: datetime
    valid_until: datetime | None = None


class MetadataBundle(Contract):
    id: str = Field(pattern=r'^[0-9a-f]{64}$')
    releases: tuple[VerifiedRelease, ...]
    staged_path: Path


class ImportStats(Contract):
    imported: int = Field(ge=0)
    rejected: int = Field(ge=0)


class GapDecision(Contract):
    state: Literal['missing_in_tested_set','unknown','fragile','available']
    eligible_source_ids: tuple[str, ...]
    untested_source_ids: tuple[str, ...]
    checked_at: datetime


class AccessContext(Contract):
    principal_id: str
    session_id: str
    expires_at: datetime
    scope: Literal['restricted']


class ObjectInfo(Contract):
    sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    size_bytes: int = Field(ge=0)
    visibility: Visibility


class LocalTarget(Contract):
    object_id: str
    visibility: Visibility


class RemoteTarget(Contract):
    source_id: str
    url: str
    visibility: Literal['public'] = 'public'


class StorageBackend(Protocol):
    def stat(self, sha256: str) -> ObjectInfo | None: ...
    def put_verified(self, file: Path, expected_sha256: str, expected_size: int) -> ObjectInfo: ...
    def download_target(self, sha256: str) -> LocalTarget | RemoteTarget: ...


class RouteDecision(Contract):
    action: Literal['local','redirect','unavailable','conflict']
    reason: str
    checked_at: datetime
    target: LocalTarget | RemoteTarget | None = None


class JobRunSummary(Contract):
    completed: int = Field(ge=0)
    failed: int = Field(ge=0)
    deferred: int = Field(ge=0)


class ReleaseManifest(Contract):
    contract_version: Literal['1.0'] = '1.0'
    schema_version: Literal[1] = 1
    commit: str = Field(pattern=r'^[0-9a-f]{40}$')
    architecture: Literal['amd64','arm64']
    base_path: Literal['/software'] = '/software'
    image_digests: tuple[str, ...] = Field(min_length=1)
    restricted_enabled: Literal[False] = False

    @model_validator(mode='after')
    def pinned_images(self):
        import re
        if any(not re.fullmatch(r'sha256:[0-9a-f]{64}', value) for value in self.image_digests):
            raise ValueError('Release images require exact sha256 digests')
        return self
