from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _is_positive_reduce(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "reduce_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("reduce_payoff_decay_vs_hold_proxy_3d"), default=999.0) < 0.0
    )


@dataclass(slots=True)
class V121NCpoReduceSideOutOfSetFalsePositiveAuditReport:
    summary: dict[str, Any]
    context_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "context_rows": self.context_rows,
            "interpretation": self.interpretation,
        }


class V121NCpoReduceSideOutOfSetFalsePositiveAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _joined_rows(self) -> list[dict[str, Any]]:
        base_rows = _load_csv_rows(
            self.repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv"
        )
        daily_basic_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_cpo_daily_basic_v1.csv"
            )
        }
        moneyflow_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv"
            )
        }
        rows: list[dict[str, Any]] = []
        for row in base_rows:
            key = (str(row["signal_trade_date"]).replace("-", ""), str(row["symbol"]))
            daily_basic = daily_basic_rows.get(key)
            moneyflow = moneyflow_rows.get(key)
            if daily_basic is None or moneyflow is None:
                continue
            merged = dict(row)
            merged["turnover_rate_f"] = _to_float(daily_basic.get("turnover_rate_f"))
            merged["volume_ratio"] = _to_float(daily_basic.get("volume_ratio"))
            rows.append(merged)
        return rows

    def analyze(self, *, v121j_payload: dict[str, Any]) -> V121NCpoReduceSideOutOfSetFalsePositiveAuditReport:
        rows = self._joined_rows()
        threshold = _to_float(v121j_payload["summary"]["best_threshold"])

        def score(row: dict[str, Any]) -> float:
            board_avg_return = _to_float(row.get("board_avg_return"))
            board_breadth = _to_float(row.get("board_breadth"))
            turnover_rate_f = _to_float(row.get("turnover_rate_f"))
            volume_ratio = _to_float(row.get("volume_ratio"))
            return -board_avg_return - board_breadth + 0.75 * turnover_rate_f + 0.5 * volume_ratio

        context_rows: list[dict[str, Any]] = []
        for context in ("reduce_vs_hold", "close_vs_hold", "add_vs_hold", "entry_vs_skip"):
            context_pool = [row for row in rows if str(row.get("action_context")) == context]
            if not context_pool:
                continue
            pass_count = sum(1 for row in context_pool if score(row) >= threshold)
            record: dict[str, Any] = {
                "action_context": context,
                "row_count": len(context_pool),
                "pass_count": pass_count,
                "pass_rate": round(pass_count / len(context_pool), 6),
            }
            if context == "reduce_vs_hold":
                positives = [row for row in context_pool if _is_positive_reduce(row)]
                positive_pass_count = sum(1 for row in positives if score(row) >= threshold)
                record["positive_row_count"] = len(positives)
                record["positive_pass_rate"] = round(positive_pass_count / len(positives), 6) if positives else 0.0
            context_rows.append(record)

        lookup = {row["action_context"]: row for row in context_rows}
        summary = {
            "acceptance_posture": "freeze_v121n_cpo_reduce_side_out_of_set_false_positive_audit_v1",
            "best_threshold": round(threshold, 6),
            "reduce_pass_rate": lookup["reduce_vs_hold"]["pass_rate"],
            "reduce_positive_pass_rate": lookup["reduce_vs_hold"].get("positive_pass_rate", 0.0),
            "add_leakage_rate": lookup.get("add_vs_hold", {}).get("pass_rate", 0.0),
            "entry_leakage_rate": lookup.get("entry_vs_skip", {}).get("pass_rate", 0.0),
            "close_leakage_rate": lookup.get("close_vs_hold", {}).get("pass_rate", 0.0),
            "recommended_next_posture": "send_reduce_side_symbol_holdout_and_leakage_audits_to_adversarial_review",
        }
        interpretation = [
            "V1.21N checks whether the new reduce-side branch leaks into other action contexts.",
            "A live reduce candidate should not silently become a generic risk flag that fires just as often on close, add, or entry surfaces.",
            "This is the direct analogue of the add-vs-entry leakage checks that killed earlier add-side lines.",
        ]
        return V121NCpoReduceSideOutOfSetFalsePositiveAuditReport(
            summary=summary,
            context_rows=context_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121NCpoReduceSideOutOfSetFalsePositiveAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121NCpoReduceSideOutOfSetFalsePositiveAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v121j_payload=json.loads((repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121n_cpo_reduce_side_out_of_set_false_positive_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
