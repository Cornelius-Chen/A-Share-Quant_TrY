from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _classify_decisive_semantic(row: dict[str, str]) -> tuple[str, str, bool]:
    layer = row["layer"]
    record_type = row["record_type"]
    text = f"{row['source_name']} {row['notes']}"

    if record_type == "forward_anchor":
        if row["event_scope"] == "policy_scope":
            return "termination_or_regulation_risk", "regulatory_or_financing_constraint_anchor", True
        if row["event_scope"] == "launch_or_deployment":
            return "continuation_enabler", "launch_or_deployment_anchor", True
        if row["event_scope"] == "capital_mapping":
            return "continuation_enabler", "capital_mapping_anchor", True
        if row["event_scope"] == "sentiment_transition":
            return "turning_point_watch", "sentiment_transition_anchor", True

    if any(keyword in text for keyword in ["跳水", "监管", "限制", "核查", "问询", "过热", "退潮", "熄火"]):
        if any(keyword in text for keyword in ["监管", "限制", "融资", "核查", "问询"]):
            return "termination_or_regulation_risk", "decisive_regulation_or_financing_risk", True
        return "turning_point_watch", "decisive_turning_point_risk", True

    if layer == "theme_heat":
        return "discarded_theme_heat", "non_decisive_theme_heat_excluded", False

    if layer == "policy_or_industry_event":
        return "continuation_enabler", "policy_or_industry_progress", True

    if layer == "industry_progress":
        return "continuation_enabler", "industry_progress", True

    if layer == "supply_chain_validation":
        return "continuation_enabler", "supply_chain_validation", True

    if layer == "general_theme_context":
        if any(keyword in text for keyword in ["深耕", "核心", "持续发力", "稳定供应", "相关性强"]):
            return "continuation_enabler", "general_context_but_industry_specific", True
        return "discarded_general_context", "non_decisive_general_context_excluded", False

    if layer == "capital_mapping":
        if any(keyword in text for keyword in ["收购", "参股", "持有", "股权", "资本连接", "并购", "映射"]):
            return "continuation_enabler", "capital_mapping_with_real_board_implication", True
        return "discarded_capital_mapping", "weak_capital_mapping_excluded", False

    return "discarded_misc", "unclassified_non_decisive", False


@dataclass(slots=True)
class V125MCommercialAerospaceDecisiveEventProtocolReport:
    summary: dict[str, Any]
    decisive_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "decisive_rows": self.decisive_rows,
            "interpretation": self.interpretation,
        }


class V125MCommercialAerospaceDecisiveEventProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_catalyst_event_registry_v1.csv"
        )

    def analyze(self) -> V125MCommercialAerospaceDecisiveEventProtocolReport:
        rows = _load_csv(self.registry_path)
        decisive_rows: list[dict[str, Any]] = []
        retained_historical = 0
        discarded_historical = 0
        continuation_count = 0
        turning_point_count = 0
        termination_count = 0

        for row in rows:
            decisive_semantic, decisive_reason, decisive_retained = _classify_decisive_semantic(row)
            enriched = {
                **row,
                "decisive_semantic": decisive_semantic,
                "decisive_reason": decisive_reason,
                "decisive_retained": decisive_retained,
            }
            decisive_rows.append(enriched)

            if row["record_type"] == "historical_source":
                if decisive_retained:
                    retained_historical += 1
                else:
                    discarded_historical += 1
            if decisive_retained:
                if decisive_semantic == "continuation_enabler":
                    continuation_count += 1
                elif decisive_semantic == "turning_point_watch":
                    turning_point_count += 1
                elif decisive_semantic == "termination_or_regulation_risk":
                    termination_count += 1

        summary = {
            "acceptance_posture": "freeze_v125m_commercial_aerospace_decisive_event_protocol_v1",
            "historical_source_count": sum(1 for row in rows if row["record_type"] == "historical_source"),
            "retained_historical_count": retained_historical,
            "discarded_historical_count": discarded_historical,
            "retained_total_count": sum(1 for row in decisive_rows if row["decisive_retained"]),
            "continuation_enabler_count": continuation_count,
            "turning_point_watch_count": turning_point_count,
            "termination_or_regulation_risk_count": termination_count,
            "authoritative_rule": "commercial_aerospace_event_learning_keeps_only_decisive_continuation_turning_point_and_regulation_financing_risk_events",
            "recommended_next_posture": "rebuild_event_conditioned_control_surface_using_only_decisive_event_rows",
        }
        interpretation = [
            "V1.25M narrows the commercial-aerospace event layer from broad theme-news collection into a decisive-event protocol.",
            "Only three classes remain lawful for the next control rebuild: continuation enablers, turning-point watches, and regulation/financing termination risks.",
            "Generic theme-heat news is now explicitly excluded from control semantics.",
        ]
        return V125MCommercialAerospaceDecisiveEventProtocolReport(
            summary=summary,
            decisive_rows=decisive_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125MCommercialAerospaceDecisiveEventProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def write_csv_file(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125MCommercialAerospaceDecisiveEventProtocolAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125m_commercial_aerospace_decisive_event_protocol_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root
        / "data"
        / "reference"
        / "catalyst_registry"
        / "commercial_aerospace_decisive_event_registry_v1.csv",
        rows=result.decisive_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
