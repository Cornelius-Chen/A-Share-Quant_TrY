from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113FPilotObjectPoolReport:
    summary: dict[str, Any]
    object_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "object_rows": self.object_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "gb18030", "utf-8"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                return [{str(key): str(value) for key, value in row.items()} for row in reader]
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv_loader", b"", 0, 1, f"Could not decode csv file: {path}")


class V113FPilotObjectPoolAnalyzer:
    """Freeze the first bounded object pool for the commercial-space theme-diffusion pilot."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_protocol_payload: dict[str, Any],
        sector_mapping_rows: list[dict[str, str]],
        security_master_rows: list[dict[str, str]],
        mainline_window_rows: list[dict[str, str]],
    ) -> V113FPilotObjectPoolReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        pilot_basis = dict(pilot_protocol_payload.get("pilot_basis", {}))
        if not bool(charter_summary.get("do_open_v113f_now")):
            raise ValueError("V1.13F must be open before pilot object pool freeze.")
        if pilot_basis.get("selected_archetype") != "commercial_space_mainline":
            raise ValueError("V1.13F only supports the commercial_space_mainline pilot.")

        commercial_rows = [
            row for row in sector_mapping_rows if row.get("sector_name") == "\u5546\u4e1a\u822a\u5929"
        ]
        if not commercial_rows:
            raise ValueError("Commercial-space local sector mapping rows are required.")

        security_master = {row.get("symbol", ""): row for row in security_master_rows}
        name_overrides = {
            "002085": "\u4e07\u4e30\u5965\u5a01",
            "000738": "\u822a\u53d1\u63a7\u5236",
            "600118": "\u4e2d\u56fd\u536b\u661f",
        }
        role_guess_overrides = {
            "002085": (
                "leader",
                "Dense commercial-space concept presence makes this the cleanest local mainline leader seed.",
            ),
            "600118": (
                "mid_core",
                "Policy and aerospace anchoring make this a plausible mid-core review seed despite sparse direct commercial-space mapping.",
            ),
            "000738": (
                "mapping_activation",
                "The symbol appears in commercial-space mapping intermittently and therefore reads more like a mapping activation draft than a clean core.",
            ),
        }
        evidence_status_overrides = {
            "002085": "dense_local_commercial_space_mapping",
            "600118": "sparse_policy_anchor_mapping",
            "000738": "sparse_cross_theme_mapping",
        }

        window_counts: dict[str, int] = {}
        for row in mainline_window_rows:
            symbol = row.get("symbol", "")
            if not symbol:
                continue
            window_counts[symbol] = window_counts.get(symbol, 0) + 1

        symbol_stats: dict[str, dict[str, Any]] = {}
        for row in commercial_rows:
            symbol = row.get("symbol", "")
            trade_date = row.get("trade_date", "")
            if not symbol or not trade_date:
                continue
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {
                    "symbol": symbol,
                    "commercial_space_mapping_days": 0,
                    "first_seen": trade_date,
                    "last_seen": trade_date,
                }
            stat = symbol_stats[symbol]
            stat["commercial_space_mapping_days"] += 1
            if trade_date < stat["first_seen"]:
                stat["first_seen"] = trade_date
            if trade_date > stat["last_seen"]:
                stat["last_seen"] = trade_date

        ranked_symbols = sorted(
            symbol_stats.values(),
            key=lambda row: (-int(row["commercial_space_mapping_days"]), str(row["symbol"])),
        )

        object_rows: list[dict[str, Any]] = []
        for stat in ranked_symbols:
            symbol = str(stat["symbol"])
            security_row = security_master.get(symbol, {})
            role_guess, role_reason = role_guess_overrides.get(
                symbol,
                (
                    "mapping_activation",
                    "Local evidence is insufficiently clean for stronger role assignment without owner review.",
                ),
            )
            local_evidence_status = evidence_status_overrides.get(symbol, "owner_review_needed")
            object_rows.append(
                {
                    "symbol": symbol,
                    "name": str(name_overrides.get(symbol) or security_row.get("name") or ""),
                    "pool_role_guess": role_guess,
                    "role_guess_reason": role_reason,
                    "commercial_space_mapping_days": int(stat["commercial_space_mapping_days"]),
                    "first_seen_in_local_mapping": str(stat["first_seen"]),
                    "last_seen_in_local_mapping": str(stat["last_seen"]),
                    "mainline_window_count": int(window_counts.get(symbol, 0)),
                    "local_evidence_status": local_evidence_status,
                    "cycle_window_status": "owner_review_needed",
                    "missing_object_override_allowed": True,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v113f_pilot_object_pool_v1",
            "selected_archetype": "commercial_space_mainline",
            "pilot_object_count": len(object_rows),
            "dense_local_mapping_object_count": sum(
                1 for row in object_rows if row["local_evidence_status"] == "dense_local_commercial_space_mapping"
            ),
            "owner_review_priority_count": sum(
                1 for row in object_rows if row["local_evidence_status"] != "dense_local_commercial_space_mapping"
            ),
            "ready_for_label_review_sheet_next": True,
        }
        interpretation = [
            "The first theme-diffusion pilot object pool stays intentionally tiny and only uses locally frozen commercial-space mapping evidence.",
            "Only one object currently looks dense and clean enough to behave like a strong leader seed; the other objects are preserved as owner-correctable draft roles.",
            "This pool is a bounded review draft, not a final truth set and not a training-ready universe.",
        ]
        return V113FPilotObjectPoolReport(summary=summary, object_rows=object_rows, interpretation=interpretation)


def write_v113f_pilot_object_pool_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113FPilotObjectPoolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
