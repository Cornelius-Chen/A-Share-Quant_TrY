from __future__ import annotations

import csv
import json
import re
import urllib3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


_META_KEYS = (
    "article:published_time",
    "published_time",
    "publishdate",
    "publish_time",
    "pubdate",
    "datepublished",
    "apub:time",
    "article:create_at",
    "weibo: article:create_at",
    "release_date",
    "news_datetime",
    "og:time",
)

_DATE_PATTERNS = (
    r"(20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})",
    r"(20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2})",
    r"(20\d{2}/\d{2}/\d{2}[ T]\d{2}:\d{2}:\d{2})",
    r"(20\d{2}/\d{2}/\d{2}[ T]\d{2}:\d{2})",
    r"(20\d{2}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2}:\d{2})",
    r"(20\d{2}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2})",
)


def _candidate_expected_dates(source_name: str, url: str) -> list[str]:
    candidates: list[str] = []
    for text in (source_name, url):
        if not text:
            continue
        for year, month, day in re.findall(r"(20\d{2})[-/年](\d{1,2})[-/月](\d{1,2})", text):
            candidates.append(f"{int(year):04d}-{int(month):02d}-{int(day):02d}")
        for year, month, day in re.findall(r"(20\d{2})(\d{2})(\d{2})", text):
            candidates.append(f"{int(year):04d}-{int(month):02d}-{int(day):02d}")
    deduped: list[str] = []
    for item in candidates:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _normalize_timestamp(raw_value: str) -> str | None:
    value = raw_value.strip()
    if not value:
        return None
    value = value.replace("T", " ")
    value = value.replace("年", "-").replace("月", "-").replace("日", "")
    value = value.replace("/", "-")
    value = re.sub(r"\s+", " ", value)
    value = value.strip()

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return None


def extract_time_candidates_from_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[dict[str, str]] = []

    for meta in soup.find_all("meta"):
        attrs = {str(key).lower(): str(value) for key, value in meta.attrs.items()}
        joined = " ".join(attrs.values()).lower()
        if any(key in joined for key in _META_KEYS):
            content = attrs.get("content", "").strip()
            normalized = _normalize_timestamp(content)
            if normalized:
                candidates.append({"source": "meta", "raw_value": content, "normalized": normalized})

    text = " ".join(soup.stripped_strings)
    for pattern in _DATE_PATTERNS:
        for match in re.findall(pattern, html):
            normalized = _normalize_timestamp(match)
            if normalized:
                candidates.append({"source": "regex_html", "raw_value": match, "normalized": normalized})
        for match in re.findall(pattern, text):
            normalized = _normalize_timestamp(match)
            if normalized:
                candidates.append({"source": "regex_text", "raw_value": match, "normalized": normalized})

    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = candidate["normalized"]
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(candidate)
    return deduped


def _select_best_candidate(
    *,
    source_name: str,
    url: str,
    candidates: list[dict[str, str]],
) -> tuple[str | None, str, str]:
    expected_dates = _candidate_expected_dates(source_name, url)
    if not candidates:
        return None, "no_timestamp_candidate_found", "none"

    if expected_dates:
        for expected_date in expected_dates:
            for candidate in candidates:
                if candidate["normalized"].startswith(expected_date):
                    confidence = "matched_expected_date"
                    if candidate["source"] == "meta":
                        confidence = "matched_expected_date_meta"
                    return candidate["normalized"], confidence, candidate["source"]
        return None, "expected_date_not_matched", "none"

    first = candidates[0]
    confidence = "best_effort_first_candidate"
    if first["source"] == "meta":
        confidence = "best_effort_meta_candidate"
    return first["normalized"], confidence, first["source"]


def _fetch_html(url: str) -> tuple[str | None, str]:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, timeout=25, headers=headers)
        response.raise_for_status()
        return response.text, "ok"
    except requests.exceptions.SSLError:
        try:
            response = requests.get(url, timeout=25, headers=headers, verify=False)
            response.raise_for_status()
            return response.text, "ok_insecure_ssl"
        except Exception as exc:  # pragma: no cover - network dependent
            return None, f"{type(exc).__name__}:{exc}"
    except Exception as exc:  # pragma: no cover - network dependent
        return None, f"{type(exc).__name__}:{exc}"


@dataclass(slots=True)
class CpoCatalystEventRegistryBootstrapReport:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


