from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V126LCommercialAerospaceFullEligibilitySupportGapAuditReport:
    summary: dict[str, Any]
    distribution_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "distribution_rows": self.distribution_rows,
            "interpretation": self.interpretation,
        }


class V126LCommercialAerospaceFullEligibilitySupportGapAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.training_table_path = repo_root / "data" / "training" / "commercial_aerospace_regime_conditioned_label_table_v1.csv"

    def analyze(self) -> V126LCommercialAerospaceFullEligibilitySupportGapAuditReport:
        rows = _load_csv(self.training_table_path)
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        train_dates = set(ordered_dates[:split_idx])
        train_rows = [row for row in rows if row["trade_date"] in train_dates]
        test_rows = [row for row in rows if row["trade_date"] not in train_dates]

        def full_rows(subset: list[dict[str, str]]) -> list[dict[str, str]]:
            return [row for row in subset if row["supervised_action_label_rc"] == "full_eligibility_target"]

        train_full = full_rows(train_rows)
        test_full = full_rows(test_rows)
        impulse_train = [
            row for row in train_full
            if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"
        ]
        impulse_test = [
            row for row in test_full
            if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"
        ]

        distribution_rows: list[dict[str, Any]] = []
        for scope_name, subset in (
            ("train_full_by_regime", train_full),
            ("test_full_by_regime", test_full),
            ("train_full_by_symbol", train_full),
            ("test_full_by_symbol", test_full),
        ):
            if "regime" in scope_name:
                counter = Counter(row["regime_proxy_semantic"] for row in subset)
            else:
                counter = Counter(row["symbol"] for row in subset)
            for key, value in sorted(counter.items()):
                distribution_rows.append({"scope": scope_name, "bucket": key, "count": value})

        train_full_dates = sorted({row["trade_date"] for row in train_full})
        test_full_dates = sorted({row["trade_date"] for row in test_full})
        summary = {
            "acceptance_posture": "freeze_v126l_commercial_aerospace_full_eligibility_support_gap_audit_v1",
            "train_full_count": len(train_full),
            "test_full_count": len(test_full),
            "impulse_continuation_train_full_count": len(impulse_train),
            "impulse_continuation_test_full_count": len(impulse_test),
            "train_full_start": train_full_dates[0] if train_full_dates else "",
            "train_full_end": train_full_dates[-1] if train_full_dates else "",
            "test_full_start": test_full_dates[0] if test_full_dates else "",
            "test_full_end": test_full_dates[-1] if test_full_dates else "",
            "main_gap_type": (
                "full_eligibility_is_absent_in_train_impulse_window_but_present_in_test_impulse_window"
                if len(impulse_train) == 0 and len(impulse_test) > 0
                else "no_structural_full_gap_detected"
            ),
            "authoritative_rule": "commercial_aerospace_full_eligibility_promotion_is_blocked_until_impulse_train_support_exists_or_split_geometry_is_reworked",
        }
        interpretation = [
            "V1.26L checks whether the full-eligibility blocker is caused by structural absence or by train/test geometry.",
            "If full labels exist only in the late impulse test window, the current split supports shadow replay but not full-layer promotion.",
        ]
        return V126LCommercialAerospaceFullEligibilitySupportGapAuditReport(
            summary=summary,
            distribution_rows=distribution_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126LCommercialAerospaceFullEligibilitySupportGapAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126LCommercialAerospaceFullEligibilitySupportGapAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126l_commercial_aerospace_full_eligibility_support_gap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
