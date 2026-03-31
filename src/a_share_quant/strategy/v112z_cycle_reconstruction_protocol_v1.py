from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ZCycleReconstructionProtocolReport:
    summary: dict[str, Any]
    protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol": self.protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ZCycleReconstructionProtocolAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        readiness_payload: dict[str, Any],
        adjacent_probe_payload: dict[str, Any],
        spillover_probe_payload: dict[str, Any],
    ) -> V112ZCycleReconstructionProtocolReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112z_now")):
            raise ValueError("V1.12Z must be open before protocol freeze.")

        readiness_summary = dict(readiness_payload.get("summary", {}))
        if not bool(readiness_summary.get("foundation_is_complete_enough_for_bounded_research")):
            raise ValueError("V1.12Z requires bounded research readiness from V1.12U.")

        adjacent_summary = dict(adjacent_probe_payload.get("summary", {}))
        spillover_summary = dict(spillover_probe_payload.get("summary", {}))

        protocol = {
            "cycle_scope": "single optical-link price-and-demand cycle only",
            "core_inputs": [
                "registry schema and feature slots from V112Q",
                "validated review assets from V112R",
                "chronology grammar from V112S",
                "spillover buckets from V112T and V112X",
                "adjacent split-ready review assets from V112Y",
            ],
            "required reconstruction layers": [
                "stage ordering",
                "catalyst ordering",
                "core/adjacent/branch role transitions",
                "board chronology overlays",
                "spillover and weak-memory overlays",
            ],
            "must_preserve_ambiguity_checks": [
                "mixed-role entities must remain visible as ambiguity checks",
                "spillover candidates must be tracked separately from core roles",
                "residual pending rows must not be silently dropped",
            ],
            "output_posture": [
                "review_only_reconstructed_cycle_map",
                "review_only_residual_gap_exposure",
                "owner_facing_reconstruction_summary",
            ],
            "forbidden_slides": [
                "auto training",
                "auto labeling freeze",
                "auto signal logic",
                "automatic feature promotion",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v112z_cycle_reconstruction_protocol_v1",
            "foundation_ready_for_bounded_cycle_reconstruction": True,
            "split_ready_adjacent_asset_count": adjacent_summary.get("split_ready_review_asset_count"),
            "bounded_spillover_factor_candidate_count": spillover_summary.get("bounded_spillover_factor_candidate_count"),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12Z freezes a reconstruction protocol rather than jumping straight into reconstructed truth.",
            "The protocol explicitly keeps mixed-role and spillover ambiguity alive so the experiment can expose problems instead of hiding them.",
            "The next lawful action after this is the actual bounded reconstruction pass.",
        ]
        return V112ZCycleReconstructionProtocolReport(summary=summary, protocol=protocol, interpretation=interpretation)


def write_v112z_cycle_reconstruction_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ZCycleReconstructionProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
