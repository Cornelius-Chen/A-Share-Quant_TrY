from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v116l_cpo_visible_only_cooled_shadow_retention_v1 import (
    V116LCpoVisibleOnlyCooledShadowRetentionAnalyzer,
)


def test_v116l_cooled_shadow_retention_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116LCpoVisibleOnlyCooledShadowRetentionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116k_payload=json.loads((repo_root / "reports" / "analysis" / "v116k_cpo_visible_only_shadow_heat_trim_review_v1.json").read_text(encoding="utf-8"))
    )
    assert result.summary["acceptance_posture"] == "freeze_v116l_cpo_visible_only_cooled_shadow_retention_v1"
    assert result.summary["retained_variant_name"] != ""
