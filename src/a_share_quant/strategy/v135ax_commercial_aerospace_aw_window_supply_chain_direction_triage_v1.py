from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [{str(k).lstrip("\ufeff"): v for k, v in row.items()} for row in csv.DictReader(handle)]


@dataclass(slots=True)
class V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows}


class V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_supply_chain_seed_summary_v1.csv"
        )

    def analyze(self) -> V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Report:
        rows = _read_csv(self.summary_path)
        if not rows:
            raise FileNotFoundError(self.summary_path)
        triage_rows = [
            {
                "sample_window_id": row["sample_window_id"],
                "final_training_admission": row["final_training_admission"],
                "recommendation": "allow_positive_support_training_but_keep_below_primary_january_ignition_archetype",
            }
            for row in rows
        ]
        summary = {
            "window_count": len(rows),
            "positive_support_ready_count": sum(
                1 for row in rows if row["final_training_admission"] == "positive_support_sample_ready"
            ),
        }
        return V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ax_commercial_aerospace_aw_window_supply_chain_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
