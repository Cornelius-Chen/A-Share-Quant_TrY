from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112TCPOSpilloverTruthCheckReport:
    summary: dict[str, Any]
    spillover_review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "spillover_review_rows": self.spillover_review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112TCPOSpilloverTruthCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        registry_payload: dict[str, Any],
    ) -> V112TCPOSpilloverTruthCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112t_now")):
            raise ValueError("V1.12T must be open before spillover truth-check.")

        spillover_rows = [
            row
            for row in registry_payload.get("cohort_rows", [])
            if row.get("cohort_tier") == "mixed_relevance_spillover_review_only"
        ]
        if len(spillover_rows) != 3:
            raise ValueError("V1.12T expects exactly three frozen mixed-relevance spillover rows from V1.12P.")

        manual_map = {
            "000070": (
                "preserve_as_a_share_spillover_factor_candidate",
                "telecom_or_network_adjacent_board_follow",
                "Keep preserved because it may capture board-follow behavior tied to communications adjacency rather than pure random noise.",
            ),
            "603228": (
                "preserve_as_hardware_sentiment_spillover_candidate",
                "hardware_or_supply_chain_sentiment_spillover",
                "Keep preserved because it may capture broader hardware-chain sentiment spillover even if the optical-link core tie is weak.",
            ),
            "001267": (
                "preserve_as_name_bonus_or_pure_board_follow_candidate",
                "name_bonus_or_pure_board_follow",
                "Keep preserved because it may carry A-share-style name bonus or pure board-follow information rather than business relevance.",
            ),
        }

        spillover_review_rows: list[dict[str, Any]] = []
        candidate_factor_count = 0
        weakest_noise_like_count = 0
        for row in spillover_rows:
            symbol = str(row.get("symbol", ""))
            disposition, refined_bucket, reading = manual_map[symbol]
            spillover_review_rows.append(
                {
                    "symbol": symbol,
                    "existing_chain_role": row.get("chain_role"),
                    "review_disposition": disposition,
                    "refined_spillover_bucket": refined_bucket,
                    "training_rights_now": "none",
                    "reading": reading,
                }
            )
            if disposition == "preserve_as_name_bonus_or_pure_board_follow_candidate":
                weakest_noise_like_count += 1
            else:
                candidate_factor_count += 1

        summary = {
            "acceptance_posture": "freeze_v112t_cpo_spillover_truth_check_v1",
            "reviewed_spillover_row_count": len(spillover_review_rows),
            "candidate_a_share_spillover_factor_count": candidate_factor_count,
            "pure_name_bonus_or_board_follow_count": weakest_noise_like_count,
            "formal_training_candidate_count": 0,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12T does not delete spillover rows; it classifies them into review categories.",
            "The result preserves possible A-share-specific spillover factor candidates while preventing them from contaminating the core cohort silently.",
            "This is still review memory, not training surface.",
        ]
        return V112TCPOSpilloverTruthCheckReport(
            summary=summary,
            spillover_review_rows=spillover_review_rows,
            interpretation=interpretation,
        )


def write_v112t_cpo_spillover_truth_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112TCPOSpilloverTruthCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
