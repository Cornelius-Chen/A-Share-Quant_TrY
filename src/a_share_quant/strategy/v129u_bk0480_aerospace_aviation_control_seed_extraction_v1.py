from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129UBK0480AerospaceAviationControlSeedExtractionReport:
    summary: dict[str, Any]
    eligibility_rows: list[dict[str, Any]]
    add_permission_rows: list[dict[str, Any]]
    de_risk_watch_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "eligibility_rows": self.eligibility_rows,
            "add_permission_rows": self.add_permission_rows,
            "de_risk_watch_rows": self.de_risk_watch_rows,
            "interpretation": self.interpretation,
        }


class V129UBK0480AerospaceAviationControlSeedExtractionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.world_model_path = repo_root / "reports" / "analysis" / "v129q_bk0480_aerospace_aviation_board_world_model_v1.json"
        self.role_grammar_path = repo_root / "reports" / "analysis" / "v129s_bk0480_aerospace_aviation_role_grammar_v1.json"

    def analyze(self) -> V129UBK0480AerospaceAviationControlSeedExtractionReport:
        world_model = json.loads(self.world_model_path.read_text(encoding="utf-8"))
        role_grammar = json.loads(self.role_grammar_path.read_text(encoding="utf-8"))

        rows = {row["symbol"]: row for row in world_model["role_rows"]}
        primary = rows["000738"]
        support = rows["600118"]

        eligibility_rows = [
            {
                **primary,
                "control_action": "eligibility_authority",
                "control_reason": "higher composite, stronger stability, and deeper local snapshot support make 000738 the initial BK0480 authority gate",
            }
        ]
        add_permission_rows = [
            {
                **support,
                "control_action": "add_permission_support",
                "control_reason": "600118 remains part of the dual-core but starts as add-permission support rather than immediate authority",
            }
        ]
        de_risk_watch_rows = [
            {
                **support,
                "control_action": "de_risk_watch",
                "control_reason": "600118 has lower composite and lower liquidity inside the dual core, so it is the first local de-risk watch point",
            }
        ]

        summary = {
            "acceptance_posture": "freeze_v129u_bk0480_aerospace_aviation_control_seed_extraction_v1",
            "board_name": role_grammar["summary"]["board_name"],
            "sector_id": role_grammar["summary"]["sector_id"],
            "control_core_count": role_grammar["summary"]["internal_owner_count"],
            "eligibility_authority_count": len(eligibility_rows),
            "add_permission_support_count": len(add_permission_rows),
            "de_risk_watch_count": len(de_risk_watch_rows),
            "authoritative_rule": "bk0480_must_start_with_a_minimal_dual_core_control_seed_before_any_local_universe_expansion_or_replay",
            "recommended_next_posture": "audit_this_minimal_control_seed_before_any_bk0480_replay_unlock",
        }
        interpretation = [
            "V1.29U derives the first BK0480 control seed directly from the dual-core local role surface.",
            "The board starts with one authority gate and one support/watch name, which keeps transfer discipline tighter than the broader commercial-aerospace control surface.",
        ]
        return V129UBK0480AerospaceAviationControlSeedExtractionReport(
            summary=summary,
            eligibility_rows=eligibility_rows,
            add_permission_rows=add_permission_rows,
            de_risk_watch_rows=de_risk_watch_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129UBK0480AerospaceAviationControlSeedExtractionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129UBK0480AerospaceAviationControlSeedExtractionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129u_bk0480_aerospace_aviation_control_seed_extraction_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
