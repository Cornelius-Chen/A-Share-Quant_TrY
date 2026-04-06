from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V132SCommercialAerospaceIntradayOverrideActionLadderReport:
    summary: dict[str, Any]
    action_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "action_rows": self.action_rows,
            "interpretation": self.interpretation,
        }


class V132SCommercialAerospaceIntradayOverrideActionLadderAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )
        self.shadow_benefit_path = (
            repo_root / "reports" / "analysis" / "v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1.json"
        )

    def analyze(self) -> V132SCommercialAerospaceIntradayOverrideActionLadderReport:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        shadow_benefit = json.loads(self.shadow_benefit_path.read_text(encoding="utf-8"))

        rows = registry["registry_rows"]
        tier_counts: dict[str, int] = {}
        for row in rows:
            tier = row["severity_tier"]
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        action_rows = [
            {
                "minute_tier_label": "severe_override_positive",
                "seed_count": tier_counts.get("severe_override_positive", 0),
                "governance_action": "emergency_exit_shadow_override",
                "execution_posture": "supervision_only_not_replay_facing",
                "rationale": "severe hits represent the clearest intraday collapse path and should become the first future emergency-exit supervision objects",
            },
            {
                "minute_tier_label": "reversal_watch",
                "seed_count": tier_counts.get("reversal_watch", 0),
                "governance_action": "panic_derisk_watch",
                "execution_posture": "supervision_only_not_replay_facing",
                "rationale": "reversal hits are not full collapse exits but do justify an explicit panic de-risk watch state",
            },
            {
                "minute_tier_label": "mild_override_watch",
                "seed_count": tier_counts.get("mild_override_watch", 0),
                "governance_action": "do_not_readd_watch",
                "execution_posture": "supervision_only_not_replay_facing",
                "rationale": "mild hits mostly act as downgrade governance, especially against impulsive re-add behavior after weak first-hour structure",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v132s_commercial_aerospace_intraday_override_action_ladder_v1",
            "authoritative_status": "retain_intraday_override_action_ladder_as_governed_state_translation",
            "governance_posture_source": shadow_benefit["summary"]["authoritative_status"],
            "tier_count": len(action_rows),
            "authoritative_rule": "the commercial-aerospace minute branch should now be read as an action ladder for governance translation, not just as a registry of bad cases",
        }
        interpretation = [
            "V1.32S translates the frozen commercial-aerospace minute tiers into explicit governance actions.",
            "This is still not replay execution logic; it is the state-translation layer that future lawful intraday work should inherit.",
        ]
        return V132SCommercialAerospaceIntradayOverrideActionLadderReport(
            summary=summary,
            action_rows=action_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132SCommercialAerospaceIntradayOverrideActionLadderReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132SCommercialAerospaceIntradayOverrideActionLadderAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132s_commercial_aerospace_intraday_override_action_ladder_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
