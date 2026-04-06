from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117a_cpo_quality_side_cooled_retention_v1 import (
    V117ACpoQualitySideCooledRetentionAnalyzer,
)


def test_v117a_quality_side_retention() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117ACpoQualitySideCooledRetentionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116z_payload=json.loads((repo_root / "reports" / "analysis" / "v116z_cpo_quality_side_cooled_refinement_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["retained_variant_name"] == "cooled_q_0p25"
    assert result.summary["equivalent_shadow_variant_name"] == "cooled_q_0p33"
    assert result.summary["effective_visible_axis"] == "pc1"
    assert _to_float(result.retained_variant_row["avg_expectancy_proxy_3d"]) == _to_float(result.equivalent_shadow_row["avg_expectancy_proxy_3d"])


def _to_float(value: object) -> float:
    return float(value)
