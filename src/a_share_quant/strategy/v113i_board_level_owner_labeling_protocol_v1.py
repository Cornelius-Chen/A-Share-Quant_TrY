from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113IBoardLevelOwnerLabelingProtocolReport:
    summary: dict[str, Any]
    owner_scope_rows: list[dict[str, Any]]
    assistant_scope_rows: list[dict[str, Any]]
    governance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "owner_scope_rows": self.owner_scope_rows,
            "assistant_scope_rows": self.assistant_scope_rows,
            "governance_rows": self.governance_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113IBoardLevelOwnerLabelingProtocolAnalyzer:
    def analyze(
        self,
        *,
        v113h_payload: dict[str, Any],
        owner_board_level_only: bool,
    ) -> V113IBoardLevelOwnerLabelingProtocolReport:
        h_summary = dict(v113h_payload.get("summary", {}))
        if not bool(h_summary.get("do_open_v113h_now")):
            raise ValueError("V1.13I expects V1.13H to be open before labeling protocol freeze.")

        owner_scope_rows = [
            {
                "label_scope": "board_phase_label",
                "owner_authority": "primary",
                "examples": ["ignition", "main_markup", "diffusion", "divergence", "decay"],
                "reading": "Owner decides the board-level phase truth.",
            },
            {
                "label_scope": "board_tradeability_label",
                "owner_authority": "primary",
                "examples": ["tradable", "guarded", "observe_only", "risk_off"],
                "reading": "Owner decides whether the board as a whole is considered tradable.",
            },
            {
                "label_scope": "board_mainline_status",
                "owner_authority": "primary",
                "examples": ["mainline", "candidate_mainline", "failed_mainline", "false_mainline"],
                "reading": "Owner decides whether the theme itself is a real mainline or a failed narrative.",
            },
        ]

        assistant_scope_rows = [
            {
                "label_scope": "role_labels",
                "assistant_authority": "primary_with_audit",
                "examples": ["leader", "core", "sidecar", "spillover", "noise"],
                "confidence_tiers": ["hard", "guarded", "review_only"],
            },
            {
                "label_scope": "control_labels",
                "assistant_authority": "primary_with_audit",
                "examples": ["eligibility", "de_risk", "entry_veto", "holding_veto", "admission_extension"],
                "confidence_tiers": ["hard", "guarded", "review_only"],
            },
            {
                "label_scope": "state_labels",
                "assistant_authority": "primary_with_audit",
                "examples": ["maturity", "congestion", "divergence", "resonance", "overstay", "miss_while_cash"],
                "confidence_tiers": ["hard", "guarded", "review_only"],
            },
            {
                "label_scope": "residual_family_labels",
                "assistant_authority": "primary_with_audit",
                "examples": ["eligibility_miss", "overstay", "false_extension", "risk_off_trigger"],
                "confidence_tiers": ["hard", "guarded", "review_only"],
            },
        ]

        governance_rows = [
            {
                "rule_name": "owner_board_precedence",
                "reading": "Assistant fine-grained labels may refine but must not overrule owner board-level labels.",
            },
            {
                "rule_name": "confidence_mandate",
                "reading": "All assistant fine-grained labels must carry one of three confidence tiers: hard, guarded, or review_only.",
            },
            {
                "rule_name": "result_adjudication",
                "reading": "Assistant fine-grained labels are provisional until judged by time-split results, drawdown behavior, and stress outcomes.",
            },
            {
                "rule_name": "unsupervised_audit_support",
                "reading": "Unsupervised discovery may challenge or refine assistant fine-grained labels, but may not replace owner board-level labels directly.",
            },
            {
                "rule_name": "no_reverse_legislation",
                "reading": "Fine-grained labels cannot back-fill board truth from single-stock behavior after the fact.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113i_board_level_owner_labeling_protocol_v1",
            "owner_board_level_only": owner_board_level_only,
            "owner_scope_count": len(owner_scope_rows),
            "assistant_scope_count": len(assistant_scope_rows),
            "confidence_tier_count": 3,
            "recommended_next_posture": "use_owner_board_labels_as_top_level_truth_and_assistant_fine_labels_as_audited_internal_grammar",
        }
        interpretation = [
            "V1.13I formalizes a split-labeling regime: the owner supplies board-level truth, while the assistant supplies fine-grained internal grammar under audit.",
            "This protocol protects the project from overfitting single-stock narratives into board truth while still allowing rich role, state, and control labels to be learned.",
            "Unsupervised discovery remains a challenger and auditor, not a legislator of board-level truth.",
        ]
        return V113IBoardLevelOwnerLabelingProtocolReport(
            summary=summary,
            owner_scope_rows=owner_scope_rows,
            assistant_scope_rows=assistant_scope_rows,
            governance_rows=governance_rows,
            interpretation=interpretation,
        )


def write_v113i_board_level_owner_labeling_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113IBoardLevelOwnerLabelingProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
