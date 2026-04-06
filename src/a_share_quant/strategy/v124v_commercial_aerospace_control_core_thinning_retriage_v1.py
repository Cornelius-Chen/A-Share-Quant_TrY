from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124t_commercial_aerospace_local_feed_universe_triage_v1 import (
    V124TCommercialAerospaceLocalFeedUniverseTriageAnalyzer,
)


@dataclass(slots=True)
class V124VCommercialAerospaceControlCoreThinningRetriageReport:
    summary: dict[str, Any]
    control_core_rows: list[dict[str, Any]]
    confirmation_rows: list[dict[str, Any]]
    mirror_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "control_core_rows": self.control_core_rows,
            "confirmation_rows": self.confirmation_rows,
            "mirror_rows": self.mirror_rows,
            "interpretation": self.interpretation,
        }


class V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V124VCommercialAerospaceControlCoreThinningRetriageReport:
        upstream = V124TCommercialAerospaceLocalFeedUniverseTriageAnalyzer(self.repo_root).analyze()
        all_rows = upstream.control_eligible_rows + upstream.confirmation_rows + upstream.mirror_rows

        control_core_rows: list[dict[str, Any]] = []
        confirmation_rows: list[dict[str, Any]] = []
        mirror_rows: list[dict[str, Any]] = []

        for row in all_rows:
            group = row["group"]
            subgroup = row["subgroup"]
            semantic = row["machine_semantic"]
            if group == "正式组":
                narrowed = {
                    **row,
                    "authority_semantic": "control_eligible_primary" if semantic == "control_eligible_primary" else "control_eligible_support",
                    "authority_reason": "formal_group_may_hold_control_authority",
                }
                control_core_rows.append(narrowed)
            elif group == "卖铲组":
                confirmation_rows.append(
                    {
                        **row,
                        "authority_semantic": "confirmation_only_supply_chain",
                        "authority_reason": "shovel_group_kept_for_confirmation_not_control_authority",
                    }
                )
            elif group == "概念助推组":
                confirmation_rows.append(
                    {
                        **row,
                        "authority_semantic": "confirmation_only_propulsion",
                        "authority_reason": "cross_board_propulsion_may_confirm_heat_but_not_hold_primary_controls",
                    }
                )
            else:
                mirror_rows.append(
                    {
                        **row,
                        "authority_semantic": "mirror_only",
                        "authority_reason": "mirror_group_is_outside_control_authority",
                    }
                )

        control_core_rows.sort(key=lambda r: (r["authority_semantic"], -r["liquidity_amount_mean"], r["symbol"]))
        confirmation_rows.sort(key=lambda r: (r["authority_semantic"], -r["liquidity_amount_mean"], r["symbol"]))
        mirror_rows.sort(key=lambda r: (-r["limit_heat_rate"], r["symbol"]))

        summary = {
            "acceptance_posture": "freeze_v124v_commercial_aerospace_control_core_thinning_retriage_v1",
            "upstream_local_supported_count": upstream.summary["fully_supported_count"],
            "control_core_count": len(control_core_rows),
            "confirmation_count": len(confirmation_rows),
            "mirror_count": len(mirror_rows),
            "authoritative_rule": "formal_group_only_may_hold_control_authority_while_shovel_concept_and_mirror_groups_are_confirmation_or_mirror_layers",
            "recommended_next_posture": "use_thinned_control_core_for_control_extraction_candidate_surface",
        }
        interpretation = [
            "V1.24V does not throw away the broad A-share commercial aerospace universe.",
            "It only narrows control authority so that concept propulsion, shovel sellers, and mirror names cannot silently become owner-level controls.",
            "This is the first lawful handoff surface for commercial aerospace control extraction.",
        ]
        return V124VCommercialAerospaceControlCoreThinningRetriageReport(
            summary=summary,
            control_core_rows=control_core_rows,
            confirmation_rows=confirmation_rows,
            mirror_rows=mirror_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124VCommercialAerospaceControlCoreThinningRetriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124v_commercial_aerospace_control_core_thinning_retriage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
