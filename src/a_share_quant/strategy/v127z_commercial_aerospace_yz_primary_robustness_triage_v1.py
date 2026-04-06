from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127ZCommercialAerospaceYZPrimaryRobustnessTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V127ZCommercialAerospaceYZPrimaryRobustnessTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v127y_commercial_aerospace_primary_reference_robustness_audit_v1.json"

    def analyze(self) -> V127ZCommercialAerospaceYZPrimaryRobustnessTriageReport:
        payload = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127z_commercial_aerospace_yz_primary_robustness_triage_v1",
            "current_primary_variant": payload["summary"]["new_primary_variant"],
            "prior_primary_variant": payload["summary"]["old_primary_variant"],
            "split_frontier_wins": payload["summary"]["split_frontier_wins"],
            "split_total": payload["summary"]["split_total"],
            "suffix_frontier_wins": payload["summary"]["suffix_frontier_wins"],
            "suffix_total": payload["summary"]["suffix_total"],
            "worst_split_equity_delta_new_minus_old": payload["summary"]["worst_split_equity_delta_new_minus_old"],
            "worst_split_drawdown_delta_new_minus_old": payload["summary"]["worst_split_drawdown_delta_new_minus_old"],
            "worst_suffix_equity_delta_new_minus_old": payload["summary"]["worst_suffix_equity_delta_new_minus_old"],
            "worst_suffix_drawdown_delta_new_minus_old": payload["summary"]["worst_suffix_drawdown_delta_new_minus_old"],
            "authoritative_status": "freeze_current_primary_after_robustness",
            "authoritative_next_step": "return_to_primary_reference_attribution_and_understanding",
            "stop_doing": [
                "do_not_continue_same_plane_robustness_escalation",
                "do_not_open_new_aggressive_gating_yet",
                "do_not_reopen_old_primary_without_new_failure",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "freeze_current_primary": True,
                "next_step": "B_return_to_attribution_understanding",
                "reason": "The robustness question has been answered cleanly enough that further same-plane auditing has diminishing returns.",
            },
            {
                "subagent": "Tesla",
                "freeze_current_primary": True,
                "next_step": "B_return_to_attribution_understanding",
                "reason": "The current primary has survived the meaningful split and suffix checks; the next value is understanding where it wins.",
            },
            {
                "subagent": "James",
                "freeze_current_primary": True,
                "next_step": "B_return_to_attribution_understanding",
                "reason": "At this point the highest-value work is to explain the symbol, phase, and window contributions behind the new primary.",
            },
        ]
        interpretation = [
            "V1.27Z freezes the current commercial-aerospace primary reference after alternate split and suffix robustness cleared cleanly against the prior primary.",
            "The q75 suffix is a no-trade tie, so the freeze is based on the meaningful earlier suffixes and split windows rather than on late empty-window symmetry.",
            "The next step is attribution and understanding, not more same-plane robustness escalation and not a new aggressive gating branch.",
        ]
        return V127ZCommercialAerospaceYZPrimaryRobustnessTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127ZCommercialAerospaceYZPrimaryRobustnessTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127ZCommercialAerospaceYZPrimaryRobustnessTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127z_commercial_aerospace_yz_primary_robustness_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
