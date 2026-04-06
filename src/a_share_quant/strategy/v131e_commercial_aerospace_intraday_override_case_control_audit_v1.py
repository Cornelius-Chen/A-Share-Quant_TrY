from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


@dataclass(slots=True)
class V131ECommercialAerospaceIntradayOverrideCaseControlAuditReport:
    summary: dict[str, Any]
    metric_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "metric_rows": self.metric_rows,
            "interpretation": self.interpretation,
        }


class V131ECommercialAerospaceIntradayOverrideCaseControlAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.supervision_report_path = (
            repo_root / "reports" / "analysis" / "v131d_commercial_aerospace_intraday_override_supervision_table_v1.json"
        )

    @staticmethod
    def _mean(rows: list[dict[str, Any]], key: str) -> float:
        if not rows:
            return 0.0
        return mean(float(row[key]) for row in rows)

    def analyze(self) -> V131ECommercialAerospaceIntradayOverrideCaseControlAuditReport:
        supervision = json.loads(self.supervision_report_path.read_text(encoding="utf-8"))
        rows = supervision["supervision_rows"]

        positives = [row for row in rows if row["supervision_label"] == "override_positive"]
        clean_controls = [row for row in rows if row["supervision_label"] == "clean_control"]
        reversal_watches = [row for row in rows if row["supervision_label"] == "reversal_watch"]

        metric_rows = []
        for metric in [
            "open_to_close_return",
            "close_location",
            "close_from_high",
            "forward_return_10",
            "max_adverse_return_10",
        ]:
            positive_mean = self._mean(positives, metric)
            clean_mean = self._mean(clean_controls, metric)
            reversal_mean = self._mean(reversal_watches, metric)
            metric_rows.append(
                {
                    "metric": metric,
                    "override_positive_mean": round(positive_mean, 8),
                    "clean_control_mean": round(clean_mean, 8),
                    "reversal_watch_mean": round(reversal_mean, 8),
                    "override_minus_clean": round(positive_mean - clean_mean, 8),
                    "override_minus_reversal": round(positive_mean - reversal_mean, 8),
                }
            )

        override_de_risk_share = (
            sum(1 for row in positives if row["signal_label_pg"] == "de_risk_target") / len(positives)
            if positives
            else 0.0
        )
        clean_de_risk_share = (
            sum(1 for row in clean_controls if row["signal_label_pg"] == "de_risk_target") / len(clean_controls)
            if clean_controls
            else 0.0
        )
        no_preopen_adverse_share = (
            sum(1 for row in positives if row["pre_open_event_status"] == "no_decisive_event") / len(positives)
            if positives
            else 0.0
        )

        summary = {
            "acceptance_posture": "freeze_v131e_commercial_aerospace_intraday_override_case_control_audit_v1",
            "override_positive_count": len(positives),
            "clean_control_count": len(clean_controls),
            "reversal_watch_count": len(reversal_watches),
            "override_signal_is_derisk_share": round(override_de_risk_share, 8),
            "clean_signal_is_derisk_share": round(clean_de_risk_share, 8),
            "override_no_preopen_adverse_share": round(no_preopen_adverse_share, 8),
            "open_to_close_separation": round(
                self._mean(positives, "open_to_close_return") - self._mean(clean_controls, "open_to_close_return"),
                8,
            ),
            "close_location_separation": round(
                self._mean(positives, "close_location") - self._mean(clean_controls, "close_location"),
                8,
            ),
            "forward_return_10_separation": round(
                self._mean(positives, "forward_return_10") - self._mean(clean_controls, "forward_return_10"),
                8,
            ),
            "authoritative_rule": "retain override positives as future intraday supervision seeds, but keep the whole construct outside lawful replay until minute-level point-in-time support exists",
        }
        interpretation = [
            "V1.31E checks whether the retained override positives are materially distinct from ordinary clean buy executions in the current primary replay.",
            "The goal is governance, not promotion: if the severe failures are clearly separable, they deserve to remain as dedicated future intraday-label seeds.",
        ]
        return V131ECommercialAerospaceIntradayOverrideCaseControlAuditReport(
            summary=summary,
            metric_rows=metric_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131ECommercialAerospaceIntradayOverrideCaseControlAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131ECommercialAerospaceIntradayOverrideCaseControlAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131e_commercial_aerospace_intraday_override_case_control_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
