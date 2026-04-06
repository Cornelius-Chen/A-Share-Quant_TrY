from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


SINA_7X24_URL = "https://finance.sina.com.cn/7x24/"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsSina7x24FetchV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class FetchAShareInternalHotNewsSina7x24V1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_dir = repo_root / "data" / "temp" / "info_center" / "ingest_staging"
        self.output_path = self.output_dir / "a_share_internal_hot_news_sina_7x24_staging_v1.csv"
        self.runtime_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_sina_probe_runtime_registry_v1.csv"
        )

    def _fetch_html(self) -> str:
        response = requests.get(
            SINA_7X24_URL,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding or "utf-8"
        return response.text

    @staticmethod
    def _extract_rows(html: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find("div", class_="seaio_list")
        if container is None:
            raise RuntimeError("sina 7x24 page missing seaio_list container")

        rows: list[dict[str, str]] = []
        for item in container.find_all("div", attrs={"newsdata-id": True}, recursive=False)[:80]:
            news_id = str(item.get("newsdata-id", "")).strip()
            news_date = str(item.get("newsdata-time", "")).strip()
            time_div = item.find("div")
            title_link = item.find("a", href=True)
            if not news_id or title_link is None or time_div is None:
                continue
            clock_text = time_div.get_text(strip=True)
            title = title_link.get_text(strip=True)
            href = title_link.get("href", "").strip()
            public_ts = ""
            if news_date and clock_text:
                public_ts = f"{news_date[:4]}-{news_date[4:6]}-{news_date[6:8]} {clock_text}"
            rows.append(
                {
                    "telegraph_id": f"sina_{news_id}",
                    "title": title,
                    "brief": title,
                    "content": title,
                    "author": "",
                    "subject_names": "",
                    "stock_count": "0",
                    "share_url": href,
                    "public_ts": public_ts,
                }
            )
        return rows

    def materialize(self) -> MaterializedAShareInternalHotNewsSina7x24FetchV1:
        html = self._fetch_html()
        rows = self._extract_rows(html)
        fetch_ts_utc = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S")

        materialized_rows = [
            {
                **row,
                "fetch_ts_utc": fetch_ts_utc,
                "source_name": "新浪财经7x24",
                "source_url": SINA_7X24_URL,
                "source_mode": "internal_only_probe",
            }
            for row in rows
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

        runtime_rows = [
            {
                "runtime_id": "internal_hot_news_sina_7x24_probe",
                "runtime_state": "internal_only_probe_active",
                "source_name": "新浪财经7x24",
                "source_url": SINA_7X24_URL,
                "fetch_mode": "page_dom_snapshot_parse",
                "pipeline_state": "probe_ready",
                "execution_gate": "research_shadow_only",
                "notes": "second-source probe kept outside the primary fastlane until theme-hit lift is proven",
            }
        ]
        self.runtime_registry_path.parent.mkdir(parents=True, exist_ok=True)
        with self.runtime_registry_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(runtime_rows[0].keys()))
            writer.writeheader()
            writer.writerows(runtime_rows)

        summary = {
            "fetch_row_count": len(materialized_rows),
            "runtime_state": "internal_only_probe_active",
            "output_path": str(self.output_path.relative_to(self.repo_root)),
            "runtime_registry_path": str(self.runtime_registry_path.relative_to(self.repo_root)),
        }
        return MaterializedAShareInternalHotNewsSina7x24FetchV1(summary=summary, rows=materialized_rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = FetchAShareInternalHotNewsSina7x24V1(repo_root).materialize()
    print(result.summary["output_path"])


if __name__ == "__main__":
    main()
