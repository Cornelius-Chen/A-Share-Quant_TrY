from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config


@dataclass(slots=True)
class V12V6RefreshManifestReport:
    summary: dict[str, Any]
    manifest_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "manifest_rows": self.manifest_rows,
            "interpretation": self.interpretation,
        }


def _load_symbol_file(path: Path) -> list[str]:
    symbols: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#"):
            continue
        symbols.append(candidate)
    return symbols


class V12V6RefreshManifestAnalyzer:
    """Audit whether the v6 refresh manifest obeys catalyst-supported carry/persistence criteria."""

    def analyze(
        self,
        *,
        reference_base_symbols: list[str],
        seed_universe_symbols: list[str],
        manifest_entries: list[dict[str, Any]],
        required_targets: list[str],
    ) -> V12V6RefreshManifestReport:
        base_set = set(reference_base_symbols)
        seed_set = set(seed_universe_symbols)
        manifest_symbols = {str(entry["symbol"]) for entry in manifest_entries}

        missing_from_seed = sorted(manifest_symbols - seed_set)
        missing_from_manifest = sorted(seed_set - manifest_symbols)
        overlap_with_base = sorted(seed_set & base_set)

        target_counts: dict[str, int] = {}
        missing_hypothesis_count = 0
        opening_clone_primary_count = 0
        invalid_reason_count = 0
        missing_catalyst_support_count = 0
        invalid_catalyst_mode_count = 0
        manifest_rows: list[dict[str, Any]] = []
        allowed_catalyst_modes = {"policy_followthrough", "multi_day_reinforcement"}

        for entry in manifest_entries:
            symbol = str(entry["symbol"])
            target = str(entry["target_training_gap"])
            hypothesis = str(entry.get("row_hypothesis", "")).strip()
            primary_reason = str(entry.get("primary_admission_reason", "")).strip()
            catalyst_support_hypothesis = str(entry.get("catalyst_support_hypothesis", "")).strip()
            catalyst_context_mode = str(entry.get("catalyst_context_mode", "")).strip()
            target_counts[target] = target_counts.get(target, 0) + 1

            if not hypothesis:
                missing_hypothesis_count += 1
            if primary_reason == "opening_led_clone":
                opening_clone_primary_count += 1
            if primary_reason not in {"true_carry_row", "clean_persistence_row"}:
                invalid_reason_count += 1
            if not catalyst_support_hypothesis:
                missing_catalyst_support_count += 1
            if catalyst_context_mode not in allowed_catalyst_modes:
                invalid_catalyst_mode_count += 1

            manifest_rows.append(
                {
                    "symbol": symbol,
                    "target_training_gap": target,
                    "primary_admission_reason": primary_reason,
                    "row_hypothesis": hypothesis,
                    "catalyst_support_hypothesis": catalyst_support_hypothesis,
                    "catalyst_context_mode": catalyst_context_mode,
                    "is_new_vs_reference_base": symbol not in base_set,
                }
            )

        missing_targets = [
            target
            for target in required_targets
            if target_counts.get(target, 0) == 0
        ]

        ready_to_bootstrap = (
            not missing_from_seed
            and not missing_from_manifest
            and not overlap_with_base
            and not missing_targets
            and missing_hypothesis_count == 0
            and opening_clone_primary_count == 0
            and invalid_reason_count == 0
            and missing_catalyst_support_count == 0
            and invalid_catalyst_mode_count == 0
        )

        summary = {
            "reference_base_count": len(base_set),
            "seed_universe_count": len(seed_set),
            "manifest_entry_count": len(manifest_entries),
            "new_symbol_count": len([symbol for symbol in seed_set if symbol not in base_set]),
            "overlap_with_reference_base_count": len(overlap_with_base),
            "missing_from_seed_count": len(missing_from_seed),
            "missing_from_manifest_count": len(missing_from_manifest),
            "missing_target_count": len(missing_targets),
            "missing_hypothesis_count": missing_hypothesis_count,
            "opening_clone_primary_count": opening_clone_primary_count,
            "invalid_primary_reason_count": invalid_reason_count,
            "missing_catalyst_support_count": missing_catalyst_support_count,
            "invalid_catalyst_mode_count": invalid_catalyst_mode_count,
            "target_counts": target_counts,
            "ready_to_bootstrap_market_research_v6_catalyst_supported_carry_persistence_refresh": ready_to_bootstrap,
        }
        interpretation = [
            "The v6 refresh manifest should satisfy the frozen training-gap criteria while using catalyst context only as a bounded support layer.",
            "That means every symbol must stay new versus the combined reference base, enter with an explicit true-carry or clean-persistence hypothesis, and include a bounded catalyst-support hypothesis.",
            "Pure opening-led clone logic is still not an acceptable primary admission reason for this v6 refresh.",
        ]
        return V12V6RefreshManifestReport(
            summary=summary,
            manifest_rows=manifest_rows,
            interpretation=interpretation,
        )


def write_v12_v6_refresh_manifest_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V6RefreshManifestReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def load_manifest_config(
    path: Path,
) -> tuple[list[str], list[str], list[dict[str, Any]], list[str]]:
    payload = load_yaml_config(path)
    paths = dict(payload["paths"])
    manifest_entries = list(payload["manifest"]["entries"])
    required_targets = list(payload["manifest"]["required_targets"])
    reference_base = _load_symbol_file(Path(paths["reference_base_file"]))
    seed_universe = _load_symbol_file(Path(paths["seed_universe_file"]))
    return reference_base, seed_universe, manifest_entries, required_targets
