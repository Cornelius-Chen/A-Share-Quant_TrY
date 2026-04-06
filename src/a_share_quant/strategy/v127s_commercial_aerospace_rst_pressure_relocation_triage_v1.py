from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V127SCommercialAerospaceRSTPressureRelocationTriageReport:
    summary: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interpretation": self.interpretation,
        }


class V127SCommercialAerospaceRSTPressureRelocationTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v127r_path = repo_root / "reports" / "analysis" / "v127r_commercial_aerospace_pressure_relocation_control_audit_v1.json"

    def analyze(self) -> V127SCommercialAerospaceRSTPressureRelocationTriageReport:
        payload = json.loads(self.v127r_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v127s_commercial_aerospace_rst_pressure_relocation_triage_v1",
            "reference_variant": payload["summary"]["reference_variant"],
            "best_variant": payload["summary"]["best_variant"],
            "best_variant_final_equity": payload["summary"]["best_variant_final_equity"],
            "best_variant_max_drawdown": payload["summary"]["best_variant_max_drawdown"],
            "authoritative_status": (
                "promote_pressure_relocation_fix"
                if payload["summary"]["best_variant"] != payload["summary"]["reference_variant"]
                else "blocked_keep_current_primary"
            ),
        }
        interpretation = [
            "V1.27S freezes the pressure-relocation branch after testing narrow preheat/impulse restraint variants.",
        ]
        return V127SCommercialAerospaceRSTPressureRelocationTriageReport(
            summary=summary,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V127SCommercialAerospaceRSTPressureRelocationTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V127SCommercialAerospaceRSTPressureRelocationTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v127s_commercial_aerospace_rst_pressure_relocation_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
