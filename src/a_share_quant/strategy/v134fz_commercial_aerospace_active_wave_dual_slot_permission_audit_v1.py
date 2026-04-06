from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FZCommercialAerospaceActiveWaveDualSlotPermissionAuditV1Report:
    summary: dict[str, Any]
    slot_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "slot_rows": self.slot_rows,
            "interpretation": self.interpretation,
        }


class V134FZCommercialAerospaceActiveWaveDualSlotPermissionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.ranking_report_path = (
            repo_root / "reports" / "analysis" / "v134fx_commercial_aerospace_active_wave_positive_ranking_audit_v1.json"
        )

    def analyze(self) -> V134FZCommercialAerospaceActiveWaveDualSlotPermissionAuditV1Report:
        ranking_report = json.loads(self.ranking_report_path.read_text(encoding="utf-8"))
        candidate_rows = ranking_report["candidate_rows"]
        same_symbol = next(row for row in candidate_rows if row["selection_state"] == "same_symbol_continuation_selected")
        clean_reset = next(row for row in candidate_rows if row["selection_state"] == "clean_reset_candidate")

        slot_rows = [
            {
                "slot_name": "continuation_slot",
                "selection_state": same_symbol["selection_state"],
                "role_reading": "reuse existing same-wave strength without forcing a fresh reset narrative",
                "local_edge": "stronger early opening impulse",
                "supporting_metric": "open_to_15m",
                "supporting_value": same_symbol["open_to_15m"],
            },
            {
                "slot_name": "reset_slot",
                "selection_state": clean_reset["selection_state"],
                "role_reading": "allow a clean reset candidate to participate without inheriting recent residue",
                "local_edge": "better close-location and hour-end continuation",
                "supporting_metric": "close_loc_15m_plus_open_to_60m",
                "supporting_value": {
                    "close_loc_15m": clean_reset["close_loc_15m"],
                    "open_to_60m": clean_reset["open_to_60m"],
                },
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134fz_commercial_aerospace_active_wave_dual_slot_permission_audit_v1",
            "selected_candidate_count": len(candidate_rows),
            "slot_count": len(slot_rows),
            "same_symbol_higher_metric_count": ranking_report["summary"]["same_symbol_higher_metric_count"],
            "clean_reset_higher_metric_count": ranking_report["summary"]["clean_reset_higher_metric_count"],
            "authoritative_rule": (
                "the current active-wave sample is better explained by a dual-slot permission view than by a forced single positive ranker"
            ),
        }
        interpretation = [
            "V1.34FZ asks whether the two retained active-wave states should still be forced into a winner-take-all ranking problem.",
            "The answer is no. Their strengths are complementary enough that the current local surface supports a dual-slot permission reading more naturally than a single best-symbol ranker.",
        ]
        return V134FZCommercialAerospaceActiveWaveDualSlotPermissionAuditV1Report(
            summary=summary,
            slot_rows=slot_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FZCommercialAerospaceActiveWaveDualSlotPermissionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FZCommercialAerospaceActiveWaveDualSlotPermissionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fz_commercial_aerospace_active_wave_dual_slot_permission_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
