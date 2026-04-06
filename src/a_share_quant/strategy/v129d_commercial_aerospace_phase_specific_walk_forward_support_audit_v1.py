from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128y_commercial_aerospace_state_machine_supervised_table_v1 import (
    V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer,
)


PHASE_FOLDS = [
    {
        "fold_name": "full_pre_dedicated_fold",
        "target_state": "full_pre",
        "train_start": "20240129",
        "train_end": "20251211",
        "test_start": "20251212",
        "test_end": "20251223",
    },
    {
        "fold_name": "full_dedicated_fold",
        "target_state": "full",
        "train_start": "20240129",
        "train_end": "20260106",
        "test_start": "20260107",
        "test_end": "20260112",
    },
    {
        "fold_name": "post_impulse_holdout_fold",
        "target_state": "high_intensity",
        "train_start": "20240129",
        "train_end": "20260112",
        "test_start": "20260113",
        "test_end": "20260320",
    },
]


@dataclass(slots=True)
class V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditReport:
    summary: dict[str, Any]
    fold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "fold_rows": self.fold_rows,
            "interpretation": self.interpretation,
        }


class V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditReport:
        table = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows

        fold_rows: list[dict[str, Any]] = []
        for fold in PHASE_FOLDS:
            train_rows = [
                row
                for row in rows
                if fold["train_start"] <= row["trade_date"] <= fold["train_end"]
            ]
            test_rows = [
                row
                for row in rows
                if fold["test_start"] <= row["trade_date"] <= fold["test_end"]
            ]

            if fold["target_state"] == "high_intensity":
                train_positive = sum(
                    1 for row in train_rows if row["supervised_action_state"] in {"full_pre", "full"}
                )
                test_positive = sum(
                    1 for row in test_rows if row["supervised_action_state"] in {"full_pre", "full"}
                )
            else:
                train_positive = sum(
                    1 for row in train_rows if row["supervised_action_state"] == fold["target_state"]
                )
                test_positive = sum(
                    1 for row in test_rows if row["supervised_action_state"] == fold["target_state"]
                )

            fold_rows.append(
                {
                    "fold_name": fold["fold_name"],
                    "target_state": fold["target_state"],
                    "train_start": fold["train_start"],
                    "train_end": fold["train_end"],
                    "test_start": fold["test_start"],
                    "test_end": fold["test_end"],
                    "train_row_count": len(train_rows),
                    "test_row_count": len(test_rows),
                    "train_positive_count": train_positive,
                    "test_positive_count": test_positive,
                    "supports_target_both_sides": train_positive > 0 and test_positive > 0,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v129d_commercial_aerospace_phase_specific_walk_forward_support_audit_v1",
            "fold_count": len(fold_rows),
            "supported_folds": [row["fold_name"] for row in fold_rows if row["supports_target_both_sides"]],
            "unsupported_folds": [row["fold_name"] for row in fold_rows if not row["supports_target_both_sides"]],
            "authoritative_status": "phase_specific_walk_forward_support_partially_available",
            "authoritative_rule": "commercial-aerospace high-intensity supervision should move from a single split to phase-specific walk-forward only where train and test both contain the target state",
        }
        interpretation = [
            "V1.29D checks whether commercial-aerospace high-intensity states can be supported by dedicated lawful walk-forward folds even though a single global split fails.",
            "This does not reopen replay; it only decides whether phase-specific supervision is supportable before the next pilot.",
        ]
        return V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditReport(
            summary=summary,
            fold_rows=fold_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129DCommercialAerospacePhaseSpecificWalkForwardSupportAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129d_commercial_aerospace_phase_specific_walk_forward_support_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
