import os
from pathlib import Path
from typing import Literal

from pydantic import Field,model_validator
from .models import Contract, Mode


class Settings(Contract):
    data_dir: Path
    base_path: str = Field(default='/software', pattern=r'^/[a-z][a-z0-9-]*$')
    mode: Mode = 'DOMESTIC_ONLY'
    restricted_enabled: bool = False
    auth_dir: Path | None = None
    metadata_dir: Path | None = None
    operation_dir: Path | None = None
    public_origin: str = 'https://tehnet.ir'
    rubika_enabled: Literal[False] = False

    @model_validator(mode='after')
    def access_configuration(self):
        from urllib.parse import urlsplit
        parsed=urlsplit(self.public_origin)
        if parsed.scheme!='https' or not parsed.hostname or parsed.netloc!=parsed.hostname or parsed.path or parsed.query or parsed.fragment:
            raise ValueError('Canonical HTTPS origin without credentials/port/path required')
        if self.restricted_enabled and (self.auth_dir is None or self.metadata_dir is None):
            raise ValueError('Private mode requires separate auth and external-metadata roots')
        roots=[x.absolute() for x in [self.data_dir,self.auth_dir,self.metadata_dir,self.operation_dir] if x is not None]
        if any(a==b or a in b.parents or b in a.parents for i,a in enumerate(roots) for b in roots[i+1:]):
            raise ValueError('State roots must be separate, non-nested directories')
        return self

    @property
    def database(self) -> Path:
        return self.data_dir / 'catalog.sqlite'

    @classmethod
    def from_env(cls):
        flag=os.environ.get('TEHNET_SOFTWARE_RESTRICTED','0')
        if flag not in ['0','1']:raise ValueError('Restricted flag must be 0 or 1')
        return cls(data_dir=Path(os.environ.get('TEHNET_SOFTWARE_DATA','./data')),
                   base_path=os.environ.get('TEHNET_SOFTWARE_PREFIX','/software'),
                   restricted_enabled=flag=='1',
                   auth_dir=Path(os.environ['TEHNET_SOFTWARE_AUTH']) if os.environ.get('TEHNET_SOFTWARE_AUTH') else None,
                   metadata_dir=Path(os.environ['TEHNET_SOFTWARE_METADATA']) if os.environ.get('TEHNET_SOFTWARE_METADATA') else None,
                   operation_dir=Path(os.environ['TEHNET_SOFTWARE_OPS']) if os.environ.get('TEHNET_SOFTWARE_OPS') else None,
                   public_origin=os.environ.get('TEHNET_SOFTWARE_ORIGIN','https://tehnet.ir'))
