from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditReport:
    summary: dict[str, Any]
    retained_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_rows": self.retained_rows,
            "interpretation": self.interpretation,
        }


class V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.coverage_report_path = (
            repo_root / "reports" / "analysis" / "v131u_commercial_aerospace_local_5min_override_coverage_audit_v1.json"
        )

    @staticmethod
    def _safe_float(value: Any) -> float:
        return float(value) if value not in ("", None) else 0.0

    def analyze(self) -> V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditReport:
        coverage = json.loads(self.coverage_report_path.read_text(encoding="utf-8"))
        rows = coverage["flagged_non_override_rows"]

        retained_rows: list[dict[str, Any]] = []
        for row in rows:
            ret60 = self._safe_float(row["ret60"])
            draw60 = self._safe_float(row["draw60"])
            close_loc60 = self._safe_float(row["close_loc60"])

            mild_override_like = ret60 <= -0.045 and draw60 <= -0.045 and close_loc60 <= 0.05
            retained_rows.append(
                {
                    **row,
                    "mild_override_like": mild_override_like,
                    "retention_decision": (
                        "retain_as_mild_override_watch" if mild_override_like else "keep_as_documented_false_positive"
                    ),
                }
            )

        retained_count = sum(1 for row in retained_rows if row["mild_override_like"])
        summary = {
            "acceptance_posture": "freeze_v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1",
            "flagged_non_override_case_count": len(retained_rows),
            "mild_override_watch_count": retained_count,
            "documented_false_positive_count": len(retained_rows) - retained_count,
            "authoritative_rule": "flagged ambiguous cases should be promoted only when they look like mild intraday override watches, otherwise they remain documented false-positive boundary cases",
        }
        interpretation = [
            "V1.31W inspects the two residual non-override hits from the local 5-minute prototype.",
            "The goal is to decide whether they are merely bounded false positives or whether they deserve to be retained as mild override-watch seeds for later minute-level work.",
        ]
        return V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditReport(
            summary=summary,
            retained_rows=retained_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
