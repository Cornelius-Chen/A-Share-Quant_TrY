from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mq_a_share_replay_tradeable_context_binding_audit_v1 import (
    V134MQAShareReplayTradeableContextBindingAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MRAShareMQReplayTradeableBindingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MRAShareMQReplayTradeableBindingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MRAShareMQReplayTradeableBindingDirectionTriageV1Report:
        report = V134MQAShareReplayTradeableContextBindingAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "date_level_bound_count": report.summary["date_level_bound_count"],
            "missing_date_context_count": report.summary["missing_date_context_count"],
            "authoritative_status": (
                "replay_tradeable_context_bound_at_date_level_but_not_symbol_level"
                if report.summary["date_level_bound_count"] > 0
                else "replay_tradeable_context_coverage_gap_explicit_and_not_symbol_bound"
            ),
        }
        triage_rows = [
            {
                "component": "tradeable_context_binding",
                "direction": (
                    "freeze_date_level_binding_and_shift_next_to_symbol_level_mapping"
                    if report.summary["date_level_bound_count"] > 0
                    else "close_limit_halt_coverage_gap_before_symbol_level_mapping_attempts"
                ),
            },
            {
                "component": "missing_date_coverage",
                "direction": "close_shadow_slice_market_context_gaps_before_attempting_unified_tradeable_binding",
            },
        ]
        interpretation = [
            "Replay has an explicit coverage diagnosis rather than an implicit assumption about tradeable-state linkage.",
            "Because date-level binding did not materialize on the current coverage window, the next step is coverage expansion before symbol-level linkage.",
        ]
        return V134MRAShareMQReplayTradeableBindingDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MRAShareMQReplayTradeableBindingDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MRAShareMQReplayTradeableBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mr_a_share_mq_replay_tradeable_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
