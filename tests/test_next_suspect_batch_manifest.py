from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.next_suspect_batch_manifest import (
    NextSuspectBatchManifestAnalyzer,
    write_next_suspect_batch_manifest_report,
)


def test_next_suspect_batch_manifest_checks_new_symbols_and_archetype_coverage(
    tmp_path: Path,
) -> None:
    analyzer = NextSuspectBatchManifestAnalyzer()
    result = analyzer.analyze(
        base_universe_symbols=["AAA", "BBB"],
        seed_universe_symbols=["CCC", "DDD", "EEE"],
        manifest_entries=[
            {
                "symbol": "CCC",
                "target_archetype": "theme_loaded_balanced_turnover_broad_sector",
                "rationale": "r1",
            },
            {
                "symbol": "DDD",
                "target_archetype": "theme_loaded_balanced_turnover_narrow_sector",
                "rationale": "r2",
            },
            {
                "symbol": "EEE",
                "target_archetype": "theme_light_concentrated_turnover_broad_sector",
                "rationale": "r3",
            },
        ],
        required_archetypes=[
            "theme_loaded_balanced_turnover_broad_sector",
            "theme_loaded_balanced_turnover_narrow_sector",
            "theme_light_concentrated_turnover_broad_sector",
        ],
    )

    assert result.summary["overlap_with_market_v1_count"] == 0
    assert result.summary["missing_archetype_count"] == 0
    assert result.summary["ready_to_bootstrap_next_batch"] is True

    output_path = write_next_suspect_batch_manifest_report(
        reports_dir=tmp_path,
        report_name="next_suspect_batch_manifest_test",
        result=result,
    )
    assert output_path.exists()
