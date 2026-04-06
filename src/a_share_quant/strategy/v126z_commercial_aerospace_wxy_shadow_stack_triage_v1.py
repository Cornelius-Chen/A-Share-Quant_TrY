from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V126ZCommercialAerospaceWXYShadowStackTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V126ZCommercialAerospaceWXYShadowStackTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.compare_path = repo_root / "reports" / "analysis" / "v126y_commercial_aerospace_shadow_stack_compare_v1.json"

    def analyze(self) -> V126ZCommercialAerospaceWXYShadowStackTriageReport:
        compare = json.loads(self.compare_path.read_text(encoding="utf-8"))
        rows = {row["variant"]: row for row in compare["stack_rows"]}
        v126o = rows["v126o_economic_reference"]
        v126q = rows["v126q_cleaner_reference"]
        v126v = rows["v126v_retained_aggressive_shadow"]
        v126x = rows["v126x_weakest_half_full_exit"]

        summary = {
            "acceptance_posture": "freeze_v126z_commercial_aerospace_wxy_shadow_stack_triage_v1",
            "economic_reference_variant": v126o["variant"],
            "economic_reference_final_equity": v126o["final_equity"],
            "economic_reference_max_drawdown": v126o["max_drawdown"],
            "cleaner_reference_variant": v126q["variant"],
            "cleaner_reference_final_equity": v126q["final_equity"],
            "cleaner_reference_max_drawdown": v126q["max_drawdown"],
            "retained_aggressive_shadow_variant": v126v["variant"],
            "retained_aggressive_shadow_final_equity": v126v["final_equity"],
            "retained_aggressive_shadow_max_drawdown": v126v["max_drawdown"],
            "detached_derisk_shadow_variant": v126x["variant"],
            "detached_derisk_shadow_final_equity": v126x["final_equity"],
            "detached_derisk_shadow_max_drawdown": v126x["max_drawdown"],
            "authoritative_status": "freeze_reference_stack_and_shift_to_narrow_downside_execution",
        }
        interpretation = [
            "V1.26Z freezes the current commercial-aerospace lawful shadow stack after comparing economic reference, cleaner reference, aggressive preheat shadow, and the best conditional de-risk variant.",
            "The stack is retained for reference only: V1.26O remains the economic anchor, V1.26Q the cleaner comparator, V1.26V the aggressive preheat shadow, and V1.26X only a detached de-risk shadow.",
            "No current variant is promoted; the next optimization layer is narrow downside execution grammar rather than more preheat expansion or replay-surface tuning.",
        ]
        return V126ZCommercialAerospaceWXYShadowStackTriageReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126ZCommercialAerospaceWXYShadowStackTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126ZCommercialAerospaceWXYShadowStackTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126z_commercial_aerospace_wxy_shadow_stack_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
