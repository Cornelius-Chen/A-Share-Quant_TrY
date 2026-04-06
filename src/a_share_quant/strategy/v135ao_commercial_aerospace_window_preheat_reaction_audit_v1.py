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
class V135AOCommercialAerospaceWindowPreheatReactionAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AOCommercialAerospaceWindowPreheatReactionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.slice_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_preheat_reaction_slice_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_preheat_reaction_summary_v1.csv"
        )

    def analyze(self) -> V135AOCommercialAerospaceWindowPreheatReactionAuditV1Report:
        rows = _read_csv(self.slice_path)
        summary_rows = _read_csv(self.summary_path)
        if not rows or not summary_rows:
            raise FileNotFoundError("Window 007 preheat reaction outputs are missing.")
        summary = {
            "row_count": len(rows),
            "covered_window_count": len({row["sample_window_id"] for row in rows}),
            "formal_or_industrial_confirmation_count": sum(
                1
                for row in rows
                if row["structure_role"]
                in {"formal_core_confirmation", "seller_shovel_breakout", "seller_shovel_supportive_confirmation"}
            ),
            "emotion_confirmation_count": sum(
                1
                for row in rows
                if row["structure_role"] in {"emotion_mirror_leader", "high_recognition_emotion_confirmation"}
            ),
            "gate_hold_count": sum(
                1
                for row in summary_rows
                if row["final_training_admission"] == "positive_sample_ready_but_not_final_training"
            ),
        }
        interpretation = [
            "Window 007 is now evidence-backed as a policy-preheat window with real board confirmation and early-ignition characteristics.",
            "It should teach early policy-backed ignition formation rather than replace the cleaner January ignition archetype.",
            "This keeps 007 useful as a positive preheat sample while still preventing it from overruling window 002.",
        ]
        return V135AOCommercialAerospaceWindowPreheatReactionAuditV1Report(
            summary=summary,
            rows=summary_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AOCommercialAerospaceWindowPreheatReactionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AOCommercialAerospaceWindowPreheatReactionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ao_commercial_aerospace_window_preheat_reaction_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
