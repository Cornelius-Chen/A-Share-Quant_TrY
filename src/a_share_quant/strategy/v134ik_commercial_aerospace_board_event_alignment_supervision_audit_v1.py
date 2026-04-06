from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Report:
    summary: dict[str, Any]
    alignment_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "alignment_rows": self.alignment_rows,
            "interpretation": self.interpretation,
        }


class V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_board_event_alignment_supervision_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Report:
        event_attention = self._load_json(
            "reports/analysis/v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        )
        expectancy = self._load_json(
            "reports/analysis/v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        )
        named_counterexamples = self._load_json(
            "reports/analysis/v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1.json"
        )

        expectancy_by_date = {}
        for row in expectancy["seed_rows"]:
            trade_date = row["trade_date"]
            expectancy_by_date.setdefault(trade_date, []).append(row)

        lockout_start = expectancy["seed_rows"][8]["trade_date"]  # first 20260115 false_bounce_only row
        lockout_end = named_counterexamples["summary"]["lockout_window_end_trade_date"]

        alignment_rows: list[dict[str, Any]] = []
        for row in event_attention["registry_rows"]:
            if row["row_type"] != "event_seed":
                continue

            trade_date = row["trade_date"]
            derived_state = row["derived_state"]
            same_day_rows = expectancy_by_date.get(trade_date, [])

            if trade_date == "20251224":
                alignment_label = "aligned_board_supportive_response"
                alignment_reading = "event lands inside a positive revival/continuation board state with strong breadth and positive forward expectancy"
            elif trade_date == "20260113":
                alignment_label = "turning_point_overheat_alignment"
                alignment_reading = "event aligns with the decisive overheating and board-turning regime rather than with renewed participation"
            elif trade_date < lockout_start:
                alignment_label = "pre_turn_alignment_watch"
                alignment_reading = "event is retained, but board alignment is still pre-turn and should be treated as a watch rather than a confirmed supportive response"
            elif lockout_start <= trade_date <= lockout_end:
                alignment_label = "lockout_misaligned_board_response"
                alignment_reading = "event remains board-misaligned because the board is inside lockout or false-bounce conditions"
            else:
                alignment_label = "raw_only_post_lockout_alignment_absent"
                alignment_reading = "raw dates exist but legal board-state derivation is absent beyond the frozen boundary, so no lawful board alignment can be assigned"

            alignment_rows.append(
                {
                    "registry_id": row["registry_id"],
                    "trade_date": trade_date,
                    "symbol": row["symbol"],
                    "display_name": row["display_name"],
                    "event_semantic": row["decisive_semantic"],
                    "event_state": derived_state,
                    "same_day_expectancy_state_count": len(same_day_rows),
                    "same_day_expectancy_states": "|".join(sorted({r["expectancy_state"] for r in same_day_rows})),
                    "board_event_alignment_label": alignment_label,
                    "board_event_alignment_reading": alignment_reading,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(alignment_rows[0].keys()))
            writer.writeheader()
            writer.writerows(alignment_rows)

        summary = {
            "acceptance_posture": "freeze_v134ik_commercial_aerospace_board_event_alignment_supervision_audit_v1",
            "event_seed_count": len(alignment_rows),
            "aligned_board_supportive_count": sum(
                1 for row in alignment_rows if row["board_event_alignment_label"] == "aligned_board_supportive_response"
            ),
            "turning_point_alignment_count": sum(
                1 for row in alignment_rows if row["board_event_alignment_label"] == "turning_point_overheat_alignment"
            ),
            "pre_turn_watch_count": sum(
                1 for row in alignment_rows if row["board_event_alignment_label"] == "pre_turn_alignment_watch"
            ),
            "lockout_misaligned_count": sum(
                1 for row in alignment_rows if row["board_event_alignment_label"] == "lockout_misaligned_board_response"
            ),
            "raw_only_alignment_absent_count": sum(
                1 for row in alignment_rows if row["board_event_alignment_label"] == "raw_only_post_lockout_alignment_absent"
            ),
            "alignment_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "board-event alignment now exists as its own supervision layer: some events align with board-supportive response, some with turning-point risk, some with lockout misalignment, and post-lockout raw-only dates remain explicitly unaligned rather than silently guessed",
        }
        interpretation = [
            "V1.34IK resolves part of the named gap by making board-event alignment explicit instead of leaving it as an intuition.",
            "The layer remains honest about incompleteness: post-lockout raw-only dates still do not receive legal board alignment labels beyond 'alignment absent'.",
        ]
        return V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Report(
            summary=summary,
            alignment_rows=alignment_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IKCommercialAerospaceBoardEventAlignmentSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ik_commercial_aerospace_board_event_alignment_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
