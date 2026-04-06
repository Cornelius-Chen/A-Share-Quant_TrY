from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v132g_commercial_aerospace_local_1min_rule_candidate_audit_v1 import _predict_tier


def _symbol_to_archive_member(symbol: str) -> str:
    if symbol.startswith("6"):
        return f"sh{symbol}.csv"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}.csv"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}.csv"
    return f"{symbol}.csv"


@dataclass(slots=True)
class V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditReport:
    summary: dict[str, Any]
    evaluation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evaluation_rows": self.evaluation_rows,
            "interpretation": self.interpretation,
        }


class V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.supervision_report_path = (
            repo_root / "reports" / "analysis" / "v131d_commercial_aerospace_intraday_override_supervision_table_v1.json"
        )
        self.mild_watch_report_path = (
            repo_root / "reports" / "analysis" / "v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1.json"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_rule_false_positive_rows_v1.csv"
        )

    def analyze(self) -> V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditReport:
        supervision = json.loads(self.supervision_report_path.read_text(encoding="utf-8"))
        mild_watch = json.loads(self.mild_watch_report_path.read_text(encoding="utf-8"))

        mild_watch_keys = {
            (row["execution_trade_date"], row["symbol"], row["action"]) for row in mild_watch["retained_rows"]
        }

        evaluation_rows: list[dict[str, Any]] = []
        for row in supervision["supervision_rows"]:
            key = (row["execution_trade_date"], row["symbol"], row["action"])
            if row["supervision_label"] == "override_positive":
                target_tier = "severe_override_positive"
            elif row["supervision_label"] == "reversal_watch":
                target_tier = "reversal_watch"
            elif key in mild_watch_keys:
                target_tier = "mild_override_watch"
            else:
                target_tier = "none"

            trade_date = row["execution_trade_date"]
            symbol = row["symbol"]
            zip_path = self.monthly_root / f"{trade_date[:4]}-{trade_date[4:6]}" / f"{trade_date}_1min.zip"
            member_name = _symbol_to_archive_member(symbol)
            with zipfile.ZipFile(zip_path) as archive:
                with archive.open(member_name, "r") as member:
                    minute_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:61]

            base_open = float(minute_rows[0][3])
            closes = [float(r[4]) for r in minute_rows]
            highs = [float(r[5]) for r in minute_rows]
            lows = [float(r[6]) for r in minute_rows]

            close15 = closes[14]
            close30 = closes[29]
            close60 = closes[59]
            low15 = min(lows[:15])
            low60 = min(lows[:60])
            high15 = max(highs[:15])
            high60 = max(highs[:60])
            close_loc15 = 0.5 if high15 == low15 else (close15 - low15) / (high15 - low15)
            close_loc60 = 0.5 if high60 == low60 else (close60 - low60) / (high60 - low60)

            feature_row = {
                "open_to_close_return": float(row["open_to_close_return"]),
                "ret15": close15 / base_open - 1.0,
                "ret30": close30 / base_open - 1.0,
                "ret60": close60 / base_open - 1.0,
                "draw60": low60 / base_open - 1.0,
                "close_loc15": close_loc15,
                "close_loc60": close_loc60,
            }
            predicted_tier = _predict_tier(feature_row)
            matched = predicted_tier == target_tier if target_tier != "none" else predicted_tier == "unmatched"

            evaluation_rows.append(
                {
                    "signal_trade_date": row["signal_trade_date"],
                    "execution_trade_date": trade_date,
                    "symbol": symbol,
                    "action": row["action"],
                    "supervision_label": row["supervision_label"],
                    "target_tier": target_tier,
                    "predicted_tier": predicted_tier,
                    "matched": matched,
                    **{k: round(v, 8) for k, v in feature_row.items()},
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(evaluation_rows[0].keys()))
            writer.writeheader()
            writer.writerows(evaluation_rows)

        seed_rows = [row for row in evaluation_rows if row["target_tier"] != "none"]
        non_seed_flagged = [row for row in evaluation_rows if row["target_tier"] == "none" and row["predicted_tier"] != "unmatched"]
        clean_control_flagged = [
            row
            for row in non_seed_flagged
            if row["supervision_label"] == "clean_control"
        ]
        ambiguous_flagged = [
            row
            for row in non_seed_flagged
            if row["supervision_label"] == "ambiguous_non_override"
        ]
        mismatch_flagged = [
            row
            for row in non_seed_flagged
            if row["supervision_label"] == "mismatch_watch"
        ]

        summary = {
            "acceptance_posture": "freeze_v132i_commercial_aerospace_local_1min_rule_false_positive_audit_v1",
            "buy_execution_row_count": len(evaluation_rows),
            "seed_row_count": len(seed_rows),
            "seed_match_count": sum(1 for row in seed_rows if row["matched"]),
            "non_seed_flagged_count": len(non_seed_flagged),
            "clean_control_flagged_count": len(clean_control_flagged),
            "ambiguous_flagged_count": len(ambiguous_flagged),
            "mismatch_flagged_count": len(mismatch_flagged),
            "evaluation_rows_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the first local 1min tier rules are only worth expanding beyond the seed set if broader false positives stay bounded away from clean controls",
        }
        interpretation = [
            "V1.32I applies the local 1-minute seed rules to the full commercial-aerospace buy-execution surface.",
            "The governance question is whether the rules remain narrow outside the frozen six-row seed set, especially whether they intrude into clean controls.",
        ]
        return V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditReport(
            summary=summary,
            evaluation_rows=evaluation_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132i_commercial_aerospace_local_1min_rule_false_positive_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
