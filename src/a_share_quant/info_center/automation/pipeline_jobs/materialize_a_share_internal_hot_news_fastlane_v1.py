from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IMPORTANT_KEYWORDS = (
    "国务院",
    "国常会",
    "证监会",
    "中国人民银行",
    "央行",
    "财政部",
    "发改委",
    "工信部",
    "商务部",
    "国资委",
    "上交所",
    "深交所",
    "金融监管总局",
    "国家统计局",
    "海关总署",
)

MARKET_MOVING_KEYWORDS = (
    "A股",
    "沪深",
    "公告",
    "停牌",
    "复牌",
    "回购",
    "增持",
    "减持",
    "收购",
    "并购",
    "重组",
    "涨停",
    "跌停",
    "发射",
    "卫星",
    "火箭",
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _classify_row(row: dict[str, str]) -> tuple[str, str]:
    text = f"{row['title']} {row['brief']} {row['content']}"
    if any(keyword in text for keyword in IMPORTANT_KEYWORDS):
        return "important_policy_or_regulatory", "promote_to_important_layer"
    if int(row["stock_count"] or 0) > 0 or any(keyword in text for keyword in MARKET_MOVING_KEYWORDS):
        return "market_moving_candidate", "promote_to_important_layer"
    return "generic_fast_news", "hot_layer_ttl_5d"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsFastlaneV1:
    summary: dict[str, Any]
    fastlane_rows: list[dict[str, Any]]
    important_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsFastlaneV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.staging_path = (
            repo_root
            / "data"
            / "temp"
            / "info_center"
            / "ingest_staging"
            / "a_share_internal_hot_news_cls_telegraph_staging_v1.csv"
        )
        self.fastlane_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_fastlane_surface_v1.csv"
        )
        self.important_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "event_registry"
            / "a_share_internal_hot_news_important_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsFastlaneV1:
        staging_rows = _read_csv(self.staging_path)

        fastlane_rows: list[dict[str, Any]] = []
        important_rows: list[dict[str, Any]] = []
        for row in staging_rows:
            signal_class, promotion_target = _classify_row(row)
            fastlane_row = {
                "telegraph_id": row["telegraph_id"],
                "public_ts": row["public_ts"],
                "fetch_ts_utc": row["fetch_ts_utc"],
                "title": row["title"],
                "brief": row["brief"],
                "author": row["author"],
                "subject_names": row["subject_names"],
                "stock_count": row["stock_count"],
                "signal_class": signal_class,
                "promotion_target": promotion_target,
                "delivery_state": "pipeline_ready_for_trading_program",
                "source_name": row["source_name"],
                "source_url": row["source_url"],
            }
            fastlane_rows.append(fastlane_row)
            if promotion_target == "promote_to_important_layer":
                important_rows.append(
                    {
                        "important_event_id": f"cls_fastlane_{row['telegraph_id']}",
                        "telegraph_id": row["telegraph_id"],
                        "public_ts": row["public_ts"],
                        "title": row["title"],
                        "brief": row["brief"],
                        "signal_class": signal_class,
                        "important_reason": (
                            "policy_or_regulatory"
                            if signal_class == "important_policy_or_regulatory"
                            else "market_moving_candidate"
                        ),
                        "source_name": row["source_name"],
                        "source_url": row["source_url"],
                    }
                )

        self.fastlane_path.parent.mkdir(parents=True, exist_ok=True)
        with self.fastlane_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fastlane_rows[0].keys()))
            writer.writeheader()
            writer.writerows(fastlane_rows)

        self.important_path.parent.mkdir(parents=True, exist_ok=True)
        safe_important_rows = important_rows or [
            {
                "important_event_id": "",
                "telegraph_id": "",
                "public_ts": "",
                "title": "",
                "brief": "",
                "signal_class": "",
                "important_reason": "",
                "source_name": "",
                "source_url": "",
            }
        ]
        with self.important_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(safe_important_rows[0].keys()))
            writer.writeheader()
            writer.writerows(safe_important_rows)

        summary = {
            "fastlane_row_count": len(fastlane_rows),
            "important_row_count": len(important_rows),
            "fastlane_path": str(self.fastlane_path.relative_to(self.repo_root)),
            "important_path": str(self.important_path.relative_to(self.repo_root)),
        }
        return MaterializedAShareInternalHotNewsFastlaneV1(
            summary=summary,
            fastlane_rows=fastlane_rows,
            important_rows=important_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsFastlaneV1(repo_root).materialize()
    print(result.summary["fastlane_path"])


if __name__ == "__main__":
    main()
