from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_report_path = (
            repo_root / "reports" / "analysis" / "v134ep_commercial_aerospace_intraday_add_tiered_label_specification_v1.json"
        )

    def analyze(self) -> V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Report:
        spec = json.loads(self.spec_report_path.read_text(encoding="utf-8"))
        status = (
            "freeze_intraday_add_tiered_label_specification_and_shift_next_to_local_add_pattern_envelope_audit"
        )
        triage_rows = [
            {
                "component": "intraday_add_tiered_label_specification",
                "status": status,
                "rationale": (
                    "the intraday-add frontier now has a canonical supervision vocabulary and should next inspect local minute-shape envelopes "
                    "rather than jump directly to execution logic"
                ),
            },
            {
                "component": "reduce_mainline",
                "status": "retain_frozen",
                "rationale": "opening add as supervision does not reopen reduce or inherit reduce execution authority",
            },
            {
                "component": "intraday_add_execution_authority",
                "status": "still_blocked",
                "rationale": "tier vocabulary belongs to supervision and does not authorize add execution or replay binding",
            },
        ]
        interpretation = [
            "V1.34EQ freezes the first add-tier vocabulary as the canonical next step for the commercial-aerospace intraday-add frontier.",
            "The next task is local add pattern-envelope auditing under the new label tiers, not execution binding.",
        ]
        return V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134eq_commercial_aerospace_ep_add_label_direction_triage_v1",
                "authoritative_status": status,
                "registry_row_count": spec["summary"]["registry_row_count"],
                "label_tier_count": spec["summary"]["label_tier_count"],
                "authoritative_rule": (
                    "the commercial-aerospace intraday-add frontier should next inspect local minute pattern envelopes under the frozen add-tier vocabulary "
                    "while keeping execution authority blocked"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EQCommercialAerospaceEPAddLabelDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134eq_commercial_aerospace_ep_add_label_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