class CpoCatalystEventRegistryBootstrapAnalyzer:
    """Bootstrap a bounded CPO catalyst/event registry with timestamp resolution where possible."""

    def analyze(
        self,
        *,
        information_registry_payload: dict[str, Any],
        future_calendar_payload: dict[str, Any],
    ) -> CpoCatalystEventRegistryBootstrapReport:
        registry_rows: list[dict[str, Any]] = []

        resolved_count = 0
        unresolved_count = 0
        source_timeout_count = 0
        source_ssl_retry_count = 0

        for index, row in enumerate(list(information_registry_payload.get("source_rows", [])), start=1):
            source_name = str(row.get("source_name", ""))
            layer = str(row.get("layer", ""))
            url = str(row.get("url", ""))
            html, fetch_status = _fetch_html(url)
            extracted_candidates: list[dict[str, str]] = []
            selected_timestamp: str | None = None
            resolution_confidence = "unresolved"
            resolution_source = "none"

            if html is not None:
                extracted_candidates = extract_time_candidates_from_html(html)
                selected_timestamp, resolution_confidence, resolution_source = _select_best_candidate(
                    source_name=source_name,
                    url=url,
                    candidates=extracted_candidates,
                )

            if fetch_status.startswith("ConnectTimeout"):
                source_timeout_count += 1
            if fetch_status == "ok_insecure_ssl":
                source_ssl_retry_count += 1

            if selected_timestamp is None:
                unresolved_count += 1
            else:
                resolved_count += 1

            registry_rows.append(
                {
                    "registry_id": f"cpo_source_{index:03d}",
                    "record_type": "historical_source",
                    "layer": layer,
                    "source_name": source_name,
                    "source_url": url,
                    "event_scope": "historical_observed_source",
                    "event_occurred_time": None,
                    "public_release_time": selected_timestamp,
                    "system_visible_time": selected_timestamp,
                    "timezone": "Asia/Shanghai",
                    "timestamp_resolution_status": "resolved" if selected_timestamp else "unresolved",
                    "timestamp_resolution_confidence": resolution_confidence,
                    "timestamp_resolution_source": resolution_source,
                    "fetch_status": fetch_status,
                    "extracted_candidate_count": len(extracted_candidates),
                    "expected_dates": _candidate_expected_dates(source_name, url),
                    "notes": "public web source bootstrap; unresolved rows require manual or alternate-source fill",
                }
            )

        for index, row in enumerate(list(future_calendar_payload.get("recurring_calendar_rows", [])), start=1):
            registry_rows.append(
                {
                    "registry_id": f"cpo_anchor_{index:03d}",
                    "record_type": "forward_anchor",
                    "layer": str(row.get("target_layer", "")),
                    "source_name": str(row.get("source_name", "")),
                    "source_url": "",
                    "event_scope": str(row.get("cadence_bucket", "")),
                    "event_occurred_time": None,
                    "public_release_time": None,
                    "system_visible_time": None,
                    "timezone": "Asia/Shanghai",
                    "timestamp_resolution_status": "forward_anchor_unresolved",
                    "timestamp_resolution_confidence": "calendar_only",
                    "timestamp_resolution_source": "v112w_future_calendar",
                    "fetch_status": "not_applicable",
                    "extracted_candidate_count": 0,
                    "expected_dates": [],
                    "notes": str(row.get("why_it_helps", "")),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v120c_cpo_catalyst_event_registry_bootstrap_v1",
            "historical_source_row_count": len(list(information_registry_payload.get("source_rows", []))),
            "forward_anchor_row_count": len(list(future_calendar_payload.get("recurring_calendar_rows", []))),
            "total_registry_row_count": len(registry_rows),
            "resolved_public_release_time_count": resolved_count,
            "unresolved_public_release_time_count": unresolved_count,
            "source_timeout_count": source_timeout_count,
            "source_ssl_retry_count": source_ssl_retry_count,
            "ready_for_second_level_manual_fill_next": True,
            "recommended_next_posture": "use_bootstrap_registry_as_bounded_event_base_and_fill_unresolved_rows_manually_or_with_higher_trust_sources",
        }
        interpretation = [
            "This bootstrap does not pretend all catalyst timestamps are known; it resolves what public web metadata can support and leaves the rest explicitly unresolved.",
            "Historical observed sources and forward anchors now live in one bounded registry so intraday legality work stops depending on vague daily source lists.",
            "The next catalyst step is not modeling; it is better timestamp resolution for unresolved rows and second-level system-visible time filling where feasible.",
        ]
        return CpoCatalystEventRegistryBootstrapReport(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_cpo_catalyst_event_registry_bootstrap_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CpoCatalystEventRegistryBootstrapReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_cpo_catalyst_event_registry_csv(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "registry_id",
        "record_type",
        "layer",
        "source_name",
        "source_url",
        "event_scope",
        "event_occurred_time",
        "public_release_time",
        "system_visible_time",
        "timezone",
        "timestamp_resolution_status",
        "timestamp_resolution_confidence",
        "timestamp_resolution_source",
        "fetch_status",
        "extracted_candidate_count",
        "expected_dates",
        "notes",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            serialized = dict(row)
            serialized["expected_dates"] = "|".join(str(item) for item in serialized.get("expected_dates", []))
            writer.writerow(serialized)
    return output_path
