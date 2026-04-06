from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup


CLS_TELEGRAPH_URL = "https://www.cls.cn/telegraph"


def _to_shanghai_ts(epoch_seconds: int) -> str:
    return (
        datetime.fromtimestamp(epoch_seconds, tz=UTC)
        .astimezone(ZoneInfo("Asia/Shanghai"))
        .strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsCLSTelegraphFetchV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class FetchAShareInternalHotNewsCLSTelegraphV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_dir = repo_root / "data" / "temp" / "info_center" / "ingest_staging"
        self.output_path = self.output_dir / "a_share_internal_hot_news_cls_telegraph_staging_v1.csv"
        self.runtime_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_registry_v1.csv"
        )

    def _fetch_payload(self) -> list[dict[str, Any]]:
        response = requests.get(
            CLS_TELEGRAPH_URL,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        if next_data_script is None:
            raise RuntimeError("cls telegraph page missing __NEXT_DATA__ payload")
        payload = json.loads(next_data_script.string or "{}")
        return payload["props"]["initialState"]["telegraph"]["telegraphList"]

    def materialize(self) -> MaterializedAShareInternalHotNewsCLSTelegraphFetchV1:
        telegraph_rows = self._fetch_payload()
        fetch_ts_utc = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S")

        rows: list[dict[str, Any]] = []
        for item in telegraph_rows[:80]:
            ctime = int(item.get("ctime") or 0)
            rows.append(
                {
                    "telegraph_id": str(item.get("id", "")),
                    "title": str(item.get("title", "")).strip(),
                    "brief": str(item.get("brief", "")).strip(),
                    "content": str(item.get("content", "")).strip(),
                    "author": str(item.get("author", "")).strip(),
                    "subject_names": "|".join(
                        str(subject.get("subject_name", "")).strip()
                        for subject in item.get("subjects", [])
                        if str(subject.get("subject_name", "")).strip()
                    ),
                    "stock_count": str(len(item.get("stock_list", []) or [])),
                    "share_url": str(item.get("shareurl", "")).strip(),
                    "public_ts": _to_shanghai_ts(ctime) if ctime else "",
                    "fetch_ts_utc": fetch_ts_utc,
                    "source_name": "财联社电报",
                    "source_url": CLS_TELEGRAPH_URL,
                    "source_mode": "internal_only_fastlane",
                }
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        runtime_rows = [
            {
                "runtime_id": "internal_hot_news_cls_telegraph_fastlane",
                "runtime_state": "internal_only_active",
                "source_name": "财联社电报",
                "source_url": CLS_TELEGRAPH_URL,
                "fetch_mode": "cls_next_data_snapshot_parse",
                "pipeline_state": "fastlane_ready",
                "retention_state": "hot_5d_ttl_plus_important_promotion",
                "execution_gate": "research_shadow_only",
                "notes": "single-source fast lane to minimize duplicate news fan-out before broader source expansion",
            }
        ]
        self.runtime_registry_path.parent.mkdir(parents=True, exist_ok=True)
        with self.runtime_registry_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(runtime_rows[0].keys()))
            writer.writeheader()
            writer.writerows(runtime_rows)

        summary = {
            "fetch_row_count": len(rows),
            "source_name": "财联社电报",
            "runtime_state": "internal_only_active",
            "output_path": str(self.output_path.relative_to(self.repo_root)),
            "runtime_registry_path": str(self.runtime_registry_path.relative_to(self.repo_root)),
        }
        return MaterializedAShareInternalHotNewsCLSTelegraphFetchV1(summary=summary, rows=rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = FetchAShareInternalHotNewsCLSTelegraphV1(repo_root).materialize()
    print(result.summary["output_path"])


if __name__ == "__main__":
    main()
