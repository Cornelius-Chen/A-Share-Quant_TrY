from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CILaserMaturationProbeReport:
    summary: dict[str, Any]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CILaserMaturationProbeAnalyzer:
    LASER_ROLE = "laser_chip_component"
    PACKAGING_ROLE = "packaging_process_enabler"
    FEATURES = [
        "core_branch_relative_strength_spread_state",
        "core_spillover_divergence_state",
        "spillover_saturation_overlay_state",
        "ai_hardware_cross_board_resonance_state",
    ]

    def analyze(
        self,
        *,
        by_payload: dict[str, Any],
        bp_payload: dict[str, Any],
        ch_payload: dict[str, Any],
    ) -> V112CILaserMaturationProbeReport:
        if int(ch_payload.get("summary", {}).get("eligibility_only_cluster_member_count", 0)) != 1:
            raise ValueError("V1.12CI expects the frozen packaging mainline template state from V1.12CH.")

        gate_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in list(bp_payload.get("gate_decision_rows", []))
            if str(row.get("symbol")) in {"688498", "300757"}
        }
        packaging_rows = [
            row for row in list(by_payload.get("sample_rows", [])) if str(row.get("role_family")) == self.PACKAGING_ROLE
        ]
        laser_rows = [
            row for row in list(by_payload.get("sample_rows", [])) if str(row.get("role_family")) == self.LASER_ROLE
        ]
        if not packaging_rows or not laser_rows:
            raise ValueError("V1.12CI requires both packaging and laser sample rows from V1.12BY.")

        packaging_vectors = []
        for row in packaging_rows:
            key = (str(row["trade_date"]), str(row["symbol"]))
            gate_row = gate_rows[key]
            packaging_vectors.append(
                {
                    "trade_date": key[0],
                    "actual_band": str(row["actual_band"]),
                    "vector": [float(gate_row[name]) for name in self.FEATURES],
                }
            )

        sample_rows = []
        fringe_watch_count = 0
        clean_eligibility_count = 0
        for row in laser_rows:
            key = (str(row["trade_date"]), str(row["symbol"]))
            gate_row = gate_rows[key]
            vector = [float(gate_row[name]) for name in self.FEATURES]
            distances = []
            for p in packaging_vectors:
                dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector, p["vector"], strict=True)))
                distances.append((dist, p["trade_date"], p["actual_band"]))
            distances.sort(key=lambda item: item[0])
            nearest = distances[0]
            nearest_eligibility = next((item for item in distances if item[2] == "eligibility_band"), None)
            nearest_non_eligibility = next((item for item in distances if item[2] != "eligibility_band"), None)

            if (
                nearest_non_eligibility is not None
                and nearest_non_eligibility[0] < 0.25
                and (nearest_eligibility is None or nearest_non_eligibility[0] < nearest_eligibility[0])
            ):
                maturation_reading = "de_risk_fringe_watch"
                fringe_watch_count += 1
            else:
                maturation_reading = "clean_eligibility_member"
                clean_eligibility_count += 1

            sample_rows.append(
                {
                    "trade_date": key[0],
                    "symbol": key[1],
                    "actual_band": str(row["actual_band"]),
                    "nearest_packaging_band": str(nearest[2]),
                    "nearest_packaging_distance": round(float(nearest[0]), 4),
                    "nearest_eligibility_distance": round(float(nearest_eligibility[0]), 4) if nearest_eligibility is not None else None,
                    "nearest_non_eligibility_distance": round(float(nearest_non_eligibility[0]), 4) if nearest_non_eligibility is not None else None,
                    "maturation_reading": maturation_reading,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112ci_laser_maturation_probe_v1",
            "sample_count": len(sample_rows),
            "clean_eligibility_count": clean_eligibility_count,
            "de_risk_fringe_watch_count": fringe_watch_count,
            "promote_de_risk_now": False,
            "recommended_next_posture": "keep_laser_as_eligibility_only_member_with_fringe_watch_overlay",
        }
        interpretation = [
            "V1.12CI checks whether laser-chip states are still clean eligibility members or are beginning to migrate toward packaging-like de-risk/veto regions.",
            "The expected result is not immediate promotion, but a controlled maturity reading that preserves the frozen packaging mainline template boundary.",
        ]
        return V112CILaserMaturationProbeReport(
            summary=summary,
            sample_rows=sample_rows,
            interpretation=interpretation,
        )


def write_v112ci_laser_maturation_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CILaserMaturationProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
