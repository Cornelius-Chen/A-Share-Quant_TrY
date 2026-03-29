from __future__ import annotations

from a_share_quant.strategy.cycle_family_inventory import CycleFamilyInventoryAnalyzer


def test_aggregates_family_edge_and_report_counts() -> None:
    analyzer = CycleFamilyInventoryAnalyzer()
    result = analyzer.analyze(
        report_specs=[
            {
                "report_name": "r1",
                "report_path": "tests/fixtures/report1.json",
                "dataset_name": "d1",
                "slice_name": "s1",
                "strategy_name": "st",
                "symbol": "AAA",
            },
            {
                "report_name": "r2",
                "report_path": "tests/fixtures/report2.json",
                "dataset_name": "d2",
                "slice_name": "s2",
                "strategy_name": "st",
                "symbol": "BBB",
            },
        ]
    )
    family = next(row for row in result.family_rows if row["family_name"] == "entry_suppression_avoidance")
    assert family["report_count"] == 2
    assert family["negative_row_count"] == 2
    assert family["net_negative_improvement"] == 300.0
    opportunity = next(row for row in result.family_rows if row["family_name"] == "entry_suppression_opportunity_cost")
    assert opportunity["positive_opportunity_cost"] == 20.0
