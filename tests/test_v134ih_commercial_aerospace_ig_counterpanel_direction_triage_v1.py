from pathlib import Path

from a_share_quant.strategy.v134ih_commercial_aerospace_ig_counterpanel_direction_triage_v1 import (
    V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Analyzer,
)


def test_v134ih_counterpanel_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IHCommercialAerospaceIGCounterpanelDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["searched_symbol_count"] == 5
    assert report.summary["second_hard_counterpanel_found"] is False
    directions = {row["target"]: row["direction"] for row in report.triage_rows}
    assert directions["hard_counterpanel"] == "still_single_case_keep_000547_as_only_hard_anchor_decoy_reference"
