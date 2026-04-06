from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V126KCommercialAerospaceAuthoritativeResearchProtocolReport:
    summary: dict[str, Any]
    phase_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "phase_rows": self.phase_rows,
            "interpretation": self.interpretation,
        }


class V126KCommercialAerospaceAuthoritativeResearchProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V126KCommercialAerospaceAuthoritativeResearchProtocolReport:
        phase_rows = [
            {
                "phase": "universe_and_role_surface",
                "status": "completed",
                "anchors": ["v124q", "v124r", "v124v", "v124y"],
                "rule": "control core, confirmation, sentiment leadership, and mirror layers are separated before execution research.",
            },
            {
                "phase": "event_and_regime_surface",
                "status": "completed",
                "anchors": ["v125m", "v125n", "v125o"],
                "rule": "only decisive events enter control semantics; structural regimes are discovered from board state rather than year buckets.",
            },
            {
                "phase": "lawful_supervised_eod_table",
                "status": "completed",
                "anchors": ["v125s", "v125t", "v125u", "v125v"],
                "rule": "only point-in-time or lagged regime proxies are allowed in EOD supervised training.",
            },
            {
                "phase": "first_replay_unlock",
                "status": "completed",
                "anchors": ["v126f", "v126g"],
                "rule": "lawful replay is allowed only after zero-trigger is explained and replay actually executes under the same EOD legality boundary.",
            },
            {
                "phase": "two_layer_shadow_refinement",
                "status": "in_progress",
                "anchors": ["v126h", "v126i", "v126j"],
                "rule": "probe/full stratification may improve shadow economics, but promotion is blocked until full eligibility has real supervised support.",
            },
            {
                "phase": "full_eligibility_label_support",
                "status": "next",
                "anchors": ["v126l"],
                "rule": "before promotion, quantify where full-eligibility labels are missing and whether scarcity is caused by split geometry or structural absence.",
            },
            {
                "phase": "promotion_or_replay_freeze",
                "status": "pending",
                "anchors": [],
                "rule": "only promote a replay-facing candidate if it is lawful, economically positive, and not dependent on unsupported shadow strata.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v126k_commercial_aerospace_authoritative_research_protocol_v1",
            "current_authoritative_stage": "two_layer_shadow_refinement",
            "current_best_shadow_variant": "probe40_full100_q70_q40",
            "current_best_shadow_final_equity": 1000937.0454,
            "current_best_shadow_max_drawdown": 0.06694498,
            "current_main_blocker": "full_eligibility_has_zero_impulse_train_labels_so_shadow_improvement_cannot_yet_be_promoted",
            "authoritative_rule": "commercial_aerospace_research_must_now_focus_on_full_eligibility_support_not_new_factor_discovery",
        }
        interpretation = [
            "V1.26K freezes the commercial aerospace research order after the first lawful replay and two-layer shadow improvement are both on disk.",
            "The next blocker is no longer legality or zero-trigger geometry; it is missing supervised support for the full-eligibility layer.",
        ]
        return V126KCommercialAerospaceAuthoritativeResearchProtocolReport(
            summary=summary,
            phase_rows=phase_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126KCommercialAerospaceAuthoritativeResearchProtocolReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126KCommercialAerospaceAuthoritativeResearchProtocolAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126k_commercial_aerospace_authoritative_research_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
