from __future__ import annotations

import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Iterable

from .base import Connector, ConnectorError, RawRecord


class KoreaPublicXMLConnector(Connector):
    """Minimal REST/XML adapter for data.go.kr or KORAD public endpoints."""

    def __init__(self, source_id: str, endpoint_env: str, service_key_env: str = "NSPO_KOREA_SERVICE_KEY", timeout: int = 20) -> None:
        self.source_id = source_id
        self.base_url = os.getenv(endpoint_env, "").strip()
        self.service_key = os.getenv(service_key_env, "").strip()
        self.timeout = timeout
        if not self.base_url:
            raise ConnectorError(f"missing endpoint environment variable: {endpoint_env}")
        if not self.service_key:
            raise ConnectorError(f"missing service key environment variable: {service_key_env}")

    def fetch(self) -> Iterable[RawRecord]:
        separator = "&" if "?" in self.base_url else "?"
        url = f"{self.base_url}{separator}{urllib.parse.urlencode({'serviceKey': self.service_key})}"
        request = urllib.request.Request(url, headers={"User-Agent": "nspo-research/0.1"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec: configured official URL
            body = response.read()
        root = ET.fromstring(body)
        items = root.findall(".//item")
        for index, item in enumerate(items, start=1):
            payload = {child.tag: (child.text or "") for child in list(item)}
            record_id = str(payload.get("id") or payload.get("stationId") or f"item-{index}")
            yield RawRecord.from_payload(self.source_id, record_id, payload, self.base_url)
