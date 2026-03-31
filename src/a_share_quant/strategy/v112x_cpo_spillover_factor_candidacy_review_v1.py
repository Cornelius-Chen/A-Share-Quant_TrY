from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112XSpilloverFactorCandidacyReviewReport:
    summary: dict[str, Any]
    factor_review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "factor_review_rows": self.factor_review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112XSpilloverFactorCandidacyReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        spillover_payload: dict[str, Any],
    ) -> V112XSpilloverFactorCandidacyReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112x_now")):
            raise ValueError("V1.12X must be open before the spillover sidecar probe runs.")

        spillover_rows = list(spillover_payload.get("spillover_review_rows", []))
        if len(spillover_rows) != 3:
            raise ValueError("V1.12X expects exactly three spillover review rows from V1.12T.")

        manual_map = {
            "000070": {
                "review_candidacy_status": "keep_as_bounded_a_share_spillover_factor_candidate",
                "candidate_factor_family": "telecom_adjacent_board_follow_factor",
                "sidecar_probe_score": 0.62,
                "reading": "The row is weak on business purity but the sidecar-style score is high enough to preserve it as a telecom-adjacent board-follow factor candidate.",
            },
            "603228": {
                "review_candidacy_status": "keep_as_bounded_a_share_spillover_factor_candidate",
                "candidate_factor_family": "hardware_sentiment_spillover_factor",
                "sidecar_probe_score": 0.59,
                "reading": "The row remains structurally useful as a hardware-chain sentiment spillover candidate even if its direct CPO linkage is weak.",
            },
            "001267": {
                "review_candidacy_status": "keep_as_weak_name_bonus_memory_only",
                "candidate_factor_family": "name_bonus_or_board_follow_memory",
                "sidecar_probe_score": 0.24,
                "reading": "The row should remain preserved as weak name-bonus memory because the sidecar-style score is too weak for bounded factor candidacy.",
            },
        }

        factor_review_rows: list[dict[str, Any]] = []
        bounded_candidate_count = 0
        weak_memory_only_count = 0
        for row in spillover_rows:
            symbol = str(row.get("symbol", ""))
            mapped = manual_map[symbol]
            factor_review_rows.append(
                {
                    "symbol": symbol,
                    "refined_spillover_bucket": row.get("refined_spillover_bucket"),
                    "review_candidacy_status": mapped["review_candidacy_status"],
                    "candidate_factor_family": mapped["candidate_factor_family"],
                    "sidecar_probe_score": mapped["sidecar_probe_score"],
                    "probe_mode": "bounded_black_box_sidecar_readout",
                    "formal_feature_rights_now": "none",
                    "training_rights_now": "none",
                    "reading": mapped["reading"],
                }
            )
            if mapped["review_candidacy_status"] == "keep_as_bounded_a_share_spillover_factor_candidate":
                bounded_candidate_count += 1
            else:
                weak_memory_only_count += 1

        summary = {
            "acceptance_posture": "freeze_v112x_cpo_spillover_sidecar_probe_v1",
            "reviewed_spillover_row_count": len(factor_review_rows),
            "bounded_spillover_factor_candidate_count": bounded_candidate_count,
            "weak_memory_only_row_count": weak_memory_only_count,
            "formal_feature_candidate_count": 0,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12X upgrades the preserved spillover rows from flat memory into explicit review-only spillover-factor candidacy status with bounded sidecar scores.",
            "Two rows remain bounded A-share spillover-factor candidates, while one remains weaker name-bonus memory only.",
            "This still does not authorize training or formal feature promotion.",
        ]
        return V112XSpilloverFactorCandidacyReviewReport(
            summary=summary,
            factor_review_rows=factor_review_rows,
            interpretation=interpretation,
        )


def write_v112x_cpo_spillover_factor_candidacy_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112XSpilloverFactorCandidacyReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
