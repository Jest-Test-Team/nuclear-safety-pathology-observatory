from __future__ import annotations

import csv
import io
import os
import urllib.request
from typing import Iterable

from .base import Connector, ConnectorError, RawRecord


class TaiwanNUSCCSVConnector(Connector):
    """Generic CSV adapter for official Taiwan NUSC open-data exports.

    Field mappings are intentionally configurable because official datasets may
    publish different Chinese or English headers. The connector never guesses
    safety conclusions; it only retrieves public records with provenance.
    """

    def __init__(self, source_id: str, endpoint_env: str, timeout: int = 20) -> None:
        self.source_id = source_id
        self.url = os.getenv(endpoint_env, "").strip()
        self.timeout = timeout
        if not self.url:
            raise ConnectorError(f"missing endpoint environment variable: {endpoint_env}")

    def fetch(self) -> Iterable[RawRecord]:
        request = urllib.request.Request(self.url, headers={"User-Agent": "nspo-research/0.1"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec: configured official URL
            body = response.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(body))
        for index, row in enumerate(reader, start=1):
            yield RawRecord.from_payload(self.source_id, f"row-{index}", dict(row), self.url)
