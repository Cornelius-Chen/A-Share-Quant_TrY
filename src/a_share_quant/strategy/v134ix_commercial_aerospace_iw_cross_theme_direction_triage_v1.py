from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134iw_commercial_aerospace_000738_cross_theme_contamination_audit_v1 import (
    V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Report:
        audit = V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "000738",
                "direction": "downshift_from_clean_second_carrier_watch_to_cross_theme_contaminated_watch",
            },
            {
                "component": "gas_turbine_comparator_pair",
                "direction": "retain_as_valid_hypothesis_but_do_not_force_same_plane conclusions_without_wider_local_coverage",
            },
            {
                "component": "capital_true_selection",
                "direction": "continue_blocked_and_do_not_use_000738_as_clean_commercial_aerospace_peer_evidence",
            },
            {
                "component": "future_labeling_extension",
                "direction": "add_concept_purity_and_basic_business_reference_layer_before_cross_theme_names_enter_board_specific_carrier_evidence",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134ix_commercial_aerospace_iw_cross_theme_direction_triage_v1",
            "theme_purity_label": audit.summary["theme_purity_label"],
            "future_labeling_extension": audit.summary["future_labeling_extension"],
            "authoritative_status": "retain_000738_as_cross_theme_contaminated_watch_and_keep_true_selection_blocked",
        }
        interpretation = [
            "V1.34IX converts the contamination audit into direction.",
            "The key move is to protect the commercial-aerospace training stack from cross-theme leakage while acknowledging the gas-turbine hypothesis as legitimate but not yet same-plane-proven.",
        ]
        return V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ix_commercial_aerospace_iw_cross_theme_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
