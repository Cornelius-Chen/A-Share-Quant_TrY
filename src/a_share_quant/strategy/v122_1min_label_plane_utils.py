from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def load_recent_1min_labeled_rows(repo_root: Path) -> list[dict[str, Any]]:
    feature_path = repo_root / "data" / "training" / "cpo_recent_1min_microstructure_feature_table_v1.csv"
    label_path = repo_root / "data" / "training" / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"

    with feature_path.open("r", encoding="utf-8") as handle:
        feature_rows = list(csv.DictReader(handle))
    with label_path.open("r", encoding="utf-8") as handle:
        label_rows = list(csv.DictReader(handle))

    feature_map = {
        (row["symbol"], row["trade_date"], row["clock_time"]): row
        for row in feature_rows
    }

    joined_rows: list[dict[str, Any]] = []
    for label_row in label_rows:
        key = (label_row["symbol"], label_row["trade_date"], label_row["clock_time"])
        feature_row = feature_map.get(key)
        if feature_row is None:
            continue
        joined_rows.append({**feature_row, **label_row})
    return joined_rows
