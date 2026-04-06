from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132WCommercialAerospaceGovernanceStackRefreshV3Report:
    summary: dict[str, Any]
    governance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "governance_rows": self.governance_rows,
            "interpretation": self.interpretation,
        }


class V132WCommercialAerospaceGovernanceStackRefreshV3Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stack_v2_path = (
            repo_root / "reports" / "analysis" / "v132q_commercial_aerospace_governance_stack_refresh_v2.json"
        )
        self.state_transition_triage_path = (
            repo_root / "reports" / "analysis" / "v132v_commercial_aerospace_uv_local_1min_state_transition_triage_v1.json"
        )

    def analyze(self) -> V132WCommercialAerospaceGovernanceStackRefreshV3Report:
        stack_v2 = json.loads(self.stack_v2_path.read_text(encoding="utf-8"))
        transition_triage = json.loads(self.state_transition_triage_path.read_text(encoding="utf-8"))

        governance_rows = list(stack_v2["governance_rows"])
        governance_rows.append(
            {
                "layer": "local_1min_state_transition_governance",
                "status": transition_triage["summary"]["authoritative_status"],
                "rule": "the local 1min branch should be treated as an ordered intraday escalation ladder when broader hit sessions predominantly evolve through mild -> reversal -> severe style transitions",
                "source_status": transition_triage["summary"]["authoritative_status"],
            }
        )

        summary = {
            "acceptance_posture": "freeze_v132w_commercial_aerospace_governance_stack_refresh_v3",
            "governance_layer_count": len(governance_rows),
            "current_primary_variant": stack_v2["summary"]["current_primary_variant"],
            "authoritative_output": "commercial_aerospace_governance_stack_v3_frozen_with_state_transition_aligned_minute_branch",
        }
        interpretation = [
            "V1.32W refreshes the commercial-aerospace governance stack after the local minute branch proved state-transition alignment on broader hit sessions.",
            "The stack is still governance-first; the lawful EOD primary remains unchanged while the intraday branch becomes a more coherent escalation framework.",
        ]
        return V132WCommercialAerospaceGovernanceStackRefreshV3Report(
            summary=summary,
            governance_rows=governance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132WCommercialAerospaceGovernanceStackRefreshV3Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132WCommercialAerospaceGovernanceStackRefreshV3Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132w_commercial_aerospace_governance_stack_refresh_v3",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
