from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v114u_intraday_event_timestamp_discipline_protocol_v1 import (
    V114UIntradayEventTimestampDisciplineProtocolAnalyzer,
)
from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import (
    _candidate_expected_dates,
    _fetch_html,
    _select_best_candidate,
    extract_time_candidates_from_html,
)
from a_share_quant.strategy.v124l_commercial_aerospace_web_concept_universe_review_v1 import (
    V124LCommercialAerospaceWebConceptUniverseReviewAnalyzer,
)


def _classify_source_layer(source_name: str, value: str) -> str:
    text = f"{source_name} {value}"
    if any(key in text for key in ("收购", "参股", "股权", "持有", "资本映射", "创投")):
        return "capital_mapping"
    if any(key in text for key in ("线缆", "卖铲", "材料", "芯片", "检测", "验证", "供应", "配套")):
        return "supply_chain_validation"
    if any(key in text for key in ("爆发", "涨停", "热点", "盘面", "概念", "主力")):
        return "theme_heat"
    if any(key in text for key in ("政策", "监管", "工信", "发改", "空天", "发射", "星座")):
        return "policy_or_industry_event"
    return "general_theme_context"


def _forward_anchor_rows() -> list[dict[str, Any]]:
    return [
        {
            "registry_id": "ca_anchor_001",
            "record_type": "forward_anchor",
            "layer": "policy_or_industry_event",
            "source_name": "商业航天政策/监管发布",
            "source_url": "",
            "event_scope": "policy_scope",
            "event_occurred_time": None,
            "public_release_time": None,
            "system_visible_time": None,
            "timezone": "Asia/Shanghai",
            "timestamp_resolution_status": "forward_anchor_unresolved",
            "timestamp_resolution_confidence": "calendar_only",
            "timestamp_resolution_source": "manual_anchor",
            "fetch_status": "not_applicable",
            "extracted_candidate_count": 0,
            "expected_dates": [],
            "notes": "政策/监管变化会直接改变商业航天题材可做性与热度上限。",
        },
        {
            "registry_id": "ca_anchor_002",
            "record_type": "forward_anchor",
            "layer": "industry_progress",
            "source_name": "火箭发射/卫星组网进展",
            "source_url": "",
            "event_scope": "launch_or_deployment",
            "event_occurred_time": None,
            "public_release_time": None,
            "system_visible_time": None,
            "timezone": "Asia/Shanghai",
            "timestamp_resolution_status": "forward_anchor_unresolved",
            "timestamp_resolution_confidence": "calendar_only",
            "timestamp_resolution_source": "manual_anchor",
            "fetch_status": "not_applicable",
            "extracted_candidate_count": 0,
            "expected_dates": [],
            "notes": "发射、入轨、组网进展是商业航天题材的一级驱动。",
        },
        {
            "registry_id": "ca_anchor_003",
            "record_type": "forward_anchor",
            "layer": "capital_mapping",
            "source_name": "股权/并购/融资映射变化",
            "source_url": "",
            "event_scope": "capital_mapping",
            "event_occurred_time": None,
            "public_release_time": None,
            "system_visible_time": None,
            "timezone": "Asia/Shanghai",
            "timestamp_resolution_status": "forward_anchor_unresolved",
            "timestamp_resolution_confidence": "calendar_only",
            "timestamp_resolution_source": "manual_anchor",
            "fetch_status": "not_applicable",
            "extracted_candidate_count": 0,
            "expected_dates": [],
            "notes": "A股商业航天题材存在明显跨板块资本映射扩散，需要单独追踪。",
        },
        {
            "registry_id": "ca_anchor_004",
            "record_type": "forward_anchor",
            "layer": "theme_heat",
            "source_name": "板块情绪扩散/镜像龙头切换",
            "source_url": "",
            "event_scope": "sentiment_transition",
            "event_occurred_time": None,
            "public_release_time": None,
            "system_visible_time": None,
            "timezone": "Asia/Shanghai",
            "timestamp_resolution_status": "forward_anchor_unresolved",
            "timestamp_resolution_confidence": "calendar_only",
            "timestamp_resolution_source": "manual_anchor",
            "fetch_status": "not_applicable",
            "extracted_candidate_count": 0,
            "expected_dates": [],
            "notes": "名字股、情绪股、镜像股轮动会改变 breadth 和 risk-off 语义。",
        },
    ]


