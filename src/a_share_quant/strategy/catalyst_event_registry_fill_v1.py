from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config


@dataclass(slots=True)
class CatalystEventRegistryFillReport:
    summary: dict[str, Any]
    fill_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "fill_rows": self.fill_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _load_mapping_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            continue
        loaded = False
        for encoding in ("utf-8-sig", "gb18030", "utf-8"):
            try:
                with path.open("r", encoding=encoding, newline="") as handle:
                    reader = csv.DictReader(handle)
                    rows.extend({str(key): str(value) for key, value in row.items()} for row in reader)
                loaded = True
                break
            except UnicodeDecodeError:
                continue
        if not loaded:
            raise UnicodeDecodeError("mapping_loader", b"", 0, 1, f"Could not decode mapping file: {path}")
    return rows


class CatalystEventRegistryFillAnalyzer:
    """Perform the first bounded fill using local market context mappings only."""

    def analyze(
        self,
        *,
        seed_payload: dict[str, Any],
        concept_mapping_rows: list[dict[str, str]],
        sector_mapping_rows: list[dict[str, str]],
    ) -> CatalystEventRegistryFillReport:
        fill_rows: list[dict[str, Any]] = []
        theme_count = 0
        sector_count = 0

        def _find_mapping(rows: list[dict[str, str]], symbol: str, trade_date: str) -> dict[str, str] | None:
            for row in rows:
                if row.get("symbol") == symbol and row.get("trade_date") == trade_date:
                    return row
            return None

        for seed_row in list(seed_payload.get("seed_rows", [])):
            symbol = str(seed_row.get("symbol", ""))
            trade_date = str(seed_row.get("event_date", ""))
            concept_match = _find_mapping(concept_mapping_rows, symbol, trade_date)
            sector_match = _find_mapping(sector_mapping_rows, symbol, trade_date)

            mapped_context_name = ""
            mapping_source = ""
            event_scope = "sector"
            board_pulse_breadth_class = "mapped_sector_present"

            if concept_match and concept_match.get("concept_name"):
                mapped_context_name = str(concept_match["concept_name"])
                mapping_source = str(concept_match.get("mapping_source", ""))
                event_scope = "theme"
                board_pulse_breadth_class = "mapped_theme_present"
                theme_count += 1
            elif sector_match and sector_match.get("sector_name"):
                mapped_context_name = str(sector_match["sector_name"])
                mapping_source = str(sector_match.get("mapping_source", ""))
                event_scope = "sector"
                board_pulse_breadth_class = "mapped_sector_present"
                sector_count += 1
            else:
                mapped_context_name = "unmapped"
                mapping_source = "none_found"
                board_pulse_breadth_class = "unmapped_context"

            label = str(seed_row.get("lane_outcome_label", ""))
            if label == "opening_led":
                event_type = "market_pulse"
            elif label == "persistence_led":
                event_type = "market_followthrough"
            else:
                event_type = "carry_context_candidate"

            fill_rows.append(
                {
                    **seed_row,
                    "event_scope": event_scope,
                    "event_type": event_type,
                    "source_authority_tier": "unverified_market_context",
                    "source_tier": "public_market_context",
                    "policy_scope": "unknown",
                    "execution_strength": "unknown",
                    "rumor_risk_level": "unknown",
                    "mapped_context_name": mapped_context_name,
                    "mapping_source": mapping_source,
                    "board_pulse_breadth_class": board_pulse_breadth_class,
                    "context_posture": "market_context_only_first_fill",
                }
            )

        summary = {
            "fill_posture": "open_catalyst_event_registry_fill_v1_as_market_context_only",
            "row_count": len(fill_rows),
            "theme_scope_count": theme_count,
            "sector_scope_count": sector_count,
            "unmapped_count": len([row for row in fill_rows if row["mapped_context_name"] == "unmapped"]),
            "official_source_filled_count": 0,
            "market_context_filled_count": len(fill_rows),
            "ready_for_manual_source_fill_next": len(fill_rows) > 0,
        }
        interpretation = [
            "The first bounded catalyst fill should begin with local market context, not a wide official-news scrape.",
            "This fill assigns theme-versus-sector scope and a mapped context name while leaving official source authority fields explicitly unresolved.",
            "The next catalyst step is manual or semi-manual source filling on top of this market-context base rather than premature modeling.",
        ]
        return CatalystEventRegistryFillReport(
            summary=summary,
            fill_rows=fill_rows,
            interpretation=interpretation,
        )


def write_catalyst_event_registry_fill_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CatalystEventRegistryFillReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def load_catalyst_event_registry_fill_config(
    path: Path,
) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]], Path, str]:
    payload = load_yaml_config(path)
    seed_payload = load_json_report(Path(payload["paths"]["seed_report"]))
    concept_mapping_rows = _load_mapping_rows([Path(p) for p in payload["paths"]["concept_mapping_files"]])
    sector_mapping_rows = _load_mapping_rows([Path(p) for p in payload["paths"]["sector_mapping_files"]])
    reports_dir = Path(payload["paths"]["reports_dir"])
    report_name = str(payload["report"]["name"])
    return seed_payload, concept_mapping_rows, sector_mapping_rows, reports_dir, report_name
