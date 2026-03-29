from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASELINE_FAMILIES = {
    "entry_suppression_avoidance",
    "earlier_exit_loss_reduction",
}

NON_BASELINE_FAMILIES = {
    "preemptive_loss_avoidance_shift",
    "carry_in_basis_advantage",
    "delayed_entry_basis_advantage",
}

TOXIC_FAMILIES = {
    "entry_suppression_opportunity_cost",
    "other_worse_loss_shift",
    "later_exit_loss_extension",
}


@dataclass(slots=True)
class SpecialistFeatureGapAuditReport:
    summary: dict[str, Any]
    pocket_rows: list[dict[str, Any]]
    grouped_rows: list[dict[str, Any]]
    feature_gap_suspects: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "pocket_rows": self.pocket_rows,
            "grouped_rows": self.grouped_rows,
            "feature_gap_suspects": self.feature_gap_suspects,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def classify_pocket(families: set[str], row_count: int) -> str:
    if row_count == 1 and families == {"entry_suppression_avoidance"}:
        return "single_row_baseline_reuse"
    if families & TOXIC_FAMILIES:
        if families & NON_BASELINE_FAMILIES and families & BASELINE_FAMILIES:
            return "stacked_family_pocket"
        return "mixed_existing_families"
    if families & NON_BASELINE_FAMILIES:
        if families & BASELINE_FAMILIES:
            return "stacked_family_pocket"
        return "clean_nonbaseline_asset"
    if families <= BASELINE_FAMILIES:
        return "baseline_family_reuse"
    return "unclassified"


class SpecialistFeatureGapAuditAnalyzer:
    """Audit whether the specialist replay loop is entering a feature-limited thinning phase."""

    def analyze(self, *, report_specs: list[dict[str, Any]]) -> SpecialistFeatureGapAuditReport:
        pocket_rows: list[dict[str, Any]] = []
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}

        for spec in report_specs:
            payload = load_json_report(Path(str(spec["report_path"])))
            mechanism_rows = list(payload.get("mechanism_rows", []))
            families = {str(row["mechanism_type"]) for row in mechanism_rows}
            classification = classify_pocket(families, len(mechanism_rows))
            pocket_row = {
                "report_name": str(spec["report_name"]),
                "dataset_name": str(spec["dataset_name"]),
                "slice_name": str(spec["slice_name"]),
                "strategy_name": str(spec["strategy_name"]),
                "symbol": str(spec["symbol"]),
                "row_count": len(mechanism_rows),
                "families": sorted(families),
                "classification": classification,
                "has_baseline_family": bool(families & BASELINE_FAMILIES),
                "has_nonbaseline_family": bool(families & NON_BASELINE_FAMILIES),
                "has_toxic_family": bool(families & TOXIC_FAMILIES),
            }
            pocket_rows.append(pocket_row)
            group_key = (
                str(spec["dataset_name"]),
                str(spec["slice_name"]),
                str(spec["symbol"]),
            )
            grouped.setdefault(group_key, []).append(pocket_row)

        grouped_rows: list[dict[str, Any]] = []
        feature_gap_suspects: list[dict[str, Any]] = []
        for (dataset_name, slice_name, symbol), rows in grouped.items():
            strategies = sorted({str(row["strategy_name"]) for row in rows})
            classifications = sorted({str(row["classification"]) for row in rows})
            combined_families = sorted({family for row in rows for family in row["families"]})
            cross_strategy = len(strategies) > 1
            grouped_row = {
                "dataset_name": dataset_name,
                "slice_name": slice_name,
                "symbol": symbol,
                "strategy_count": len(strategies),
                "strategies": strategies,
                "classifications": classifications,
                "families": combined_families,
                "cross_strategy": cross_strategy,
            }
            grouped_rows.append(grouped_row)

            likely_feature_limited = False
            reason = None
            if cross_strategy and classifications == ["mixed_existing_families"]:
                likely_feature_limited = True
                reason = "cross_strategy_mixed_repeat"
            elif "stacked_family_pocket" in classifications:
                likely_feature_limited = True
                reason = "stacked_known_families"

            if likely_feature_limited:
                feature_gap_suspects.append(
                    {
                        **grouped_row,
                        "reason": reason,
                    }
                )

        grouped_rows.sort(key=lambda item: (item["dataset_name"], item["slice_name"], item["symbol"]))
        feature_gap_suspects.sort(
            key=lambda item: (
                item["reason"],
                item["dataset_name"],
                item["slice_name"],
                item["symbol"],
            )
        )

        classification_counts: dict[str, int] = {}
        for row in pocket_rows:
            classification = str(row["classification"])
            classification_counts[classification] = classification_counts.get(classification, 0) + 1

        summary = {
            "pocket_count": len(pocket_rows),
            "group_count": len(grouped_rows),
            "feature_gap_suspect_count": len(feature_gap_suspects),
            "classification_counts": classification_counts,
            "thinning_signal": (
                classification_counts.get("single_row_baseline_reuse", 0)
                + classification_counts.get("baseline_family_reuse", 0)
                + classification_counts.get("mixed_existing_families", 0)
            )
            >= max(1, len(pocket_rows) - 2),
        }
        interpretation = [
            "A replay loop is likely thinning when most newly replayed pockets collapse into single-row baseline reuse, baseline-family reuse, or repeated mixed pockets.",
            "Cross-strategy mixed repeats and stacked-family pockets are plausible feature-gap suspects: the mechanism is recurring, but current features may be collapsing richer structure into known families.",
            "This audit does not prove that a new family exists. It only identifies where more expressive features may be worth trying before spending more replay budget.",
        ]
        return SpecialistFeatureGapAuditReport(
            summary=summary,
            pocket_rows=pocket_rows,
            grouped_rows=grouped_rows,
            feature_gap_suspects=feature_gap_suspects,
            interpretation=interpretation,
        )


def write_specialist_feature_gap_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SpecialistFeatureGapAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
