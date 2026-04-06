from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root / "reports" / "analysis" / "v134ej_commercial_aerospace_intraday_add_supervision_registry_v1.json"
        )

    def analyze(self) -> V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Report:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "build_v134ek_commercial_aerospace_ej_add_registry_direction_triage_v1",
            "authoritative_status": "retain_intraday_add_registry_bootstrap_and_shift_next_to_point_in_time_add_seed_feed",
            "registry_row_count": registry["summary"]["registry_row_count"],
            "seed_family_count": registry["summary"]["seed_family_count"],
            "authoritative_rule": "the first add frontier artifact should remain a registry bootstrap until point-in-time seed feeds exist",
        }
        triage_rows = [
            {
                "component": "allowed_add_seed",
                "status": "retain_as_positive_supervision",
                "rationale": "historical pre-lockout open/add executions form the first positive add candidate set",
            },
            {
                "component": "failed_add_seed",
                "status": "retain_as_negative_supervision",
                "rationale": "same-day intraday failure after add must remain explicit negative evidence for later add labeling",
            },
            {
                "component": "blocked_add_seed",
                "status": "retain_as_veto_supervision",
                "rationale": "board lockout remains an upstream add veto and should be visible inside the registry itself",
            },
        ]
        interpretation = [
            "V1.34EK turns the bootstrap registry into a direction judgment for the newly opened add frontier.",
            "The next justified step is point-in-time add seed feeds, not execution logic and not broad all-session expansion.",
        ]
        return V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134EKCommercialAerospaceEJAddRegistryDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ek_commercial_aerospace_ej_add_registry_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
