from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134AUCommercialAerospacePostExitReboundPatternAuditV1Report:
    summary: dict[str, Any]
    pattern_rows: list[dict[str, Any]]
    case_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "pattern_rows": self.pattern_rows,
            "case_rows": self.case_rows,
            "interpretation": self.interpretation,
        }


class V134AUCommercialAerospacePostExitReboundPatternAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.horizon_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_full_horizon_sanity_audit_v1.csv"
        )
        self.local_deferral_path = (
            repo_root / "reports" / "analysis" / "v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_post_exit_rebound_pattern_audit_v1.csv"
        )

    @staticmethod
    def _sign_label(value_raw: str) -> str:
        value = float(value_raw)
        if value > 0:
            return "pos"
        if value < 0:
            return "neg"
        return "flat"

    def analyze(self) -> V134AUCommercialAerospacePostExitReboundPatternAuditV1Report:
        with self.horizon_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            horizon_rows = list(csv.DictReader(handle))
        local_deferral = json.loads(self.local_deferral_path.read_text(encoding="utf-8"))
        excluded_keys = {(row["trade_date"], row["symbol"]) for row in local_deferral["impacted_rows"]}

        case_rows: list[dict[str, Any]] = []
        pattern_map: dict[str, list[dict[str, Any]]] = {}
        for row in horizon_rows:
            if row["horizon_pnl_5d"] == "":
                continue
            if (row["trade_date"], row["symbol"]) in excluded_keys:
                continue
            if float(row["horizon_pnl_5d"]) <= 0:
                continue

            pattern_key = (
                f"{self._sign_label(row['horizon_pnl_1d'])}_1d|"
                f"{self._sign_label(row['horizon_pnl_3d'])}_3d|"
                f"{self._sign_label(row['horizon_pnl_5d'])}_5d"
            )
            case = {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "month_bucket": row["month_bucket"],
                "reversal_minute": int(row["reversal_minute"]),
                "horizon_pnl_1d": float(row["horizon_pnl_1d"]),
                "horizon_pnl_3d": float(row["horizon_pnl_3d"]),
                "horizon_pnl_5d": float(row["horizon_pnl_5d"]),
                "pattern_key": pattern_key,
            }
            case_rows.append(case)
            pattern_map.setdefault(pattern_key, []).append(case)

        pattern_rows = [
            {
                "pattern_key": pattern_key,
                "case_count": len(rows),
                "symbols": "|".join(sorted({row["symbol"] for row in rows})),
                "trade_dates": "|".join(sorted(row["trade_date"] for row in rows)),
                "mean_horizon_pnl_1d": round(sum(row["horizon_pnl_1d"] for row in rows) / len(rows), 4),
                "mean_horizon_pnl_3d": round(sum(row["horizon_pnl_3d"] for row in rows) / len(rows), 4),
                "mean_horizon_pnl_5d": round(sum(row["horizon_pnl_5d"] for row in rows) / len(rows), 4),
            }
            for pattern_key, rows in sorted(pattern_map.items(), key=lambda item: (-len(item[1]), item[0]))
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(case_rows[0].keys()))
            writer.writeheader()
            writer.writerows(case_rows)

        dominant_pattern = pattern_rows[0]["pattern_key"] if pattern_rows else ""
        delayed_rebound_share = 0.0
        if case_rows:
            delayed_rebound_share = round(
                sum(1 for row in case_rows if row["horizon_pnl_1d"] < 0 and row["horizon_pnl_3d"] > 0) / len(case_rows),
                8,
            )

        summary = {
            "acceptance_posture": "freeze_v134au_commercial_aerospace_post_exit_rebound_pattern_audit_v1",
            "remaining_rebound_case_count": len(case_rows),
            "dominant_pattern": dominant_pattern,
            "dominant_pattern_case_count": pattern_rows[0]["case_count"] if pattern_rows else 0,
            "delayed_rebound_share": delayed_rebound_share,
            "case_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_post_exit_rebound_pattern_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AU asks whether the remaining rebound-cost cases after the local deferral fix are still sell-side errors or are actually post-exit re-entry gaps.",
            "A negative 1-day horizon with positive later horizons suggests the sell itself was valid but the branch lacks a later rebuild or re-entry supervision family.",
        ]
        return V134AUCommercialAerospacePostExitReboundPatternAuditV1Report(
            summary=summary,
            pattern_rows=pattern_rows,
            case_rows=case_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134AUCommercialAerospacePostExitReboundPatternAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134AUCommercialAerospacePostExitReboundPatternAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134au_commercial_aerospace_post_exit_rebound_pattern_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
