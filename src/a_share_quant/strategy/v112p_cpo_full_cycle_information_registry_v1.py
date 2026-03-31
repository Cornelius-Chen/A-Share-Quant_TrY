from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PCPOFullCycleInformationRegistryReport:
    summary: dict[str, Any]
    information_layers: list[dict[str, Any]]
    cohort_rows: list[dict[str, Any]]
    source_rows: list[dict[str, Any]]
    remaining_gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "information_layers": self.information_layers,
            "cohort_rows": self.cohort_rows,
            "source_rows": self.source_rows,
            "remaining_gap_rows": self.remaining_gap_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112PCPOFullCycleInformationRegistryAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        study_scope_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
    ) -> V112PCPOFullCycleInformationRegistryReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112p_now")):
            raise ValueError("V1.12P must be open before registry freeze.")

        validated_symbols = {
            str(row.get("symbol", ""))
            for row in list(pilot_dataset_payload.get("dataset_rows", []))
        }
        adjacent_symbols = {
            str(row.get("symbol_or_name", ""))
            for row in list(study_scope_payload.get("candidate_rows", []))
            if row.get("study_tier") == "review_only_adjacent_candidate"
        }

        information_layers = [
            {"layer_name": "news_and_catalyst", "focus": ["AI capex", "NVIDIA/Broadcom/CPO roadmap", "theme-level board catalysts"]},
            {"layer_name": "earnings_and_performance", "focus": ["revenue and profit acceleration", "guidance and forecast", "quarterly momentum change"]},
            {"layer_name": "technology_and_industry_chain", "focus": ["optical modules", "optical chips", "MPO/connectors", "optical fiber and cable", "CPO adjacency"]},
            {"layer_name": "price_and_technical_cycle", "focus": ["cycle windows", "major markup", "high-level consolidation", "pullback and rebound"]},
            {"layer_name": "index_liquidity_and_sentiment", "focus": ["risk appetite", "board breadth", "turnover", "concept-strength days"]},
            {"layer_name": "spillover_and_mixed_relevance", "focus": ["story spillover", "name bonus", "board-follow rows", "mixed business relevance"]},
        ]

        cohort_rows = [
            {"symbol": "300308", "display_name": "中际旭创", "cohort_tier": "validated_core_leader", "chain_role": "core_module_leader"},
            {"symbol": "300502", "display_name": "新易盛", "cohort_tier": "validated_core_leader", "chain_role": "high_beta_core_module"},
            {"symbol": "300394", "display_name": "天孚通信", "cohort_tier": "validated_core_leader", "chain_role": "upstream_component_platform"},
            {"symbol": "002281", "display_name": "光迅科技", "cohort_tier": "direct_related_review_only", "chain_role": "domestic_optics_platform"},
            {"symbol": "603083", "display_name": "剑桥科技", "cohort_tier": "direct_related_review_only", "chain_role": "high_beta_module_extension"},
            {"symbol": "688205", "display_name": "德科立", "cohort_tier": "direct_related_review_only", "chain_role": "high_end_module_extension"},
            {"symbol": "301205", "display_name": "联特科技", "cohort_tier": "direct_related_review_only", "chain_role": "smaller_cap_high_beta_module"},
            {"symbol": "300620", "display_name": "光库科技", "cohort_tier": "direct_related_review_only", "chain_role": "upstream_photonics_cpo_adjacent"},
            {"symbol": "300548", "display_name": "博创科技", "cohort_tier": "direct_related_review_only", "chain_role": "module_and_cpo_adjacency"},
            {"symbol": "000988", "display_name": "华工科技", "cohort_tier": "direct_related_review_only", "chain_role": "optoelectronic_vertical_platform"},
            {"symbol": "300570", "display_name": "太辰光", "cohort_tier": "extension_concept_review_only", "chain_role": "mpo_and_optical_connector"},
            {"symbol": "688498", "display_name": "源杰科技", "cohort_tier": "extension_concept_review_only", "chain_role": "optical_chip_and_laser"},
            {"symbol": "688313", "display_name": "仕佳光子", "cohort_tier": "extension_concept_review_only", "chain_role": "silicon_photonics_and_chip_adjacency"},
            {"symbol": "300757", "display_name": "罗博特科", "cohort_tier": "extension_concept_review_only", "chain_role": "equipment_and_cpo_process_adjacency"},
            {"symbol": "601869", "display_name": "长飞光纤", "cohort_tier": "chain_extension_review_only", "chain_role": "optical_fiber_and_cable"},
            {"symbol": "600487", "display_name": "亨通光电", "cohort_tier": "chain_extension_review_only", "chain_role": "optical_fiber_and_cable"},
            {"symbol": "600522", "display_name": "中天科技", "cohort_tier": "chain_extension_review_only", "chain_role": "optical_fiber_and_cable"},
            {"symbol": "000070", "display_name": "特发信息", "cohort_tier": "mixed_relevance_spillover_review_only", "chain_role": "story_spillover_or_board_follow"},
            {"symbol": "603228", "display_name": "景旺电子", "cohort_tier": "mixed_relevance_spillover_review_only", "chain_role": "board_follow_with_unclear_core_link"},
            {"symbol": "001267", "display_name": "汇绿生态", "cohort_tier": "mixed_relevance_spillover_review_only", "chain_role": "board_follow_with_unclear_core_link"},
        ]
        for row in cohort_rows:
            symbol = row["symbol"]
            if symbol in validated_symbols:
                row["validation_status"] = "validated_local_seed"
            elif symbol in adjacent_symbols:
                row["validation_status"] = "review_only_adjacent_candidate"
            else:
                row["validation_status"] = "review_only_pending_validation"

        source_rows = [
            {"source_name": "中际旭创2024年报核心数据解读", "layer": "earnings_and_performance", "url": "https://www.senn.com.cn/Item/207447.aspx"},
            {"source_name": "新易盛2024年报/2025Q1点评", "layer": "earnings_and_performance", "url": "https://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/lastest/rptid/798851138700/index.phtml"},
            {"source_name": "天孚通信互动平台/CPO产品进展", "layer": "earnings_and_performance", "url": "https://www.yicai.com/news/102780055.html"},
            {"source_name": "光迅科技2024年报点评", "layer": "earnings_and_performance", "url": "https://data.eastmoney.com/report/info/AP202504301664920555.html"},
            {"source_name": "中国金融信息网 2023-12-08 CPO板块强势", "layer": "index_liquidity_and_sentiment", "url": "https://www.cnfin.com/yw-lb/detail/20231208/3978903_1.html"},
            {"source_name": "新浪 2023-09-22 CPO方向领涨", "layer": "price_and_technical_cycle", "url": "https://finance.sina.cn/2023-09-22/detail-imznqakm2690339.d.html"},
            {"source_name": "证券时报 2024-09-25 CPO概念爆发", "layer": "news_and_catalyst", "url": "https://stcn.com/article/detail/1703076.html"},
            {"source_name": "光纤在线 2025-03-19 英伟达GTC CPO交换机", "layer": "technology_and_industry_chain", "url": "https://www.c-fol.net/news/7_202503/20250319124734.html"},
            {"source_name": "Forbes China 2025-07 CPO板块与新易盛业绩预告", "layer": "news_and_catalyst", "url": "https://www.forbeschina.com/insights/70130"},
            {"source_name": "搜狐/数据宝 CPO概念资金与成份股", "layer": "index_liquidity_and_sentiment", "url": "https://www.sohu.com/a/917184533_115433"},
        ]

        remaining_gap_rows = [
            {"gap_name": "daily_concept_index_turnover_series", "priority": "high", "why_missing": "board-strength snapshots exist but not a full daily turnover history"},
            {"gap_name": "official_report_links_for_all_adjacent_names", "priority": "high", "why_missing": "core trio and some direct names have anchors, but not the entire adjacent cohort"},
            {"gap_name": "future_visible_catalyst_calendar", "priority": "medium", "why_missing": "future-event and industry-calendar fields are not yet normalized"},
            {"gap_name": "mixed_relevance_spillover_truth_check", "priority": "medium", "why_missing": "story-follow rows are included intentionally but still need bounded validation"},
        ]

        summary = {
            "acceptance_posture": "freeze_v112p_cpo_full_cycle_information_registry_v1",
            "information_layer_count": len(information_layers),
            "cohort_row_count": len(cohort_rows),
            "validated_core_count": sum(1 for row in cohort_rows if row["cohort_tier"] == "validated_core_leader"),
            "review_only_related_count": sum(1 for row in cohort_rows if row["cohort_tier"] != "validated_core_leader"),
            "source_count": len(source_rows),
            "remaining_gap_count": len(remaining_gap_rows),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "This first-pass registry values omission control over purity: some noisy rows are intentionally preserved in review-only form.",
            "The registry separates validated training anchors from direct-related, extension, and mixed-relevance names so later cohort validation can stay disciplined.",
            "The next discussion should focus on what is still missing and which candidate tiers deserve bounded validation first.",
        ]
        return V112PCPOFullCycleInformationRegistryReport(
            summary=summary,
            information_layers=information_layers,
            cohort_rows=cohort_rows,
            source_rows=source_rows,
            remaining_gap_rows=remaining_gap_rows,
            interpretation=interpretation,
        )


def write_v112p_cpo_full_cycle_information_registry_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PCPOFullCycleInformationRegistryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
