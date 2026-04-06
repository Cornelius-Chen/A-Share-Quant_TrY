from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Report:
    summary: dict[str, Any]
    source_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "source_rows": self.source_rows,
            "interpretation": self.interpretation,
        }


class V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_event_attention_source_hardness_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def _load_events(self) -> dict[str, dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        path = (
            self.repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows[row["registry_id"]] = row
        return rows

    def analyze(self) -> V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Report:
        events = self._load_events()
        candidates = self._load_json(
            "reports/analysis/v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1.json"
        )
        separation = self._load_json(
            "reports/analysis/v134ia_commercial_aerospace_event_attention_role_separation_audit_v1.json"
        )

        separated_by_symbol = {row["symbol"]: row for row in separation["separated_rows"]}

        source_rows: list[dict[str, Any]] = []
        for row in candidates["candidate_rows"]:
            symbol = row["symbol"]
            source_backing = row["source_backing"]
            separated_role = separated_by_symbol.get(symbol, {}).get("separated_role", "")

            if symbol == "000547":
                event_id = "ca_source_007"
                event_row = events[event_id]
                source_hardness = "hard_anchor_grade_source"
                hardness_reasoning = (
                    "explicit symbol-named turning-point theme-heat source retained as decisive risk seed"
                )
            elif symbol == "603601":
                event_id = "ca_source_010"
                event_row = events[event_id]
                source_hardness = "retained_continuation_support_source"
                hardness_reasoning = (
                    "retained supply-chain validation source supports continuation and carrier watch, but it is not a direct heat-axis naming source"
                )
            elif symbol == "301306":
                event_id = "ca_source_011"
                event_row = events[event_id]
                source_hardness = "retained_follow_support_source"
                hardness_reasoning = (
                    "retained supply-chain validation source supports follow behavior, but current evidence still reads as follower-grade rather than anchor-grade"
                )
            elif symbol == "300342":
                event_id = "ca_source_004"
                event_row = events[event_id]
                source_hardness = "discarded_theme_heat_source"
                hardness_reasoning = (
                    "theme-heat source exists, but it was explicitly discarded as non-decisive and cannot support hard anchor promotion"
                )
            else:
                event_id = ""
                event_row = {}
                source_hardness = "no_retained_event_source"
                hardness_reasoning = (
                    "current local role is built from crowding path only and has no retained event source to harden anchor status"
                )

            source_rows.append(
                {
                    "symbol": symbol,
                    "display_name": row["display_name"],
                    "candidate_role": row["candidate_role"],
                    "separated_role": separated_role,
                    "source_backing": source_backing,
                    "event_registry_id": event_id,
                    "event_scope": event_row.get("event_scope", ""),
                    "decisive_semantic": event_row.get("decisive_semantic", ""),
                    "decisive_retained": event_row.get("decisive_retained", ""),
                    "decisive_reason": event_row.get("decisive_reason", ""),
                    "source_hardness": source_hardness,
                    "hardness_reasoning": hardness_reasoning,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(source_rows[0].keys()))
            writer.writeheader()
            writer.writerows(source_rows)

        summary = {
            "acceptance_posture": "freeze_v134ja_commercial_aerospace_event_attention_source_hardness_audit_v1",
            "symbol_count": len(source_rows),
            "hard_anchor_grade_source_count": sum(
                1 for row in source_rows if row["source_hardness"] == "hard_anchor_grade_source"
            ),
            "retained_but_non_anchor_source_count": sum(
                1
                for row in source_rows
                if row["source_hardness"]
                in {"retained_continuation_support_source", "retained_follow_support_source"}
            ),
            "discarded_or_missing_source_count": sum(
                1
                for row in source_rows
                if row["source_hardness"] in {"discarded_theme_heat_source", "no_retained_event_source"}
            ),
            "only_hard_anchor_symbol": "000547",
            "source_hardness_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "event-attention source hardness remains single-case: only 000547 has anchor-grade source backing, while 603601 and 301306 have retained but non-anchor support sources, 300342 has only discarded theme heat, and 002361 has no retained event source",
        }
        interpretation = [
            "V1.34JA asks a narrower question than role quality: what kind of source is actually backing each role candidate.",
            "This makes the current stopline explicit: the stack is not missing a threshold tweak, it is missing a second anchor-grade source.",
        ]
        return V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Report(
            summary=summary,
            source_rows=source_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JACommercialAerospaceEventAttentionSourceHardnessAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ja_commercial_aerospace_event_attention_source_hardness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
