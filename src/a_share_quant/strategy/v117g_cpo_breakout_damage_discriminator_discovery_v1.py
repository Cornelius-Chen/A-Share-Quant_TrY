from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VISIBLE_FEATURES = (
    "f30_breakout_efficiency_rz",
    "f60_breakout_efficiency_rz",
    "f30_pullback_from_high_rz",
    "f60_pullback_from_high_rz",
    "f30_last_bar_return_rz",
    "f60_last_bar_return_rz",
    "f30_afternoon_volume_share_rz",
    "f60_afternoon_volume_share_rz",
    "d5_30_last_bar_upper_shadow_ratio_rz",
    "d15_60_last_bar_upper_shadow_ratio_rz",
    "f30_failed_push_proxy",
    "f60_failed_push_proxy",
    "d15_60_failed_push_proxy",
    "pc3_score",
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V117GCpoBreakoutDamageDiscriminatorDiscoveryReport:
    summary: dict[str, Any]
    feature_separation_rows: list[dict[str, Any]]
    candidate_score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_separation_rows": self.feature_separation_rows,
            "candidate_score_rows": self.candidate_score_rows,
            "interpretation": self.interpretation,
        }


class V117GCpoBreakoutDamageDiscriminatorDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v116z_payload: dict[str, Any],
        v116w_payload: dict[str, Any],
        rebuilt_rows_path: Path,
    ) -> V117GCpoBreakoutDamageDiscriminatorDiscoveryReport:
        q25_hits = {
            (str(row["signal_trade_date"]), str(row["symbol"]))
            for row in list(v116z_payload.get("hit_rows", []))
            if str(row.get("variant_name")) == "cooled_q_0p25"
        }
        hot_only = {
            (str(row["signal_trade_date"]), str(row["symbol"]))
            for row in list(v116w_payload.get("hit_rows", []))
            if str(row.get("variant_name")) == "hot_upper_bound_reference"
            and (str(row["signal_trade_date"]), str(row["symbol"])) not in q25_hits
        }

        rows = _load_csv_rows(rebuilt_rows_path)
        q25_rows = [row for row in rows if (str(row["signal_trade_date"]), str(row["symbol"])) in q25_hits]
        hot_only_rows = [row for row in rows if (str(row["signal_trade_date"]), str(row["symbol"])) in hot_only]

        feature_separation_rows: list[dict[str, Any]] = []
        for feature in VISIBLE_FEATURES:
            q25_mean = sum(_to_float(row.get(feature)) for row in q25_rows) / len(q25_rows)
            hot_mean = sum(_to_float(row.get(feature)) for row in hot_only_rows) / len(hot_only_rows)
            separation = q25_mean - hot_mean
            preferred_direction = "higher_is_better" if separation > 0 else "lower_is_better"
            feature_separation_rows.append(
                {
                    "feature_name": feature,
                    "q25_mean": round(q25_mean, 6),
                    "hot_only_mean": round(hot_mean, 6),
                    "mean_separation": round(separation, 6),
                    "preferred_direction": preferred_direction,
                    "abs_separation": round(abs(separation), 6),
                }
            )
        feature_separation_rows.sort(key=lambda row: row["abs_separation"], reverse=True)

        positive_features = (
            "f30_breakout_efficiency_rz",
            "f60_breakout_efficiency_rz",
            "f30_last_bar_return_rz",
            "f60_last_bar_return_rz",
            "f30_pullback_from_high_rz",
            "f60_pullback_from_high_rz",
        )
        negative_features = (
            "f30_afternoon_volume_share_rz",
            "f60_afternoon_volume_share_rz",
            "d5_30_last_bar_upper_shadow_ratio_rz",
            "d15_60_last_bar_upper_shadow_ratio_rz",
            "f30_failed_push_proxy",
            "f60_failed_push_proxy",
            "d15_60_failed_push_proxy",
        )

        candidate_score_rows: list[dict[str, Any]] = []
        for row in rows:
            key = (str(row["signal_trade_date"]), str(row["symbol"]))
            if key not in q25_hits and key not in hot_only:
                continue
            positive_score = sum(_to_float(row.get(feature)) for feature in positive_features)
            negative_score = sum(_to_float(row.get(feature)) for feature in negative_features)
            composite_score = positive_score - negative_score
            candidate_score_rows.append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "group_name": "q25_hit" if key in q25_hits else "hot_only",
                    "state_band": str(row.get("state_band")),
                    "action_favored_3d": str(row.get("action_favored_3d")),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                    "damage_positive_score": round(positive_score, 6),
                    "damage_negative_score": round(negative_score, 6),
                    "candidate_damage_score": round(composite_score, 6),
                }
            )

        candidate_score_rows.sort(
            key=lambda row: (row["group_name"] != "q25_hit", -_to_float(row["candidate_damage_score"])),
        )

        q25_scores = [row["candidate_damage_score"] for row in candidate_score_rows if row["group_name"] == "q25_hit"]
        hot_scores = [row["candidate_damage_score"] for row in candidate_score_rows if row["group_name"] == "hot_only"]
        score_gap = (sum(q25_scores) / len(q25_scores)) - (sum(hot_scores) / len(hot_scores))

        summary = {
            "acceptance_posture": "freeze_v117g_cpo_breakout_damage_discriminator_discovery_v1",
            "q25_hit_count": len(q25_rows),
            "hot_only_count": len(hot_only_rows),
            "top_separation_feature": feature_separation_rows[0]["feature_name"],
            "candidate_discriminator_name": "breakout_damage_containment_score_candidate",
            "candidate_score_mean_gap_q25_minus_hot_only": round(score_gap, 6),
            "recommended_next_posture": "audit_breakout_damage_score_as_new_quality_side_candidate_and_keep_candidate_only",
        }
        interpretation = [
            "V1.17G deliberately avoids the old continuation-integrity package and instead searches for a new quality-side discriminator centered on breakout efficiency and price-damage containment.",
            "The resulting candidate score rewards efficient continuation and punishes late-session damage, failed push behavior, and volume-heavy deterioration.",
            "This is still discovery only. The point is to start a genuinely new branch, not to silently rebrand the previous quality line.",
        ]
        return V117GCpoBreakoutDamageDiscriminatorDiscoveryReport(
            summary=summary,
            feature_separation_rows=feature_separation_rows,
            candidate_score_rows=candidate_score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V117GCpoBreakoutDamageDiscriminatorDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V117GCpoBreakoutDamageDiscriminatorDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116z_payload=json.loads((repo_root / "reports" / "analysis" / "v116z_cpo_quality_side_cooled_refinement_v1.json").read_text(encoding="utf-8")),
        v116w_payload=json.loads((repo_root / "reports" / "analysis" / "v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1.json").read_text(encoding="utf-8")),
        rebuilt_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v117g_cpo_breakout_damage_discriminator_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
