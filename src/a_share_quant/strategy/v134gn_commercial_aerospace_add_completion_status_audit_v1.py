from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GNCommercialAerospaceAddCompletionStatusAuditV1Report:
    summary: dict[str, Any]
    component_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "component_rows": self.component_rows,
            "interpretation": self.interpretation,
        }


class V134GNCommercialAerospaceAddCompletionStatusAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root / "reports" / "analysis" / "v134ej_commercial_aerospace_intraday_add_supervision_registry_v1.json"
        )
        self.rules_path = (
            repo_root / "reports" / "analysis" / "v134et_commercial_aerospace_local_add_rule_candidate_audit_v1.json"
        )
        self.false_positive_path = (
            repo_root / "reports" / "analysis" / "v134ev_commercial_aerospace_broader_add_false_positive_audit_v1.json"
        )
        self.permission_path = (
            repo_root / "reports" / "analysis" / "v134fd_commercial_aerospace_add_permission_family_audit_v1.json"
        )
        self.confirmation_path = (
            repo_root / "reports" / "analysis" / "v134ff_commercial_aerospace_persistent_permission_confirmation_audit_v1.json"
        )
        self.capacity_path = (
            repo_root / "reports" / "analysis" / "v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1.json"
        )
        self.single_slot_path = (
            repo_root / "reports" / "analysis" / "v134gk_commercial_aerospace_gj_single_slot_direction_triage_v1.json"
        )

    def analyze(self) -> V134GNCommercialAerospaceAddCompletionStatusAuditV1Report:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        rules = json.loads(self.rules_path.read_text(encoding="utf-8"))
        false_positive = json.loads(self.false_positive_path.read_text(encoding="utf-8"))
        permission = json.loads(self.permission_path.read_text(encoding="utf-8"))
        confirmation = json.loads(self.confirmation_path.read_text(encoding="utf-8"))
        capacity = json.loads(self.capacity_path.read_text(encoding="utf-8"))
        single_slot = json.loads(self.single_slot_path.read_text(encoding="utf-8"))

        component_rows = [
            {
                "component": "seed_registry",
                "status": "frozen_complete",
                "evidence": registry["summary"]["registry_row_count"],
                "reading": "the add branch owns a stable seed registry and no longer lacks first-layer supervision objects",
            },
            {
                "component": "seed_rules",
                "status": "frozen_complete",
                "evidence": rules["summary"]["match_rate"],
                "reading": "current local add rules fully recover the seed surface and preserve the supervision ladder",
            },
            {
                "component": "broader_positive_portability",
                "status": "blocked",
                "evidence": false_positive["summary"]["non_seed_positive_hit_rate"],
                "reading": "shape-only positive add promotion remains too dense on the wider local session surface",
            },
            {
                "component": "local_permission_hierarchy",
                "status": "retain_as_local",
                "evidence": permission["summary"]["persistent_permission_candidate_count"],
                "reading": "the branch has a believable local permission family, but it remains local rather than portable",
            },
            {
                "component": "persistent_confirmation_layer",
                "status": "retain_as_local",
                "evidence": confirmation["summary"]["best_precision"],
                "reading": "persistent confirmation is clean locally, but still not a broader promotion license",
            },
            {
                "component": "slot_capacity_hierarchy",
                "status": "retain_as_local",
                "evidence": capacity["summary"]["tiered_dual_slot_day_count"],
                "reading": "slot capacity now has a usable local hierarchy: zero-slot veto or tiered dual-slot",
            },
            {
                "component": "portable_single_slot_template",
                "status": "still_unobserved",
                "evidence": single_slot["summary"]["observed_single_slot_day_count"],
                "reading": "the branch still does not own a naturally observed single-slot fallback template",
            },
            {
                "component": "add_execution_authority",
                "status": "still_blocked",
                "evidence": "blocked",
                "reading": "the frontier has grown a rich supervision stack, but it still lacks portable permission and execution-safe allocation modules",
            },
        ]

        frozen_complete_count = sum(1 for row in component_rows if row["status"] == "frozen_complete")
        local_only_count = sum(1 for row in component_rows if row["status"] == "retain_as_local")
        blocked_count = sum(1 for row in component_rows if row["status"] in {"blocked", "still_blocked", "still_unobserved"})

        summary = {
            "acceptance_posture": "freeze_v134gn_commercial_aerospace_add_completion_status_audit_v1",
            "seed_row_count": registry["summary"]["registry_row_count"],
            "seed_rule_match_rate": rules["summary"]["match_rate"],
            "non_seed_positive_hit_rate": false_positive["summary"]["non_seed_positive_hit_rate"],
            "persistent_confirmation_precision": confirmation["summary"]["best_precision"],
            "tiered_dual_slot_day_count": capacity["summary"]["tiered_dual_slot_day_count"],
            "observed_single_slot_day_count": single_slot["summary"]["observed_single_slot_day_count"],
            "frozen_complete_count": frozen_complete_count,
            "local_only_count": local_only_count,
            "blocked_count": blocked_count,
            "authoritative_rule": (
                "the intraday add branch is now research-complete enough at the supervision layer: "
                "its local hierarchy is rich and internally consistent, but broader positive portability, observed single-slot fallback, "
                "and execution authority remain blocked"
            ),
        }
        interpretation = [
            "V1.34GN stops asking for another local clue and instead asks whether the add branch has crossed from open exploration into supervision-level completion.",
            "The answer is yes at the supervision layer. The branch now owns registry, seed rules, local permission hierarchy, and local slot-capacity hierarchy. What remains missing is not more local semantics, but portable promotion and execution authority.",
        ]
        return V134GNCommercialAerospaceAddCompletionStatusAuditV1Report(
            summary=summary,
            component_rows=component_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GNCommercialAerospaceAddCompletionStatusAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GNCommercialAerospaceAddCompletionStatusAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gn_commercial_aerospace_add_completion_status_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
