from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CrossStrategyCycleConsistencyReport:
    summary: dict[str, Any]
    strategy_rows: list[dict[str, Any]]
    shared_mechanisms: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "strategy_rows": self.strategy_rows,
            "shared_mechanisms": self.shared_mechanisms,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class CrossStrategyCycleConsistencyAnalyzer:
    """Check whether multiple strategies share the same drawdown-cycle map."""

    def analyze(self, *, report_payloads: list[dict[str, Any]]) -> CrossStrategyCycleConsistencyReport:
        strategy_rows: list[dict[str, Any]] = []
        signatures: list[tuple[str, str, str]] = []
        per_strategy_signatures: dict[str, set[tuple[str, str, str]]] = {}

        for payload in report_payloads:
            summary = dict(payload.get("summary", {}))
            strategy_name = str(summary.get("strategy_name"))
            mechanism_rows = list(payload.get("mechanism_rows", []))
            negative_rows = [row for row in mechanism_rows if str(row.get("cycle_sign")) == "negative"]
            signature_set = {
                (
                    str(row.get("mechanism_type")),
                    str(row.get("incumbent_cycle", {}).get("entry_date")),
                    str(row.get("incumbent_cycle", {}).get("exit_date")),
                )
                for row in negative_rows
            }
            per_strategy_signatures[strategy_name] = signature_set
            signatures.extend(signature_set)
            strategy_rows.append(
                {
                    "strategy_name": strategy_name,
                    "negative_cycle_count": len(negative_rows),
                    "mechanism_types": sorted({str(row.get("mechanism_type")) for row in negative_rows}),
                    "cycle_signatures": [
                        {
                            "mechanism_type": signature[0],
                            "entry_date": signature[1],
                            "exit_date": signature[2],
                        }
                        for signature in sorted(signature_set)
                    ],
                }
            )

        counter = Counter(signatures)
        strategy_count = len(strategy_rows)
        shared_mechanisms = [
            {
                "mechanism_type": mechanism_type,
                "entry_date": entry_date,
                "exit_date": exit_date,
                "shared_strategy_count": count,
            }
            for (mechanism_type, entry_date, exit_date), count in counter.items()
            if count == strategy_count
        ]
        shared_mechanisms.sort(key=lambda item: (item["entry_date"], item["mechanism_type"]))

        identical = all(
            signatures == next(iter(per_strategy_signatures.values()))
            for signatures in per_strategy_signatures.values()
        ) if per_strategy_signatures else False
        summary = {
            "strategy_count": strategy_count,
            "shared_negative_mechanism_count": len(shared_mechanisms),
            "identical_negative_cycle_map": identical,
            "primary_takeaway": (
                "If multiple strategies share the same negative-cycle map, the drawdown pocket is more likely to be a dataset-level structural effect."
            ),
        }
        interpretation = [
            "A shared negative-cycle map means the pocket is not just one strategy's accident.",
            "If the same entry dates and mechanism types repeat across strategies, future replay effort should move to other pockets instead of re-explaining the same one.",
            "Differences across strategies matter only when the shared map breaks; otherwise the pocket can be treated as structurally stable.",
        ]
        return CrossStrategyCycleConsistencyReport(
            summary=summary,
            strategy_rows=strategy_rows,
            shared_mechanisms=shared_mechanisms,
            interpretation=interpretation,
        )


def write_cross_strategy_cycle_consistency_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CrossStrategyCycleConsistencyReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
