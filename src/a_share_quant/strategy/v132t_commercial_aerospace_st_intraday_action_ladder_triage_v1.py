from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132TCommercialAerospaceSTIntradayActionLadderTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V132TCommercialAerospaceSTIntradayActionLadderTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.ladder_report_path = (
            repo_root / "reports" / "analysis" / "v132s_commercial_aerospace_intraday_override_action_ladder_v1.json"
        )

    def analyze(self) -> V132TCommercialAerospaceSTIntradayActionLadderTriageReport:
        ladder_report = json.loads(self.ladder_report_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v132t_commercial_aerospace_st_intraday_action_ladder_triage_v1",
            "authoritative_status": "retain_intraday_override_action_ladder_as_governance_state_machine_extension",
            "tier_count": ladder_report["summary"]["tier_count"],
            "authoritative_rule": "the minute branch should now extend the governance state machine with explicit severe / reversal / mild action semantics while the lawful EOD replay remains unchanged",
        }
        triage_rows = [
            {
                "component": "intraday_override_action_ladder",
                "status": "retain_intraday_override_action_ladder_as_governance_state_machine_extension",
                "rationale": "the minute branch has enough structure to translate tiers into governance actions even though it is still not replay-facing",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "action semantics strengthen governance and future intraday design, but they do not yet permit direct replay modification",
            },
        ]
        interpretation = [
            "V1.32T freezes the intraday action ladder as the next extension of the commercial-aerospace governance stack.",
            "The ladder is organizational and semantic: it prepares future lawful intraday work without altering the frozen EOD primary.",
        ]
        return V132TCommercialAerospaceSTIntradayActionLadderTriageReport(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132TCommercialAerospaceSTIntradayActionLadderTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132TCommercialAerospaceSTIntradayActionLadderTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132t_commercial_aerospace_st_intraday_action_ladder_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
