from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.lane_path = (
            repo_root / "reports" / "analysis" / "v134cb_commercial_aerospace_isolated_sell_side_shadow_lane_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_cb_isolated_lane_direction_triage_v1.csv"
        )

    def analyze(self) -> V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Report:
        lane = json.loads(self.lane_path.read_text(encoding="utf-8"))

        triage_rows = [
            {
                "component": "isolated_sell_side_shadow_lane",
                "status": "retained_shadow_binding_surface",
                "detail": "Keep the lane as the first holdings-aware sell-side binding surface; it now consumes only carried start-of-day inventory.",
            },
            {
                "component": "same_day_reconciliation",
                "status": "explicit_and_mandatory",
                "detail": "Preserve reconciliation rows and clipping behavior so later EOD reduce/close actions cannot double-consume carried inventory.",
            },
            {
                "component": "next_real_work",
                "status": "stop_lane_expansion_and_audit_binding_quality",
                "detail": "Do not widen scope yet; next justified work is attribution and quality audit of this isolated lane, not replay binding.",
            },
            {
                "component": "scope_guardrail",
                "status": "mandatory",
                "detail": "Keep the branch sell-side only and continue excluding reentry execution and full replay binding.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134cc_commercial_aerospace_cb_isolated_lane_direction_triage_v1",
            "authoritative_status": "retain_isolated_sell_side_shadow_lane_and_audit_binding_quality_next",
            "executed_session_count": lane["summary"]["executed_session_count"],
            "clipped_reconciliation_count": lane["summary"]["clipped_reconciliation_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CC converts the first isolated sell-side lane into a practical direction judgment.",
            "The lane should be retained as the first holdings-aware binding surface, but the next step is quality audit rather than replay expansion.",
        ]
        return V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CCCommercialAerospaceCBIsolatedLaneDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cc_commercial_aerospace_cb_isolated_lane_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
