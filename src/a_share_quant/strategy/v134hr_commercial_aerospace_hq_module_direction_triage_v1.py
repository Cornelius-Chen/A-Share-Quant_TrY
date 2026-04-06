from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1 import (
    V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134HRCommercialAerospaceHQModuleDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HRCommercialAerospaceHQModuleDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134HRCommercialAerospaceHQModuleDirectionTriageV1Report:
        audit = V134HQCommercialAerospaceBoardWeakSymbolStrongConcentrationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "module_name": "board_weak_symbol_strong_concentration",
                "direction": "retain_as_higher_level_negative_label_module_and_do_not_treat_symbol_concentration_as_board_unlock",
            },
            {
                "module_name": "outside_module_negative_labels",
                "direction": "keep_as_separate_subfamilies_not_every_negative_label_needs_symbol_strong_concentration",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v134hr_commercial_aerospace_hq_module_direction_triage_v1",
            "module_member_count": audit.summary["module_member_count"],
            "module_member_symbols": audit.summary["module_member_symbols"],
            "authoritative_status": "retain_board_weak_symbol_strong_concentration_as_higher_level_negative_label_module",
        }
        interpretation = [
            "V1.34HR converts the higher-level module into direction.",
            "The system should learn strong local concentration inside a weak board as its own negative-label module rather than as restart evidence.",
        ]
        return V134HRCommercialAerospaceHQModuleDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HRCommercialAerospaceHQModuleDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HRCommercialAerospaceHQModuleDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hr_commercial_aerospace_hq_module_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
