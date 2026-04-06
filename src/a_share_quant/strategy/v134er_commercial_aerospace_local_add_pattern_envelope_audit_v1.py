from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ep_commercial_aerospace_intraday_add_tiered_label_specification_v1 import (
    V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer,
)


@dataclass(slots=True)
class V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Report:
    summary: dict[str, Any]
    envelope_rows: list[dict[str, Any]]
    separation_rows: list[dict[str, Any]]
    archetype_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "envelope_rows": self.envelope_rows,
            "separation_rows": self.separation_rows,
            "archetype_rows": self.archetype_rows,
            "interpretation": self.interpretation,
        }


class V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _round_or_none(value: float | None) -> float | None:
        return round(value, 8) if value is not None else None

    @staticmethod
    def _index_by_label(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        return {row["label_tier"]: row for row in rows}

    @staticmethod
    def _gap(lhs: dict[str, Any], rhs: dict[str, Any], field: str) -> float | None:
        left = lhs.get(f"{field}_mean")
        right = rhs.get(f"{field}_mean")
        if left is None or right is None:
            return None
        return round(left - right, 8)

    def analyze(self) -> V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Report:
        spec = V134EPCommercialAerospaceIntradayAddTieredLabelSpecificationV1Analyzer(self.repo_root).analyze()
        tier_map = self._index_by_label(spec.tier_rows)

        envelope_rows = spec.tier_rows
        separation_rows = [
            {
                "comparison": "allowed_preheat_full_vs_allowed_preheat_probe",
                "open_to_5m_gap": self._gap(
                    tier_map["allowed_preheat_full_add"],
                    tier_map["allowed_preheat_probe_add"],
                    "open_to_5m",
                ),
                "open_to_15m_gap": self._gap(
                    tier_map["allowed_preheat_full_add"],
                    tier_map["allowed_preheat_probe_add"],
                    "open_to_15m",
                ),
                "close_loc_15m_gap": self._gap(
                    tier_map["allowed_preheat_full_add"],
                    tier_map["allowed_preheat_probe_add"],
                    "close_loc_15m",
                ),
                "open_to_60m_gap": self._gap(
                    tier_map["allowed_preheat_full_add"],
                    tier_map["allowed_preheat_probe_add"],
                    "open_to_60m",
                ),
                "reading": "preheat_full_add carries materially stronger early acceptance than preheat_probe_add and should stay a separate allowed tier",
            },
            {
                "comparison": "failed_impulse_chase_vs_allowed_preheat_full",
                "open_to_5m_gap": self._gap(
                    tier_map["failed_impulse_chase_add"],
                    tier_map["allowed_preheat_full_add"],
                    "open_to_5m",
                ),
                "open_to_15m_gap": self._gap(
                    tier_map["failed_impulse_chase_add"],
                    tier_map["allowed_preheat_full_add"],
                    "open_to_15m",
                ),
                "close_loc_15m_gap": self._gap(
                    tier_map["failed_impulse_chase_add"],
                    tier_map["allowed_preheat_full_add"],
                    "close_loc_15m",
                ),
                "open_to_60m_gap": self._gap(
                    tier_map["failed_impulse_chase_add"],
                    tier_map["allowed_preheat_full_add"],
                    "open_to_60m",
                ),
                "reading": "failed impulse adds are not weak versions of allowed adds; they are immediate hard-collapse chases",
            },
            {
                "comparison": "blocked_board_lockout_vs_failed_impulse_chase",
                "open_to_15m_gap": self._gap(
                    tier_map["blocked_board_lockout_add"],
                    tier_map["failed_impulse_chase_add"],
                    "open_to_15m",
                ),
                "close_loc_15m_gap": self._gap(
                    tier_map["blocked_board_lockout_add"],
                    tier_map["failed_impulse_chase_add"],
                    "close_loc_15m",
                ),
                "open_to_60m_gap": self._gap(
                    tier_map["blocked_board_lockout_add"],
                    tier_map["failed_impulse_chase_add"],
                    "open_to_60m",
                ),
                "close_loc_60m_gap": self._gap(
                    tier_map["blocked_board_lockout_add"],
                    tier_map["failed_impulse_chase_add"],
                    "close_loc_60m",
                ),
                "reading": "blocked adds can show brief early stabilization, but they remain board-vetoed and decay back into weak late-session acceptance",
            },
        ]

        archetype_rows = [
            {
                "label_tier": "allowed_preheat_probe_add",
                "archetype_name": "soft_neutral_preheat_acceptance",
                "archetype_text": (
                    "the first 15 minutes are usually near flat with middling close-location support; this is permissive participation, not aggressive confirmation"
                ),
            },
            {
                "label_tier": "allowed_preheat_full_add",
                "archetype_name": "high_acceptance_preheat_full",
                "archetype_text": (
                    "the first 15 to 30 minutes tend to hold positive open-to-minute returns and upper-half range closes, indicating stronger acceptance than the probe tier"
                ),
            },
            {
                "label_tier": "failed_impulse_chase_add",
                "archetype_name": "hard_opening_impulse_failure",
                "archetype_text": (
                    "the add attempt collapses within the first 5 to 15 minutes and remains pinned near the session floor; this is a chase failure, not a timing miss"
                ),
            },
            {
                "label_tier": "blocked_board_lockout_add",
                "archetype_name": "board_vetoed_local_rebound",
                "archetype_text": (
                    "the first 15 minutes can look temporarily repaired, but the broader 30 to 60 minute envelope remains weak and board-level vetoes dominate the decision"
                ),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v134er_commercial_aerospace_local_add_pattern_envelope_audit_v1",
            "label_tier_count": len(envelope_rows),
            "separation_pair_count": len(separation_rows),
            "authoritative_rule": (
                "the intraday-add frontier now has stable local pattern envelopes: preheat full is a stronger allowed family than probe, "
                "failed impulse chase is a distinct hard-collapse family, and blocked board-lockout adds remain board-vetoed despite occasional brief early repair"
            ),
        }
        interpretation = [
            "V1.34ER turns the first add-tier vocabulary into local early-session pattern envelopes.",
            "The next useful step is no longer descriptive counting; it is rule-candidate auditing built on these frozen envelopes.",
        ]
        return V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Report(
            summary=summary,
            envelope_rows=envelope_rows,
            separation_rows=separation_rows,
            archetype_rows=archetype_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ERCommercialAerospaceLocalAddPatternEnvelopeAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134er_commercial_aerospace_local_add_pattern_envelope_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