@dataclass(slots=True)
class V125HCommercialAerospaceCatalystEventRegistryBootstrapReport:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


class V125HCommercialAerospaceCatalystEventRegistryBootstrapAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, skip_fetch: bool = False) -> V125HCommercialAerospaceCatalystEventRegistryBootstrapReport:
        universe_review = V124LCommercialAerospaceWebConceptUniverseReviewAnalyzer().analyze()
        _ = V114UIntradayEventTimestampDisciplineProtocolAnalyzer(repo_root=self.repo_root).analyze()

        registry_rows: list[dict[str, Any]] = []
        resolved_count = 0
        unresolved_count = 0
        for idx, row in enumerate(universe_review.source_rows, start=1):
            source_name = str(row["source_name"])
            source_url = str(row["url"])
            value = str(row["value"])
            layer = _classify_source_layer(source_name, value)

            fetch_status = "skipped"
            extracted_candidates: list[dict[str, str]] = []
            selected_timestamp: str | None = None
            resolution_confidence = "unresolved_skip_fetch"
            resolution_source = "none"
            if not skip_fetch:
                html, fetch_status = _fetch_html(source_url)
                if html is not None:
                    extracted_candidates = extract_time_candidates_from_html(html)
                    selected_timestamp, resolution_confidence, resolution_source = _select_best_candidate(
                        source_name=source_name,
                        url=source_url,
                        candidates=extracted_candidates,
                    )

            if selected_timestamp is None:
                unresolved_count += 1
                resolution_status = "unresolved"
            else:
                resolved_count += 1
                resolution_status = "resolved"

            registry_rows.append(
                {
                    "registry_id": f"ca_source_{idx:03d}",
                    "record_type": "historical_source",
                    "layer": layer,
                    "source_name": source_name,
                    "source_url": source_url,
                    "event_scope": layer,
                    "event_occurred_time": None,
                    "public_release_time": selected_timestamp,
                    "system_visible_time": selected_timestamp,
                    "timezone": "Asia/Shanghai",
                    "timestamp_resolution_status": resolution_status,
                    "timestamp_resolution_confidence": resolution_confidence,
                    "timestamp_resolution_source": resolution_source,
                    "fetch_status": fetch_status,
                    "extracted_candidate_count": len(extracted_candidates),
                    "expected_dates": _candidate_expected_dates(source_name, source_url),
                    "notes": value,
                }
            )

        registry_rows.extend(_forward_anchor_rows())
        summary = {
            "acceptance_posture": "freeze_v125h_commercial_aerospace_catalyst_event_registry_bootstrap_v1",
            "historical_source_row_count": len(universe_review.source_rows),
            "forward_anchor_row_count": 4,
            "total_registry_row_count": len(registry_rows),
            "resolved_public_release_time_count": resolved_count,
            "unresolved_public_release_time_count": unresolved_count,
            "skip_fetch": skip_fetch,
            "authoritative_rule": "commercial_aerospace_event_learning_must_follow_second_level_system_visible_time_discipline_before_any_intraday_binding",
            "recommended_next_posture": "fill_unresolved_rows_and_use_this_registry_as_the_bounded_information_event_base_before_replay",
        }
        interpretation = [
            "V1.25H opens the commercial-aerospace information layer as a bounded catalyst/event registry rather than a vague theme-news pile.",
            "The registry preserves layer distinctions such as capital mapping, supply-chain validation, theme heat, and policy/industry events.",
            "This is still pre-modeling work: unresolved timestamps must be improved before any point-in-time replay binding.",
        ]
        return V125HCommercialAerospaceCatalystEventRegistryBootstrapReport(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125HCommercialAerospaceCatalystEventRegistryBootstrapReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def write_csv_file(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
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
            serialized["expected_dates"] = "|".join(serialized["expected_dates"])
            writer.writerow(serialized)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125HCommercialAerospaceCatalystEventRegistryBootstrapAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125h_commercial_aerospace_catalyst_event_registry_bootstrap_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root
        / "data"
        / "reference"
        / "catalyst_registry"
        / "commercial_aerospace_catalyst_event_registry_v1.csv",
        rows=result.registry_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
