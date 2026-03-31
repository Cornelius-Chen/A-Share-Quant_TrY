from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BNPhaseCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BNPhaseCheckAnalyzer:
    def analyze(self, *, teacher_decomposition_payload: dict[str, Any]) -> V112BNPhaseCheckReport:
        summary_in = dict(teacher_decomposition_payload.get("summary", {}))
        if not bool(summary_in.get("no_leak_enforced")):
            raise ValueError("V1.12BN phase check requires explicit no-leak enforcement.")
        if int(summary_in.get("candidate_row_count", 0)) <= 0:
            raise ValueError("V1.12BN requires at least one searched candidate.")
        if int(summary_in.get("sample_count", 0)) <= 0:
            raise ValueError("V1.12BN requires a non-empty sample frame.")

        all_non_cash_failed = bool(summary_in.get("all_non_cash_failed_proven"))
        if not all_non_cash_failed and int(summary_in.get("best_candidate_row_count", 0)) <= 0:
            raise ValueError("V1.12BN expects either a non-cash best candidate or an explicit proof that all non-cash candidates failed.")

        summary = {
            "acceptance_posture": "keep_v112bn_as_teacher_decomposition_gate_search",
            "do_open_v112bn_now": True,
            "candidate_row_count": int(summary_in.get("candidate_row_count", 0)),
            "non_cash_candidate_count": int(summary_in.get("non_cash_candidate_count", 0)),
            "best_candidate_non_cash": bool(summary_in.get("best_candidate_non_cash")),
            "teacher_alignment_f1": float(summary_in.get("teacher_alignment_f1", 0.0)),
            "trade_count": int(summary_in.get("trade_count", 0)),
            "cash_ratio": float(summary_in.get("cash_ratio", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "best_candidate_row",
                "actual": {
                    "rule_signature": teacher_decomposition_payload.get("candidate_rows", [{}])[0].get("rule_signature"),
                    "teacher_alignment_f1": teacher_decomposition_payload.get("candidate_rows", [{}])[0].get("teacher_alignment_f1"),
                },
                "reading": "The phase is only meaningful if the search enumerates bounded rule stacks and returns a concrete best non-cash candidate or a proven all-cash failure state.",
            }
        ]
        interpretation = [
            "V1.12BN is valid because it tests teacher factorization with bounded rule search rather than a new opaque model class.",
        ]
        return V112BNPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bn_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BNPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
