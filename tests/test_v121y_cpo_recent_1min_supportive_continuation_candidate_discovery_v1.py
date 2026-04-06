from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1 import (
    V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryAnalyzer,
    write_report,
)


def test_v121y_cpo_recent_1min_supportive_continuation_candidate_discovery(tmp_path: Path) -> None:
    report_path = tmp_path / "reports" / "analysis"
    report_path.mkdir(parents=True, exist_ok=True)
    source = report_path / "v121x_cpo_recent_1min_pca_structure_audit_v1.json"
    source.write_text(
        json.dumps(
            {
                "band_rows": [
                    {
                        "band": "pc1_low__pc2_low",
                        "mean_close_vs_vwap": -0.0001,
                        "mean_push_efficiency": 0.7,
                        "mean_burst_then_fade_score": 0.0005,
                        "mean_late_session_integrity_score": 0.09,
                    },
                    {
                        "band": "pc1_high__pc2_high",
                        "mean_close_vs_vwap": -0.01,
                        "mean_push_efficiency": -0.8,
                        "mean_burst_then_fade_score": 0.002,
                        "mean_late_session_integrity_score": -0.05,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    analyzer = V121YCpoRecent1MinSupportiveContinuationCandidateDiscoveryAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=report_path,
        report_name="v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1",
        result=result,
    )
    assert result.summary["candidate_band_count"] == 1
    assert result.summary["candidate_band_names"] == ["pc1_low__pc2_low"]
    assert output.exists()
