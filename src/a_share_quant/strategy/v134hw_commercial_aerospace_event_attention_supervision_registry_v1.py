from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Report:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


class V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_event_attention_supervision_registry_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        path = self.repo_root / relative_path
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_decisive_events(self) -> dict[str, dict[str, Any]]:
        path = (
            self.repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        rows: dict[str, dict[str, Any]] = {}
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows[row["registry_id"]] = row
        return rows

    @staticmethod
    def _trade_date_from_visible_ts(value: str) -> str:
        if not value:
            return ""
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d")

    def analyze(self) -> V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Report:
        decisive_events = self._load_decisive_events()
        named_counterexamples = self._load_json(
            "reports/analysis/v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1.json"
        )
        local_only = self._load_json(
            "reports/analysis/v134bk_commercial_aerospace_local_only_rebound_audit_v1.json"
        )
        concentration = self._load_json(
            "reports/analysis/v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1.json"
        )

        counterexample_by_symbol = {
            row["symbol"]: row for row in named_counterexamples["symbol_rows"]
        }

        event_seed_specs = [
            {
                "registry_id": "ca_source_010",
                "row_type": "event_seed",
                "supervision_label": "event_trigger_validity",
                "derived_state": "board_supportive_continuation_seed",
                "symbol": "603601",
                "display_name": "再升科技",
                "reasoning": "supply-chain validation became visible inside a board-positive continuation window rather than inside a lockout",
            },
            {
                "registry_id": "ca_source_001",
                "row_type": "event_seed",
                "supervision_label": "event_trigger_validity",
                "derived_state": "pre_turn_continuation_watch",
                "symbol": "",
                "display_name": "",
                "reasoning": "capital-mapping event arrived before the January turning point and is retained as an early continuation watch, not a later unlock authority",
            },
            {
                "registry_id": "ca_source_007",
                "row_type": "event_seed",
                "supervision_label": "event_trigger_validity",
                "derived_state": "turning_point_risk_seed",
                "symbol": "000547",
                "display_name": "航天发展",
                "reasoning": "theme-heat article became visible exactly at the decisive overheating and turning-point risk date",
            },
            {
                "registry_id": "ca_source_005",
                "row_type": "event_seed",
                "supervision_label": "event_trigger_validity",
                "derived_state": "lockout_misaligned_continuation_watch",
                "symbol": "",
                "display_name": "",
                "reasoning": "symbol-specific continuation logic appeared only after board lockout had already started, so it cannot be treated as board-supportive",
            },
            {
                "registry_id": "ca_source_009",
                "row_type": "event_seed",
                "supervision_label": "event_trigger_validity",
                "derived_state": "lockout_misaligned_continuation_watch",
                "symbol": "",
                "display_name": "",
                "reasoning": "supply-chain validation visible inside the lockout regime is still event-relevant but not board-validating",
            },
            {
                "registry_id": "ca_source_006",
                "row_type": "event_seed",
                "supervision_label": "event_trigger_validity",
                "derived_state": "raw_only_post_lockout_continuation_watch",
                "symbol": "",
                "display_name": "",
                "reasoning": "capital-mapping continuation theme exists after lockout end only in the raw-only window, before any legal board-state extension",
            },
        ]

        registry_rows: list[dict[str, Any]] = []
        for spec in event_seed_specs:
            event_row = decisive_events[spec["registry_id"]]
            trade_date = self._trade_date_from_visible_ts(event_row["system_visible_time"])
            registry_rows.append(
                {
                    "row_type": spec["row_type"],
                    "registry_id": spec["registry_id"],
                    "trade_date": trade_date,
                    "symbol": spec["symbol"],
                    "display_name": spec["display_name"],
                    "layer": "event_attention",
                    "supervision_label": spec["supervision_label"],
                    "derived_state": spec["derived_state"],
                    "source_name": event_row["source_name"],
                    "decisive_semantic": event_row["decisive_semantic"],
                    "system_visible_time": event_row["system_visible_time"],
                    "evidence": spec["reasoning"],
                    "authority_boundary": "supervision_only",
                }
            )

        anchor_counterexample = counterexample_by_symbol["000547"]
        anchor_trade_date = "20260113"
        registry_rows.extend(
            [
                {
                    "row_type": "symbol_role_seed",
                    "registry_id": "anchor_000547_20260113",
                    "trade_date": anchor_trade_date,
                    "symbol": "000547",
                    "display_name": "航天发展",
                    "layer": "event_attention",
                    "supervision_label": "attention_anchor",
                    "derived_state": "high_recognition_attention_anchor_seed",
                    "source_name": decisive_events["ca_source_007"]["source_name"],
                    "decisive_semantic": "turning_point_watch",
                    "system_visible_time": decisive_events["ca_source_007"]["system_visible_time"],
                    "evidence": "the decisive turning-point source explicitly names 航天发展 as a high-recognition emotional axis inside overheated theme conditions",
                    "authority_boundary": "supervision_only",
                },
                {
                    "row_type": "symbol_role_seed",
                    "registry_id": "decoy_000547_20260113",
                    "trade_date": anchor_trade_date,
                    "symbol": "000547",
                    "display_name": "航天发展",
                    "layer": "event_attention",
                    "supervision_label": "attention_decoy",
                    "derived_state": "anchor_without_board_restart_seed",
                    "source_name": "ca_source_007 + named_counterexample + local_only_rebound_guard",
                    "decisive_semantic": "turning_point_watch_plus_locked_board_weak_repair",
                    "system_visible_time": decisive_events["ca_source_007"]["system_visible_time"],
                    "evidence": "航天发展 acts as a visible attention anchor around the turning point, but later only repairs weakly, never clears prior peak, and never reopens board participation",
                    "authority_boundary": "supervision_only",
                },
            ]
        )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(registry_rows[0].keys()))
            writer.writeheader()
            writer.writerows(registry_rows)

        summary = {
            "acceptance_posture": "freeze_v134hw_commercial_aerospace_event_attention_supervision_registry_v1",
            "registry_row_count": len(registry_rows),
            "event_seed_count": sum(1 for row in registry_rows if row["row_type"] == "event_seed"),
            "symbol_role_seed_count": sum(1 for row in registry_rows if row["row_type"] == "symbol_role_seed"),
            "event_trigger_validity_count": sum(1 for row in registry_rows if row["supervision_label"] == "event_trigger_validity"),
            "attention_anchor_count": sum(1 for row in registry_rows if row["supervision_label"] == "attention_anchor"),
            "attention_decoy_count": sum(1 for row in registry_rows if row["supervision_label"] == "attention_decoy"),
            "local_only_rebound_seed_count": local_only["summary"]["local_only_rebound_seed_count"],
            "concentration_module_member_count": concentration["summary"]["module_member_count"],
            "anchor_symbol_post_lockout_peak_gap": anchor_counterexample["post_lockout_max_vs_pre_lockout_peak"],
            "registry_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the first event-attention supervision layer is now explicit: event trigger validity can be positive, misaligned, or raw-only, while 航天发展 is retained as the first hard attention-anchor and attention-decoy seed rather than being mistaken for board restart evidence",
        }
        interpretation = [
            "V1.34HW starts the event-attention layer conservatively: only evidence-hard event rows and the clearest role row are promoted.",
            "This registry does not claim a full causal model of policy, attention, and capital. It only formalizes the first legal seeds so the next layer can grow without pretending incomplete information is complete.",
        ]
        return V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Report(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hw_commercial_aerospace_event_attention_supervision_registry_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
