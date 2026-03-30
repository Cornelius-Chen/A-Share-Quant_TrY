from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_REFRESH_TRIGGER_TYPES = (
    "archetype_gap",
    "new_suspect",
    "specialist_geography_shift",
    "clean_frontier_break",
    "secondary_status_break",
    "policy_override",
)


@dataclass(slots=True)
class RefreshTriggerIntakeRecord:
    summary: dict[str, Any]
    evidence: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence": self.evidence,
            "interpretation": self.interpretation,
        }


class RefreshTriggerIntakeBuilder:
    """Normalize a future trigger signal into a persistent intake artifact."""

    def build(
        self,
        *,
        trigger_name: str,
        source: str,
        rationale: str,
        trigger_type: str,
        datasets: list[str],
        symbols: list[str],
        slices: list[str],
    ) -> RefreshTriggerIntakeRecord:
        normalized_trigger_type = trigger_type.strip()
        if normalized_trigger_type not in ALLOWED_REFRESH_TRIGGER_TYPES:
            allowed = ", ".join(ALLOWED_REFRESH_TRIGGER_TYPES)
            raise ValueError(
                f"Unsupported trigger_type '{normalized_trigger_type}'. "
                f"Allowed values: {allowed}."
            )

        normalized_datasets = sorted({item.strip() for item in datasets if item.strip()})
        normalized_symbols = sorted({item.strip() for item in symbols if item.strip()})
        normalized_slices = sorted({item.strip() for item in slices if item.strip()})

        summary = {
            "trigger_name": trigger_name.strip(),
            "trigger_type": normalized_trigger_type,
            "source": source.strip(),
            "dataset_count": len(normalized_datasets),
            "symbol_count": len(normalized_symbols),
            "slice_count": len(normalized_slices),
            "recommended_next_step": "rerun_phase_guard_after_persisting_new_signal",
        }
        evidence = [
            {
                "evidence_name": "signal_origin",
                "actual": {
                    "source": source.strip(),
                    "rationale": rationale.strip(),
                },
                "reading": "This records where the potential refresh signal came from and why it may matter.",
            },
            {
                "evidence_name": "affected_scope",
                "actual": {
                    "datasets": normalized_datasets,
                    "symbols": normalized_symbols,
                    "slices": normalized_slices,
                },
                "reading": "This records which datasets, symbols, or slices are suspected to have changed the current waiting-state reading.",
            },
        ]
        interpretation = [
            "This artifact does not open refresh by itself.",
            "It is the canonical intake record for a newly observed signal before rerunning the guard stack.",
            "After writing this record, the next safe command remains `python scripts/run_phase_guard.py`.",
        ]
        return RefreshTriggerIntakeRecord(
            summary=summary,
            evidence=evidence,
            interpretation=interpretation,
        )


def write_refresh_trigger_intake(
    *,
    reports_dir: Path,
    report_name: str,
    record: RefreshTriggerIntakeRecord,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(record.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
