import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from .models import Contract, Mode


class Settings(Contract):
    data_dir: Path
    base_path: str = Field(default='/software', pattern=r'^/[a-z][a-z0-9-]*$')
    mode: Mode = 'DOMESTIC_ONLY'
    restricted_enabled: Literal[False] = False
    rubika_enabled: Literal[False] = False

    @property
    def database(self) -> Path:
        return self.data_dir / 'catalog.sqlite'

    @classmethod
    def from_env(cls):
        return cls(data_dir=Path(os.environ.get('TEHNET_SOFTWARE_DATA','./data')),
                   base_path=os.environ.get('TEHNET_SOFTWARE_PREFIX','/software'))
