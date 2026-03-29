from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class ConceptToLateBridgeAnalysisReport:
    summary: dict[str, Any]
    bridge_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "bridge_rows": self.bridge_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Config at {path} must decode to a mapping.")
    return payload


class ConceptToLateBridgeAnalyzer:
    """Quantify how much concept support would need to bridge a late-mover threshold gap."""

    def analyze(
        self,
        *,
        recheck_report_path: Path,
        case_name: str,
        timeline_config_path: Path,
        derived_config_path: Path,
    ) -> ConceptToLateBridgeAnalysisReport:
        recheck_payload = load_json_report(recheck_report_path)
        timeline_config = load_yaml(timeline_config_path)
        derived_config = load_yaml(derived_config_path)

        challenger_name = str(timeline_config["comparison"]["challenger_candidate"])
        challenger = next(
            item for item in timeline_config["candidates"] if str(item["candidate_name"]) == challenger_name
        )
        late_threshold = float(challenger["override"]["trend"]["hierarchy"]["min_quality_for_late_mover"])
        rules = dict(derived_config.get("rules", {}))
        current_boost = float(rules.get("concept_support_late_quality_boost", 0.0))
        band_lower = float(rules.get("concept_support_band_lower", 0.0))
        band_upper = float(rules.get("concept_support_band_upper", 1.0))
        cap_enabled = bool(rules.get("concept_support_cap_to_band_upper", False))

        rows = [
            row
            for row in recheck_payload.get("case_rows", [])
            if str(row["case_name"]) == case_name and bool(row.get("late_quality_straddle"))
        ]
        bridge_rows = []
        for row in rows:
            late_quality = float(row.get("late_mover_quality", 0.0))
            concept_support = float(row.get("concept_support", 0.0))
            required_uplift = round(max(0.0, late_threshold - late_quality), 6)
            implied_boost_coef = round(required_uplift / concept_support, 6) if concept_support > 0 else None
            within_current_band = band_lower <= late_quality < band_upper
            blocked_by_cap = bool(cap_enabled and band_upper < late_threshold)
            requires_band_extension = late_quality >= band_upper or late_quality < band_lower
            bridge_rows.append(
                {
                    "trigger_date": str(row["trigger_date"]),
                    "mechanism_type": str(row["mechanism_type"]),
                    "late_mover_quality": late_quality,
                    "concept_support": concept_support,
                    "primary_concept_weight": float(row.get("primary_concept_weight", 0.0)),
                    "concept_concentration_ratio": float(row.get("concept_concentration_ratio", 0.0)),
                    "late_threshold": late_threshold,
                    "required_uplift": required_uplift,
                    "implied_boost_coef": implied_boost_coef,
                    "within_current_band": within_current_band,
                    "requires_band_extension": requires_band_extension,
                    "blocked_by_cap": blocked_by_cap,
                }
            )

        implied_values = [row["implied_boost_coef"] for row in bridge_rows if row["implied_boost_coef"] is not None]
        summary = {
            "case_name": case_name,
            "row_count": len(bridge_rows),
            "current_boost": current_boost,
            "current_band_lower": band_lower,
            "current_band_upper": band_upper,
            "cap_enabled": cap_enabled,
            "max_required_boost_coef": round(max(implied_values), 6) if implied_values else None,
            "min_required_boost_coef": round(min(implied_values), 6) if implied_values else None,
            "rows_needing_band_extension": sum(bool(row["requires_band_extension"]) for row in bridge_rows),
            "rows_blocked_by_cap": sum(bool(row["blocked_by_cap"]) for row in bridge_rows),
            "recommended_variant": {
                "concept_support_late_quality_boost": 0.10,
                "concept_support_band_lower": 0.58,
                "concept_support_band_upper": 0.65,
                "concept_support_cap_to_band_upper": False,
            },
        }
        interpretation = [
            "The key quantity is not just whether concept support exists, but how much late-quality uplift is required to cross the challenger threshold.",
            "If the needed rows already sit above the current band upper, the next refinement must widen the band instead of only increasing the boost coefficient.",
            "If a narrow variant can target only the late-mover band rows, it is preferable to a broad concept boost across the full distribution.",
        ]
        return ConceptToLateBridgeAnalysisReport(
            summary=summary,
            bridge_rows=bridge_rows,
            interpretation=interpretation,
        )


def write_concept_to_late_bridge_analysis_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ConceptToLateBridgeAnalysisReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
