from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable


class ConnectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class RawRecord:
    source_id: str
    source_record_id: str
    payload: dict[str, object]
    source_url: str
    retrieved_at: str
    content_hash: str

    @classmethod
    def from_payload(cls, source_id: str, source_record_id: str, payload: dict[str, object], source_url: str) -> "RawRecord":
        material = repr(sorted(payload.items())).encode("utf-8")
        return cls(
            source_id=source_id,
            source_record_id=source_record_id,
            payload=payload,
            source_url=source_url,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            content_hash=sha256(material).hexdigest(),
        )


class Connector(ABC):
    @abstractmethod
    def fetch(self) -> Iterable[RawRecord]:
        raise NotImplementedError
