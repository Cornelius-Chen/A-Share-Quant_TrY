from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_beneficiary_role_normalizer import (
    normalize_beneficiary_role,
)


THEME_ALIAS_MAP = {
    "commercial_aerospace": ("商业航天", "航天", "卫星", "火箭"),
    "defense_industry": ("军工", "导弹", "无人机"),
    "oil_gas": ("油气", "石油", "天然气", "原油"),
    "gold": ("黄金", "贵金属"),
    "ai": ("人工智能", "AI", "算力", "大模型"),
    "semiconductor": ("半导体", "芯片"),
    "lithium_battery": ("锂电", "锂矿", "动力电池", "电池", "固态电池"),
    "brokerage": ("券商", "证券", "投行"),
    "bank": ("银行", "降准", "降息", "信贷"),
    "nuclear_power": ("核电", "核能"),
    "rare_earth": ("稀土",),
    "coal": ("煤炭", "煤价"),
    "optical_communication": ("光模块", "CPO", "光通信", "高速互联"),
    "telecom": ("通信", "运营商", "6G", "5G"),
    "robotics": ("机器人", "自动化", "工业机器人", "智能制造"),
    "consumer_electronics": ("消费电子", "果链", "手机链", "可穿戴"),
    "pharmaceutical": ("医药", "创新药", "医疗", "生物医药"),
    "new_energy_vehicle": ("新能源车", "智能驾驶", "汽车", "车企"),
    "shipping": ("航运", "海运", "集运", "船舶"),
    "nonferrous_metals": ("有色", "有色金属", "铜", "铝", "钴", "钼"),
    "medicine_devices": ("医疗器械", "器械", "IVD", "医疗设备"),
    "innovative_drug": ("创新药", "新药", "生物药", "CXO"),
    "liquor": ("白酒", "酒类", "名酒"),
    "power_equipment": ("电力设备", "储能", "逆变器", "光伏设备", "电网设备"),
    "consumer_staples": ("消费", "内需", "必选消费"),
    "home_appliances": ("家电", "白电", "空调", "冰洗"),
    "pv_solar": ("光伏", "硅料", "组件", "逆变器"),
    "energy_storage": ("储能", "储能系统", "电化学储能"),
    "military_electronics": ("军工电子", "军用电子", "军民融合"),
    "chemical_materials": ("化工材料", "新材料", "材料"),
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _latest_concept_surface(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return []
    latest_trade_date = max(row["trade_date"] for row in rows)
    return [row for row in rows if row["trade_date"] == latest_trade_date]


def _theme_beneficiary_map(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["theme_slug"], []).append(row)
    return grouped


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _match_concepts(theme_slug: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    aliases = THEME_ALIAS_MAP.get(theme_slug, ())
    if not aliases:
        return []
    return [row for row in rows if any(alias in row["concept_name"] for alias in aliases)]


def _rank_symbols(concept_rows: list[dict[str, str]]) -> list[str]:
    ranked = sorted(
        concept_rows,
        key=lambda row: (
            0 if str(row["is_primary_concept"]).lower() == "true" else 1,
            -_to_float(row["weight"]),
            row["symbol"],
        ),
    )
    deduped: list[str] = []
    for row in ranked:
        symbol = row["symbol"]
        if symbol not in deduped:
            deduped.append(symbol)
    return deduped


def _curated_match(theme_slug: str, theme_beneficiary_map: dict[str, list[dict[str, str]]]) -> tuple[list[str], str]:
    curated_rows = theme_beneficiary_map.get(theme_slug, [])
    if not curated_rows:
        return [], "none", "unmapped", ""
    symbols = [row["symbol"] for row in curated_rows]
    confidence_order = {"high": 3, "medium": 2, "low": 1}
    confidence = max(
        (row.get("mapping_confidence", "medium") for row in curated_rows),
        key=lambda value: confidence_order.get(value, 0),
    )
    top_row = max(
        curated_rows,
        key=lambda row: (
            confidence_order.get(row.get("mapping_confidence", "medium"), 0),
            1 if row.get("beneficiary_role", "").startswith("direct_") else 0,
        ),
    )
    role = top_row.get("beneficiary_role", "")
    _, linkage_class = normalize_beneficiary_role(
        beneficiary_role=role,
        mapping_confidence=confidence,
    )
    return symbols, confidence, linkage_class, role


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsSignalEnrichmentV1:
    summary: dict[str, Any]
    board_signal_rows: list[dict[str, Any]]
    important_queue_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsSignalEnrichmentV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.concept_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_concept_membership_v1.csv"
        )
        self.theme_beneficiary_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_beneficiary_registry_v1.csv"
        )
        self.board_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_board_signal_surface_v1.csv"
        )
        self.important_queue_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_important_trading_queue_v1.csv"
        )
        self.enriched_board_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_board_signal_enriched_v1.csv"
        )
        self.enriched_important_queue_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_important_trading_queue_enriched_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        fieldnames = list(materialized_rows[0].keys())
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(materialized_rows)

    @staticmethod
    def _annotate_row(
        row: dict[str, str],
        concept_rows: list[dict[str, str]],
        theme_beneficiary_map: dict[str, list[dict[str, str]]],
    ) -> dict[str, Any]:
        theme_slug = row.get("target_theme_slug", "broad_market")
        if theme_slug == "broad_market":
            return {
                **row,
                "board_hit_state": "broad_market_only",
                "beneficiary_mapping_confidence": "none",
                "beneficiary_linkage_class": "none",
                "beneficiary_role_top": "",
                "beneficiary_symbol_count": "0",
                "beneficiary_symbols_top5": "",
            }

        curated_symbols, curated_confidence, curated_linkage_class, curated_role = _curated_match(
            theme_slug, theme_beneficiary_map
        )
        if curated_symbols:
            return {
                **row,
                "board_hit_state": "theme_detected_and_curated_beneficiary_matched",
                "beneficiary_mapping_confidence": curated_confidence,
                "beneficiary_linkage_class": curated_linkage_class,
                "beneficiary_role_top": curated_role,
                "beneficiary_symbol_count": str(len(curated_symbols)),
                "beneficiary_symbols_top5": "|".join(curated_symbols[:5]),
            }

        matched = _match_concepts(theme_slug, concept_rows)
        ranked_symbols = _rank_symbols(matched)
        if not ranked_symbols:
            return {
                **row,
                "board_hit_state": "theme_detected_but_member_surface_missing",
                "beneficiary_mapping_confidence": "low",
                "beneficiary_linkage_class": "unmapped",
                "beneficiary_role_top": "",
                "beneficiary_symbol_count": "0",
                "beneficiary_symbols_top5": "",
            }

        confidence = "high" if len(ranked_symbols) >= 5 else "medium"
        return {
            **row,
            "board_hit_state": "theme_detected_and_member_surface_matched",
            "beneficiary_mapping_confidence": confidence,
            "beneficiary_linkage_class": "proxy_beneficiary",
            "beneficiary_role_top": "member_surface_proxy",
            "beneficiary_symbol_count": str(len(ranked_symbols)),
            "beneficiary_symbols_top5": "|".join(ranked_symbols[:5]),
        }

    def materialize(self) -> MaterializedAShareInternalHotNewsSignalEnrichmentV1:
        concept_rows = _latest_concept_surface(_read_csv(self.concept_path))
        theme_beneficiary_rows = _read_csv(self.theme_beneficiary_registry_path)
        theme_beneficiary_map = _theme_beneficiary_map(theme_beneficiary_rows)
        board_signal_rows = _read_csv(self.board_signal_path)
        important_queue_rows = _read_csv(self.important_queue_path)

        enriched_board_signal_rows = [
            self._annotate_row(row, concept_rows, theme_beneficiary_map) for row in board_signal_rows
        ]
        enriched_important_queue_rows = [
            self._annotate_row(row, concept_rows, theme_beneficiary_map) for row in important_queue_rows
        ]

        self._write_csv(self.enriched_board_signal_path, enriched_board_signal_rows)
        self._write_csv(self.enriched_important_queue_path, enriched_important_queue_rows)

        all_rows = enriched_board_signal_rows + enriched_important_queue_rows
        summary = {
            "board_signal_row_count": len(enriched_board_signal_rows),
            "important_queue_row_count": len(enriched_important_queue_rows),
            "curated_match_count": sum(
                row["board_hit_state"] == "theme_detected_and_curated_beneficiary_matched"
                for row in all_rows
            ),
            "matched_board_signal_count": sum(
                row["board_hit_state"] == "theme_detected_and_member_surface_matched"
                for row in enriched_board_signal_rows
            ),
            "matched_important_queue_count": sum(
                row["board_hit_state"] == "theme_detected_and_member_surface_matched"
                for row in enriched_important_queue_rows
            ),
            "missing_surface_count": sum(
                row["board_hit_state"] == "theme_detected_but_member_surface_missing" for row in all_rows
            ),
            "authoritative_output": "a_share_internal_hot_news_signal_enrichment_materialized",
        }
        return MaterializedAShareInternalHotNewsSignalEnrichmentV1(
            summary=summary,
            board_signal_rows=enriched_board_signal_rows,
            important_queue_rows=enriched_important_queue_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsSignalEnrichmentV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
