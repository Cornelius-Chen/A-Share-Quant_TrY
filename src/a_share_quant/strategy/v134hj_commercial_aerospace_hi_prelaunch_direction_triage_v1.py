from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.card_path = (
            repo_root / "reports" / "analysis" / "v134hi_commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1.json"
        )

    def analyze(self) -> V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Report:
        card = json.loads(self.card_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "prelaunch_status_card",
                "status": "retain",
                "rationale": "the boundary-extension option now has a compact status card and does not need more speculative governance artifacts",
            },
            {
                "component": "frontier_opening_now",
                "status": "blocked",
                "rationale": "the current authoritative state remains deferred_prelaunch with ready_to_open_now = False",
            },
            {
                "component": "silent_opening",
                "status": "forbidden",
                "rationale": "existing raw coverage still does not authorize silent extension",
            },
        ]
        interpretation = [
            "V1.34HJ converts the prelaunch card into a simple governance verdict.",
            "The option is now well-formed enough to stop; any further move would need an explicit frontier shift rather than more preparation.",
        ]
        return V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134hj_commercial_aerospace_hi_prelaunch_direction_triage_v1",
                "authoritative_status": (
                    "freeze_shadow_boundary_extension_prelaunch_card_and_keep_frontier_deferred_until_explicit_shift"
                ),
                "frontier_name": card["summary"]["frontier_name"],
                "frontier_state": card["summary"]["frontier_state"],
                "opening_gate_count": card["summary"]["opening_gate_count"],
                "ready_to_open_now": card["summary"]["ready_to_open_now"],
                "silent_opening_allowed": card["summary"]["silent_opening_allowed"],
                "authoritative_rule": (
                    "the shadow-boundary-extension option may be prepared but not opened while its state remains deferred_prelaunch"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hj_commercial_aerospace_hi_prelaunch_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
