from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134GWCommercialAerospaceGVHandoffDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134GWCommercialAerospaceGVHandoffDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = (
            repo_root / "reports" / "analysis" / "v134gv_commercial_aerospace_reentry_unlock_handoff_readiness_audit_v1.json"
        )

    def analyze(self) -> V134GWCommercialAerospaceGVHandoffDirectionTriageV1Report:
        audit = json.loads(self.audit_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "handoff_readiness_surface",
                "status": "retain",
                "rationale": "the bridge now has an explicit per-seed readiness audit rather than only a qualitative blocked status",
            },
            {
                "component": "lockout_overlap_block",
                "status": "dominant_blocker",
                "rationale": "all current rebuild-watch dates still overlap the frozen board lockout regime",
            },
            {
                "component": "future_unlock_absence",
                "status": "dominant_blocker",
                "rationale": "no future unlock seed exists after any current rebuild-watch date, so add consult cannot yet open",
            },
            {
                "component": "add_handoff",
                "status": "keep_blocked",
                "rationale": "handoff remains zero-ready and cannot yet escalate into add-permission consultation",
            },
            {
                "component": "execution_authority",
                "status": "still_blocked",
                "rationale": "the bridge remains explanatory and read-only even after readiness is made explicit",
            },
        ]
        interpretation = [
            "V1.34GW turns the handoff-readiness audit into the current governance verdict.",
            "The next blocker is now explicit and concrete: all current seeds fail because they still sit under lockout overlap and have no later unlock seed to hand off into.",
        ]
        return V134GWCommercialAerospaceGVHandoffDirectionTriageV1Report(
            summary={
                "acceptance_posture": "freeze_v134gw_commercial_aerospace_gv_handoff_direction_triage_v1",
                "authoritative_status": (
                    "retain_handoff_readiness_audit_and_keep_reentry_to_add_handoff_blocked_until_post_lockout_unlock_context_exists"
                ),
                "seed_count": audit["summary"]["seed_count"],
                "handoff_ready_count": audit["summary"]["handoff_ready_count"],
                "lockout_overlap_block_count": audit["summary"]["lockout_overlap_block_count"],
                "no_future_unlock_seed_count": audit["summary"]["no_future_unlock_seed_count"],
                "authoritative_rule": (
                    "current reentry-to-add handoff stays blocked because every current seed still overlaps lockout and lacks a later unlock seed"
                ),
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134GWCommercialAerospaceGVHandoffDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134GWCommercialAerospaceGVHandoffDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134gw_commercial_aerospace_gv_handoff_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
