from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config


@dataclass(slots=True)
class NextSuspectBatchManifestReport:
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


class NextSuspectBatchManifestAnalyzer:
    """Audit whether a proposed next-batch seed matches the current design rule."""

    def analyze(
        self,
        *,
        base_universe_symbols: list[str],
        seed_universe_symbols: list[str],
        manifest_entries: list[dict[str, Any]],
        required_archetypes: list[str],
    ) -> NextSuspectBatchManifestReport:
        base_set = set(base_universe_symbols)
        seed_set = set(seed_universe_symbols)
        manifest_symbols = {str(entry["symbol"]) for entry in manifest_entries}

        missing_from_seed = sorted(manifest_symbols - seed_set)
        missing_from_manifest = sorted(seed_set - manifest_symbols)
        overlap_with_base = sorted(seed_set & base_set)

        archetype_counts: dict[str, int] = {}
        manifest_rows: list[dict[str, Any]] = []
        for entry in manifest_entries:
            symbol = str(entry["symbol"])
            archetype = str(entry["target_archetype"])
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
            manifest_rows.append(
                {
                    "symbol": symbol,
                    "target_archetype": archetype,
                    "rationale": str(entry.get("rationale", "")),
                    "is_new_vs_market_v1": symbol not in base_set,
                }
            )

        missing_archetypes = [
            archetype
            for archetype in required_archetypes
            if archetype_counts.get(archetype, 0) == 0
        ]
        ready_to_bootstrap = (
            not missing_from_seed
            and not missing_from_manifest
            and not overlap_with_base
            and not missing_archetypes
        )
        summary = {
            "base_universe_count": len(base_set),
            "seed_universe_count": len(seed_set),
            "manifest_entry_count": len(manifest_entries),
            "new_symbol_count": len([symbol for symbol in seed_set if symbol not in base_set]),
            "overlap_with_market_v1_count": len(overlap_with_base),
            "missing_from_seed_count": len(missing_from_seed),
            "missing_from_manifest_count": len(missing_from_manifest),
            "missing_archetype_count": len(missing_archetypes),
            "archetype_counts": archetype_counts,
            "ready_to_bootstrap_next_batch": ready_to_bootstrap,
        }
        interpretation = [
            "The next suspect batch should be designed, not just enlarged.",
            "A good seed manifest should add only new symbols versus market_research_v1 while explicitly covering the targeted missing archetypes.",
            "This audit is a design-quality gate before any free-data bootstrap is attempted.",
        ]
        return NextSuspectBatchManifestReport(
            summary=summary,
            manifest_rows=manifest_rows,
            interpretation=interpretation,
        )


def write_next_suspect_batch_manifest_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: NextSuspectBatchManifestReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def load_manifest_config(path: Path) -> tuple[list[str], list[str], list[dict[str, Any]], list[str]]:
    payload = load_yaml_config(path)
    paths = dict(payload["paths"])
    manifest_entries = list(payload["manifest"]["entries"])
    required_archetypes = list(payload["manifest"]["required_archetypes"])
    base_universe = _load_symbol_file(Path(paths["base_universe_file"]))
    seed_universe = _load_symbol_file(Path(paths["seed_universe_file"]))
    return base_universe, seed_universe, manifest_entries, required_archetypes
