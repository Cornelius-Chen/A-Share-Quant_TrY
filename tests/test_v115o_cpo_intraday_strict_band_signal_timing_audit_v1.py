import csv
import json
from pathlib import Path

from a_share_quant.strategy.v115o_cpo_intraday_strict_band_signal_timing_audit_v1 import (
    V115OCpoIntradayStrictBandSignalTimingAuditAnalyzer,
)


def test_v115o_strict_signal_timing_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    v115m_payload = json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8"))
    strict_overlay_rows = list(v115m_payload.get("strict_overlay_hit_rows", []))
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv").open("r", encoding="utf-8") as handle:
        training_view_rows = list(csv.DictReader(handle))
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv").open("r", encoding="utf-8") as handle:
        feature_base_rows = list(csv.DictReader(handle))

    analyzer = V115OCpoIntradayStrictBandSignalTimingAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        strict_overlay_rows=strict_overlay_rows,
        training_view_rows=training_view_rows,
        feature_base_rows=feature_base_rows,
    )
    assert result.summary["acceptance_posture"] == "freeze_v115o_cpo_intraday_strict_band_signal_timing_audit_v1"
    assert result.summary["strict_signal_count"] >= 1
    assert len(result.timing_rows) == result.summary["strict_signal_count"]
    assert result.summary["strict_signal_count"] >= 1
    assert all(row["timing_bucket"] in {"intraday_same_session", "late_session", "post_close_or_next_day", "unresolved"} for row in result.timing_rows)
