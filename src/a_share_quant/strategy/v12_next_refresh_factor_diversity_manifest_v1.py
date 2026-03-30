from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config


@dataclass(slots=True)
class V12NextRefreshFactorDiversityManifestReport:
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


class V12NextRefreshFactorDiversityManifestAnalyzer:
    """Audit whether the next V1.2 refresh manifest really targets row diversity."""

    def analyze(
        self,
        *,
        reference_base_symbols: list[str],
        seed_universe_symbols: list[str],
        manifest_entries: list[dict[str, Any]],
        required_targets: list[str],
    ) -> V12NextRefreshFactorDiversityManifestReport:
        base_set = set(reference_base_symbols)
        seed_set = set(seed_universe_symbols)
        manifest_symbols = {str(entry["symbol"]) for entry in manifest_entries}

        missing_from_seed = sorted(manifest_symbols - seed_set)
        missing_from_manifest = sorted(seed_set - manifest_symbols)
        overlap_with_base = sorted(seed_set & base_set)

        target_counts: dict[str, int] = {}
        manifest_rows: list[dict[str, Any]] = []
        for entry in manifest_entries:
            symbol = str(entry["symbol"])
            target = str(entry["target_row_diversity"])
            target_counts[target] = target_counts.get(target, 0) + 1
            manifest_rows.append(
                {
                    "symbol": symbol,
                    "target_row_diversity": target,
                    "rationale": str(entry.get("rationale", "")),
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
            "target_counts": target_counts,
            "ready_to_bootstrap_market_research_v3_factor_diversity_seed": ready_to_bootstrap,
        }
        interpretation = [
            "The next refresh manifest should solve carry row-diversity gaps, not generic sample-size gaps.",
            "A valid seed must add only new symbols versus the combined v1/v2 reference base while covering all four diversity targets.",
            "This gate should pass before any market_research_v3 factor-diversity bootstrap is attempted.",
        ]
        return V12NextRefreshFactorDiversityManifestReport(
            summary=summary,
            manifest_rows=manifest_rows,
            interpretation=interpretation,
        )


def write_v12_next_refresh_factor_diversity_manifest_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12NextRefreshFactorDiversityManifestReport,
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
