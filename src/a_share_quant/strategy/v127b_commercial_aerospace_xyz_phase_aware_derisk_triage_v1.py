from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127BCommercialAerospaceXYZPhaseAwareDeriskTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V127BCommercialAerospaceXYZPhaseAwareDeriskTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v126y_path = repo_root / "reports" / "analysis" / "v126y_commercial_aerospace_shadow_stack_compare_v1.json"
        self.v127a_path = repo_root / "reports" / "analysis" / "v127a_commercial_aerospace_phase_aware_derisk_audit_v1.json"

    def analyze(self) -> V127BCommercialAerospaceXYZPhaseAwareDeriskTriageReport:
        compare = json.loads(self.v126y_path.read_text(encoding="utf-8"))
        rows = {row["variant"]: row for row in compare["stack_rows"]}
        v126o = rows["v126o_economic_reference"]
        v126q = rows["v126q_cleaner_reference"]
        v126v = rows["v126v_retained_aggressive_shadow"]
        v127a = json.loads(self.v127a_path.read_text(encoding="utf-8"))
        best_variant = next(
            row for row in v127a["variant_rows"] if row["variant"] == v127a["summary"]["best_variant"]
        )

        replaces_aggressive = (
            best_variant["final_equity"] >= v126v["final_equity"]
            and best_variant["max_drawdown"] <= v126v["max_drawdown"]
        )
        promotable = (
            best_variant["final_equity"] >= v126o["final_equity"]
            and best_variant["max_drawdown"] <= v126o["max_drawdown"]
            and best_variant["max_drawdown"] <= v126q["max_drawdown"]
        )

        summary = {
            "acceptance_posture": "freeze_v127b_commercial_aerospace_xyz_phase_aware_derisk_triage_v1",
            "economic_reference_variant": v126o["variant"],
            "cleaner_reference_variant": v126q["variant"],
            "retired_aggressive_shadow_variant": v126v["variant"],
            "new_aggressive_shadow_variant": best_variant["variant"] if replaces_aggressive else v126v["variant"],
            "new_aggressive_shadow_final_equity": best_variant["final_equity"] if replaces_aggressive else v126v["final_equity"],
            "new_aggressive_shadow_max_drawdown": best_variant["max_drawdown"] if replaces_aggressive else v126v["max_drawdown"],
            "replaces_old_aggressive_shadow": replaces_aggressive,
            "promotable_to_reference_frontier": promotable,
            "authoritative_status": "replace_aggressive_shadow_and_continue_phase_aware_downside_grammar",
        }
        interpretation = [
            "V1.27B freezes the commercial-aerospace shadow stack after phase-aware de-risking: V1.26O remains the economic reference, V1.26Q the cleaner reference, and V1.27A replaces V1.26V inside the aggressive slot.",
            "This is still not a promotion to the reference frontier; the remaining optimization layer is narrower downside execution grammar, not further entry amplification.",
        ]
        return V127BCommercialAerospaceXYZPhaseAwareDeriskTriageReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V127BCommercialAerospaceXYZPhaseAwareDeriskTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127BCommercialAerospaceXYZPhaseAwareDeriskTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127b_commercial_aerospace_xyz_phase_aware_derisk_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
