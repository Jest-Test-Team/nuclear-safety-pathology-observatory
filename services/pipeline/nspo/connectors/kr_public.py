from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Iterable

from .base import Connector, ConnectorError, RawRecord


def _timeout_seconds() -> int:
    return int(os.getenv("NSPO_HTTP_TIMEOUT_SECONDS", "20"))


def _rate_limit_seconds() -> float:
    return float(os.getenv("NSPO_RATE_LIMIT_SECONDS", "1"))


def _user_agent() -> str:
    return os.getenv("NSPO_USER_AGENT", "nspo-research/0.1")


def _redact_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    for key in list(query):
        if key.lower() in {"servicekey", "service_key", "apikey", "api_key"}:
            query[key] = ["REDACTED"]
    redacted = parsed._replace(query=urllib.parse.urlencode(query, doseq=True))
    return urllib.parse.urlunparse(redacted)


class KoreaPublicAPIConnector(Connector):
    """Quota-aware REST adapter for data.go.kr / KHNP / KORAD public endpoints."""

    def __init__(
        self,
        source_id: str,
        endpoint_env: str,
        service_key_env: str = "NSPO_KOREA_SERVICE_KEY",
        timeout: int | None = None,
        rate_limit_seconds: float | None = None,
    ) -> None:
        self.source_id = source_id
        self.base_url = os.getenv(endpoint_env, "").strip()
        self.service_key = os.getenv(service_key_env, "").strip()
        self.timeout = timeout if timeout is not None else _timeout_seconds()
        self.rate_limit_seconds = rate_limit_seconds if rate_limit_seconds is not None else _rate_limit_seconds()
        self._credential_env = service_key_env
        if not self.base_url:
            raise ConnectorError(f"missing endpoint environment variable: {endpoint_env}")
        if not self.service_key:
            raise ConnectorError(f"missing service key environment variable: {service_key_env}")

    def fetch(self) -> Iterable[RawRecord]:
        separator = "&" if "?" in self.base_url else "?"
        url = f"{self.base_url}{separator}{urllib.parse.urlencode({'serviceKey': self.service_key})}"
        request = urllib.request.Request(url, headers={"User-Agent": _user_agent()})
        time.sleep(max(0.0, self.rate_limit_seconds))
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec: configured official URL
                body = response.read()
                content_type = response.headers.get("Content-Type", "")
        except urllib.error.URLError as exc:
            raise ConnectorError(f"korea public fetch failed for {self.source_id}: {exc}") from exc

        safe_url = _redact_url(url)
        payloads = self._parse_body(body, content_type)
        for index, payload in enumerate(payloads, start=1):
            record_id = str(
                payload.get("id")
                or payload.get("stationId")
                or payload.get("measDt")
                or payload.get("resultCode")
                or f"item-{index}"
            )
            if "resultCode" in payload or "resultMsg" in payload:
                payload = {
                    **payload,
                    "_official_result_code": payload.get("resultCode", ""),
                    "_official_result_msg": payload.get("resultMsg", ""),
                }
            yield RawRecord.from_payload(self.source_id, record_id, payload, safe_url)

    def _parse_body(self, body: bytes, content_type: str) -> list[dict[str, object]]:
        text = body.decode("utf-8-sig", errors="replace").strip()
        if not text:
            return []
        lowered = content_type.lower()
        if "json" in lowered or text[:1] in {"{", "["}:
            return self._parse_json(text)
        return self._parse_xml(text)

    def _parse_json(self, text: str) -> list[dict[str, object]]:
        data = json.loads(text)
        if isinstance(data, list):
            return [dict(item) for item in data if isinstance(item, dict)]
        if not isinstance(data, dict):
            raise ConnectorError(f"unsupported JSON payload for {self.source_id}")
        # Common data.go.kr envelope shapes.
        for path in (
            ("response", "body", "items", "item"),
            ("response", "body", "items"),
            ("body", "items", "item"),
            ("items", "item"),
            ("data",),
        ):
            cursor: object = data
            for key in path:
                if not isinstance(cursor, dict) or key not in cursor:
                    cursor = None
                    break
                cursor = cursor[key]
            if cursor is None:
                continue
            if isinstance(cursor, list):
                return [dict(item) for item in cursor if isinstance(item, dict)]
            if isinstance(cursor, dict):
                return [dict(cursor)]
        # Preserve top-level result metadata as a single record when items are absent.
        return [dict(data)]

    def _parse_xml(self, text: str) -> list[dict[str, object]]:
        root = ET.fromstring(text)
        items = root.findall(".//item")
        records: list[dict[str, object]] = []
        header = root.find(".//header")
        result_code = header.findtext("resultCode") if header is not None else root.findtext(".//resultCode")
        result_msg = header.findtext("resultMsg") if header is not None else root.findtext(".//resultMsg")
        for index, item in enumerate(items, start=1):
            payload = {child.tag: (child.text or "") for child in list(item)}
            if result_code is not None:
                payload["resultCode"] = result_code
            if result_msg is not None:
                payload["resultMsg"] = result_msg
            if not payload:
                payload = {"item": str(index)}
            records.append(payload)
        if records:
            return records
        payload = {child.tag: (child.text or "") for child in list(root)}
        if result_code is not None:
            payload["resultCode"] = result_code
        if result_msg is not None:
            payload["resultMsg"] = result_msg
        return [payload] if payload else []


# Backward-compatible alias used by older imports.
KoreaPublicXMLConnector = KoreaPublicAPIConnector
