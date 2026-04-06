from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


FEATURES = [
    "expected_upside",
    "drive_strength",
    "stability",
    "liquidity",
    "resonance",
    "non_junk_composite_score",
]


@dataclass(slots=True)
class V129WBK0480AerospaceAviationControlSeedAuditReport:
    summary: dict[str, Any]
    overlap_feature_rows: list[dict[str, Any]]
    overlap_extreme_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "overlap_feature_rows": self.overlap_feature_rows,
            "overlap_extreme_rows": self.overlap_extreme_rows,
            "interpretation": self.interpretation,
        }


class V129WBK0480AerospaceAviationControlSeedAuditAnalyzer:
    SECTOR_ID = "BK0480"
    AUTHORITY = "000738"
    SUPPORT = "600118"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.stock_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.control_seed_path = (
            repo_root / "reports" / "analysis" / "v129u_bk0480_aerospace_aviation_control_seed_extraction_v1.json"
        )

    def _load_rows(self) -> list[dict[str, str]]:
        with self.stock_snapshot_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return [
            row
            for row in rows
            if row["sector_id"] == self.SECTOR_ID and row["symbol"] in {self.AUTHORITY, self.SUPPORT}
        ]

    def analyze(self) -> V129WBK0480AerospaceAviationControlSeedAuditReport:
        control_seed = json.loads(self.control_seed_path.read_text(encoding="utf-8"))
        rows = self._load_rows()
        by_symbol: dict[str, dict[str, dict[str, str]]] = {}
        for row in rows:
            by_symbol.setdefault(row["symbol"], {})[row["trade_date"]] = row

        common_dates = sorted(set(by_symbol[self.AUTHORITY]).intersection(by_symbol[self.SUPPORT]))

        feature_rows = []
        composite_rows = []
        for feature in FEATURES:
            diffs = [
                float(by_symbol[self.AUTHORITY][dt][feature]) - float(by_symbol[self.SUPPORT][dt][feature])
                for dt in common_dates
            ]
            feature_rows.append(
                {
                    "feature": feature,
                    "authority_minus_support_mean_gap": round(mean(diffs), 6),
                    "authority_win_rate": round(sum(value > 0 for value in diffs) / len(diffs), 6),
                }
            )

        for dt in common_dates:
            authority_row = by_symbol[self.AUTHORITY][dt]
            support_row = by_symbol[self.SUPPORT][dt]
            authority_composite = sum(float(authority_row[feature]) for feature in FEATURES) / len(FEATURES)
            support_composite = sum(float(support_row[feature]) for feature in FEATURES) / len(FEATURES)
            composite_rows.append(
                {
                    "trade_date": dt,
                    "authority_composite": round(authority_composite, 6),
                    "support_composite": round(support_composite, 6),
                    "authority_minus_support_composite_gap": round(authority_composite - support_composite, 6),
                }
            )

        composite_rows_sorted = sorted(
            composite_rows,
            key=lambda row: row["authority_minus_support_composite_gap"],
        )

        authority_win_rate = sum(row["authority_minus_support_composite_gap"] > 0 for row in composite_rows) / len(composite_rows)
        support_role_flip_count = sum(row["authority_minus_support_composite_gap"] <= 0 for row in composite_rows)

        summary = {
            "acceptance_posture": "freeze_v129w_bk0480_aerospace_aviation_control_seed_audit_v1",
            "board_name": control_seed["summary"]["board_name"],
            "sector_id": control_seed["summary"]["sector_id"],
            "overlap_date_count": len(common_dates),
            "authority_overlap_composite_win_rate": round(authority_win_rate, 6),
            "support_role_flip_count": support_role_flip_count,
            "authority_expected_upside_mean_gap": next(
                row["authority_minus_support_mean_gap"] for row in feature_rows if row["feature"] == "expected_upside"
            ),
            "authority_non_junk_mean_gap": next(
                row["authority_minus_support_mean_gap"] for row in feature_rows if row["feature"] == "non_junk_composite_score"
            ),
            "support_stability_advantage": round(
                -next(row["authority_minus_support_mean_gap"] for row in feature_rows if row["feature"] == "stability"),
                6,
            ),
            "authoritative_rule": "bk0480_dual_core_control_seed_is_coherent_enough_for_kickoff_but_too_unstable_for_replay_unlock",
            "recommended_next_posture": "expand_locally_around_the_dual_core_and_audit_date_conditioned_authority_handoffs_before_replay",
        }
        overlap_extreme_rows = [
            {
                "bucket": "authority_best_dates",
                "rows": composite_rows_sorted[-3:][::-1],
            },
            {
                "bucket": "support_flip_dates",
                "rows": composite_rows_sorted[:3],
            },
        ]
        interpretation = [
            "V1.29W audits whether the minimal BK0480 dual-core control seed is economically coherent on overlapping dates.",
            "000738 wins often enough to stay the initial authority, but 600118 flips the ranking on a material minority of overlap dates, so replay should remain blocked.",
        ]
        return V129WBK0480AerospaceAviationControlSeedAuditReport(
            summary=summary,
            overlap_feature_rows=feature_rows,
            overlap_extreme_rows=overlap_extreme_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129WBK0480AerospaceAviationControlSeedAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129WBK0480AerospaceAviationControlSeedAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129w_bk0480_aerospace_aviation_control_seed_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
