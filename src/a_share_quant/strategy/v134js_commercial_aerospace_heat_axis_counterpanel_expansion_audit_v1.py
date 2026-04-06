from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Report:
    summary: dict[str, Any]
    expansion_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "expansion_rows": self.expansion_rows,
            "interpretation": self.interpretation,
        }


class V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        self.counterpanel_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134ig_commercial_aerospace_anchor_decoy_counterpanel_search_audit_v1.json"
        )
        self.source_hardness_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134ja_commercial_aerospace_event_attention_source_hardness_audit_v1.json"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_heat_axis_counterpanel_expansion_v1.csv"
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Report:
        registry_rows = self._load_csv(self.registry_path)
        counterpanel = self._load_json(self.counterpanel_path)
        source_hardness = self._load_json(self.source_hardness_path)

        heat_rows = [
            row
            for row in registry_rows
            if row["decisive_retained"] == "True"
            and row["decisive_reason"] in {"decisive_turning_point_risk", "sentiment_transition_anchor"}
        ]
        realized_heat_rows = [row for row in heat_rows if row["record_type"] == "historical_source"]
        forward_heat_rows = [row for row in heat_rows if row["record_type"] == "forward_anchor"]

        expansion_rows = [
            {
                "registry_id": row["registry_id"],
                "record_type": row["record_type"],
                "event_scope": row["event_scope"],
                "source_role": (
                    "realized_heat_axis_seed" if row["record_type"] == "historical_source" else "forward_heat_axis_anchor"
                ),
                "same_plane_usability": (
                    "same_plane_ready" if row["record_type"] == "historical_source" else "forward_only_not_same_plane"
                ),
                "counterpanel_expansion_utility": (
                    "reinforces_existing_singleton" if row["record_type"] == "historical_source" else "future_structure_only"
                ),
                "detail": row["source_name"],
            }
            for row in heat_rows
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(expansion_rows[0].keys()))
            writer.writeheader()
            writer.writerows(expansion_rows)

        summary = {
            "acceptance_posture": "freeze_v134js_commercial_aerospace_heat_axis_counterpanel_expansion_audit_v1",
            "retained_heat_axis_source_count": len(heat_rows),
            "realized_heat_axis_source_count": len(realized_heat_rows),
            "forward_heat_axis_anchor_count": len(forward_heat_rows),
            "current_hard_counterpanel_count": counterpanel["summary"]["current_hard_counterpanel_count"],
            "hard_anchor_grade_source_count": source_hardness["summary"]["hard_anchor_grade_source_count"],
            "counterpanel_thickened_now": False,
            "same_plane_counterpanel_expansion_ready_count": len(realized_heat_rows),
            "expansion_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_heat_axis_counterpanel_expansion_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JS checks whether the heat-axis branch can thicken the anchor/decoy counterpanel right now.",
            "It finds one realized same-plane heat-axis seed and one forward heat-axis anchor. That is enough to formalize the branch, but not enough to claim that the hard counterpanel is already thicker than a singleton.",
        ]
        return V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Report(
            summary=summary,
            expansion_rows=expansion_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134js_commercial_aerospace_heat_axis_counterpanel_expansion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
