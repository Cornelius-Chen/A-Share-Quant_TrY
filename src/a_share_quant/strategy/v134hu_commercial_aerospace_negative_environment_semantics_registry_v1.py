from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Report:
    summary: dict[str, Any]
    semantic_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "semantic_rows": self.semantic_rows,
            "interpretation": self.interpretation,
        }


class V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_negative_environment_semantics_registry_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        path = self.repo_root / relative_path
        return json.loads(path.read_text(encoding="utf-8"))

    def analyze(self) -> V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Report:
        local_only = self._load_json(
            "reports/analysis/v134bk_commercial_aerospace_local_only_rebound_audit_v1.json"
        )
        expectancy = self._load_json(
            "reports/analysis/v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        )
        crowding = self._load_json(
            "reports/analysis/v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1.json"
        )
        concentration = self._load_json(
            "reports/analysis/v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1.json"
        )

        semantic_rows = [
            {
                "semantic_name": "attention_distorted",
                "phase_status": "promote_as_next_main_supervision_target",
                "seed_family": "crowding_like_shelter_rebound_plus_board_weak_symbol_strong_concentration",
                "seed_count": concentration["summary"]["module_member_count"],
                "supporting_count": crowding["summary"]["crowding_like_shelter_rebound_count"],
                "core_evidence": "few symbols can run near or through prior highs on heavy turnover while board unlock remains absent",
                "current_scope": "board_local_negative_semantics",
                "known_gap": "true attention proxies and heat-board divergence labels are not yet explicit",
                "promotion_boundary": "supervision_only",
            },
            {
                "semantic_name": "capital_misaligned_with_board",
                "phase_status": "promote_as_next_main_supervision_target",
                "seed_family": "local_only_rebound_watch",
                "seed_count": local_only["summary"]["local_only_rebound_seed_count"],
                "supporting_count": expectancy["summary"]["false_bounce_only_count"],
                "core_evidence": "top symbol forward strength can be high while probe/full breadth remains weak and board drawdown remains deep",
                "current_scope": "board_local_negative_semantics",
                "known_gap": "symbol-level concentration is visible, but event/catalyst source of the concentration is not yet bound",
                "promotion_boundary": "supervision_only",
            },
            {
                "semantic_name": "board_fragile_divergence",
                "phase_status": "promote_as_next_main_supervision_target",
                "seed_family": "false_bounce_only_plus_lockout_worthy",
                "seed_count": expectancy["summary"]["false_bounce_only_count"],
                "supporting_count": expectancy["summary"]["lockout_worthy_count"],
                "core_evidence": "board can show local rebound or continuation heat while forward expectancy remains poor and lockout stays justified",
                "current_scope": "board_local_negative_semantics",
                "known_gap": "external environment and policy/news pressure are not yet part of the semantic state",
                "promotion_boundary": "supervision_only",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(semantic_rows[0].keys()))
            writer.writeheader()
            writer.writerows(semantic_rows)

        summary = {
            "acceptance_posture": "freeze_v134hu_commercial_aerospace_negative_environment_semantics_registry_v1",
            "semantic_count": len(semantic_rows),
            "primary_semantics_ready_count": sum(
                1 for row in semantic_rows if row["phase_status"] == "promote_as_next_main_supervision_target"
            ),
            "local_only_rebound_seed_count": local_only["summary"]["local_only_rebound_seed_count"],
            "false_bounce_only_count": expectancy["summary"]["false_bounce_only_count"],
            "lockout_worthy_count": expectancy["summary"]["lockout_worthy_count"],
            "concentration_module_member_count": concentration["summary"]["module_member_count"],
            "registry_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the first environment-level supervision layer is now explicit: attention distortion, capital misalignment with the board, and board fragile divergence are retained as the next primary negative semantics, but they remain board-local and intentionally incomplete until the later event-attention layer is built",
        }
        interpretation = [
            "V1.34HU lifts the local negative-label families into three environment-level negative semantics rather than inventing more action rules.",
            "The registry is deliberately incomplete in one sense: it keeps the semantics board-local and records what is still missing, so incomplete information does not silently become false certainty.",
        ]
        return V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Report(
            summary=summary,
            semantic_rows=semantic_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hu_commercial_aerospace_negative_environment_semantics_registry_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
