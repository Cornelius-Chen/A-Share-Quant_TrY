from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v128s_commercial_aerospace_failure_library_bootstrap_v1 import (
    V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer,
)


@dataclass(slots=True)
class V128TCommercialAerospaceFailureLibraryTriageReport:
    summary: dict[str, Any]
    retained_rows: list[dict[str, Any]]
    blocked_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_rows": self.retained_rows,
            "blocked_rows": self.blocked_rows,
            "interpretation": self.interpretation,
        }


class V128TCommercialAerospaceFailureLibraryTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V128TCommercialAerospaceFailureLibraryTriageReport:
        bootstrap = V128SCommercialAerospaceFailureLibraryBootstrapAnalyzer(self.repo_root).analyze()
        retained_rows: list[dict[str, Any]] = []
        blocked_rows: list[dict[str, Any]] = []
        for row in bootstrap.failure_rows:
            if row["failure_type"] == "intraday_collapse_override_required":
                retained_rows.append(
                    {
                        "failure_id": row["failure_id"],
                        "symbol": row["symbol"],
                        "signal_trade_date": row["signal_trade_date"],
                        "execution_trade_date": row["execution_trade_date"],
                        "status": "retain_for_intraday_override_library",
                        "why": "lawful overnight buy but severe same-day collapse suggests missing intraday emergency-exit grammar rather than time leakage",
                    }
                )
            else:
                blocked_rows.append(
                    {
                        "failure_id": row["failure_id"],
                        "symbol": row["symbol"],
                        "status": "watch_only",
                        "why": "not severe or not clean enough to become the first authoritative intraday-override archetype",
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v128t_commercial_aerospace_failure_library_triage_v1",
            "failure_case_count": bootstrap.summary["failure_case_count"],
            "retained_intraday_override_case_count": len(retained_rows),
            "blocked_watch_only_case_count": len(blocked_rows),
            "next_direction": "use retained cases as supervision objects for future intraday collapse override grammar without contaminating current EOD lawful replay",
        }
        interpretation = [
            "V1.28T freezes the first commercial-aerospace failure-library triage.",
            "Retained cases do not become training labels yet; they become supervised governance objects for the later intraday emergency-exit layer.",
        ]
        return V128TCommercialAerospaceFailureLibraryTriageReport(
            summary=summary,
            retained_rows=retained_rows,
            blocked_rows=blocked_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128TCommercialAerospaceFailureLibraryTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128TCommercialAerospaceFailureLibraryTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128t_commercial_aerospace_failure_library_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
