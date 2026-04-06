from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129HCommercialAerospaceGHILatePreheatFilterTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "interpretation": self.interpretation}


class V129HCommercialAerospaceGHILatePreheatFilterTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.audit_path = repo_root / "reports" / "analysis" / "v129g_commercial_aerospace_late_preheat_full_filter_audit_v1.json"

    def analyze(self) -> V129HCommercialAerospaceGHILatePreheatFilterTriageReport:
        payload = json.loads(self.audit_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v129h_commercial_aerospace_ghi_late_preheat_filter_triage_v1",
            "reference_variant": payload["summary"]["reference_variant"],
            "best_variant": payload["summary"]["best_variant"],
            "best_variant_final_equity": payload["summary"]["best_variant_final_equity"],
            "best_variant_max_drawdown": payload["summary"]["best_variant_max_drawdown"],
            "authoritative_status": (
                "promote_late_preheat_filter"
                if payload["summary"]["best_variant"] != payload["summary"]["reference_variant"]
                else "keep_current_primary_and_retain_late_preheat_filter_as_supervision_only"
            ),
            "authoritative_rule": "late-preheat full-pre supervision should only enter replay if it improves the current primary frontier rather than merely cleaning one suspicious trade",
        }
        interpretation = [
            "V1.29H freezes whether late-preheat full-pre supervision is strong enough to modify the current commercial-aerospace primary replay.",
            "If it does not beat the current primary, it should remain as supervision/governance rather than replay-facing tuning.",
        ]
        return V129HCommercialAerospaceGHILatePreheatFilterTriageReport(summary=summary, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V129HCommercialAerospaceGHILatePreheatFilterTriageReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129HCommercialAerospaceGHILatePreheatFilterTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129h_commercial_aerospace_ghi_late_preheat_filter_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
