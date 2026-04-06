from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131ZCommercialAerospaceYZIntradayRegistryTriageReport:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V131ZCommercialAerospaceYZIntradayRegistryTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_report_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )

    def analyze(self) -> V131ZCommercialAerospaceYZIntradayRegistryTriageReport:
        registry = json.loads(self.registry_report_path.read_text(encoding="utf-8"))
        summary = registry["summary"]

        status = "freeze_commercial_aerospace_intraday_supervision_registry_and_shift_next_to_minute_tiered_label_specification"
        triage_rows = [
            {
                "component": "intraday_supervision_registry",
                "status": status,
                "rationale": "the registry is now the canonical seed object for future minute-level work because it preserves severity tiers and governance lineage",
            },
            {
                "component": "lawful_eod_primary",
                "status": "retain_unchanged",
                "rationale": "the new registry still serves supervision only and does not authorize replay contamination",
            },
        ]
        interpretation = [
            "V1.31Z converts the new intraday supervision registry into a next-step governance direction.",
            "The correct next move is minute-tiered label specification, not direct replay modification.",
        ]
        return V131ZCommercialAerospaceYZIntradayRegistryTriageReport(
            summary={
                "acceptance_posture": "freeze_v131z_commercial_aerospace_yz_intraday_registry_triage_v1",
                "authoritative_status": status,
                "registry_row_count": summary["registry_row_count"],
                "severe_override_positive_count": summary["severe_override_positive_count"],
                "reversal_watch_count": summary["reversal_watch_count"],
                "mild_override_watch_count": summary["mild_override_watch_count"],
                "authoritative_rule": "the commercial-aerospace intraday branch should move next to minute-tiered label specification using the frozen supervision registry as the only canonical seed source",
            },
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131ZCommercialAerospaceYZIntradayRegistryTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131ZCommercialAerospaceYZIntradayRegistryTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131z_commercial_aerospace_yz_intraday_registry_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
