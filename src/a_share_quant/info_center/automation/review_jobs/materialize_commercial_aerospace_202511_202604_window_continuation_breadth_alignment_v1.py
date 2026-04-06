from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {str(key).lstrip("\ufeff"): value for key, value in row.items()}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [_normalize_row(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


PHASE_CONFIGS = (
    {
        "phase_id": "ca008_phase_december_confirmation",
        "sample_window_id": "ca_train_window_008",
        "phase_name": "december_forum_density_confirmation",
        "trade_date_start": "20251222",
        "trade_date_end": "20251226",
        "expected_anchor_dates": {"2025-12-22", "2025-12-24"},
        "narrative_state": "conference_density_with_explicit_forum_cluster",
        "continuation_question": "Did conference density produce real board confirmation rather than pure attention?",
    },
    {
        "phase_id": "ca008_phase_january_continuation",
        "sample_window_id": "ca_train_window_008",
        "phase_name": "january_conference_continuation_check",
        "trade_date_start": "20260122",
        "trade_date_end": "20260126",
        "expected_anchor_dates": {"2026-01-22"},
        "narrative_state": "conference_chain_continues_into_january",
        "continuation_question": "Did the January continuation meeting upgrade December diffusion into a stronger board leg?",
    },
    {
        "phase_id": "ca008_phase_february_followthrough",
        "sample_window_id": "ca_train_window_008",
        "phase_name": "february_followthrough_failure_check",
        "trade_date_start": "20260203",
        "trade_date_end": "20260213",
        "expected_anchor_dates": set(),
        "narrative_state": "carry_without_new_major_anchor",
        "continuation_question": "Without a fresh major anchor, did the board still show enough breadth to keep the chain tradable?",
    },
)


FIELDNAMES = [
    "phase_id",
    "sample_window_id",
    "phase_name",
    "trade_date_start",
    "trade_date_end",
    "anchor_count",
    "anchor_presence_state",
    "anchor_titles",
    "narrative_state",
    "symbol_coverage_count",
    "positive_return_count",
    "strong_return_count",
    "breakout_like_count",
    "positive_return_share",
    "strong_return_share",
    "breakout_like_share",
    "average_window_return_pct",
    "breadth_alignment_state",
    "continuation_alignment_judgement",
    "strict_supervisor_conclusion",
]

SUMMARY_FIELDNAMES = [
    "sample_window_id",
    "december_alignment_state",
    "january_alignment_state",
    "february_alignment_state",
    "final_window_judgement",
    "final_training_admission",
    "strict_supervisor_conclusion",
]


def _load_bars_by_symbol(path: Path) -> dict[str, list[dict[str, str]]]:
    rows = _read_csv(path)
    by_symbol: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_symbol[row["symbol"]].append(row)
    for symbol_rows in by_symbol.values():
        symbol_rows.sort(key=lambda row: row["trade_date"])
    return by_symbol


def _window_stats(
    by_symbol: dict[str, list[dict[str, str]]],
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    covered = 0
    positive = 0
    strong = 0
    breakout = 0
    returns: list[float] = []
    for symbol_rows in by_symbol.values():
        window_rows = [row for row in symbol_rows if start_date <= row["trade_date"] <= end_date]
        if not window_rows:
            continue
        covered += 1
        start_close = float(window_rows[0]["close"])
        end_close = float(window_rows[-1]["close"])
        ret = ((end_close - start_close) / start_close * 100.0) if start_close else 0.0
        returns.append(ret)
        if ret > 0:
            positive += 1
        if ret >= 5.0:
            strong += 1
        pre_rows = [row for row in symbol_rows if row["trade_date"] < start_date]
        pre20_rows = pre_rows[-20:]
        pre20_high = max((float(row["high"]) for row in pre20_rows), default=0.0)
        window_high = max(float(row["high"]) for row in window_rows)
        if pre20_high and window_high > pre20_high:
            breakout += 1
    positive_share = (positive / covered) if covered else 0.0
    strong_share = (strong / covered) if covered else 0.0
    breakout_share = (breakout / covered) if covered else 0.0
    average_return = (sum(returns) / len(returns)) if returns else 0.0
    return {
        "symbol_coverage_count": covered,
        "positive_return_count": positive,
        "strong_return_count": strong,
        "breakout_like_count": breakout,
        "positive_return_share": round(positive_share, 4),
        "strong_return_share": round(strong_share, 4),
        "breakout_like_share": round(breakout_share, 4),
        "average_window_return_pct": round(average_return, 4),
    }


def _anchor_rows_for_phase(
    extract_rows: list[dict[str, str]],
    expected_anchor_dates: set[str],
) -> list[dict[str, str]]:
    if not expected_anchor_dates:
        return []
    return [row for row in extract_rows if row["event_date"] in expected_anchor_dates]


def _breadth_alignment_state(stats: dict[str, Any]) -> str:
    if (
        stats["positive_return_share"] >= 0.8
        and stats["strong_return_share"] >= 0.5
        and stats["breakout_like_share"] >= 0.5
    ):
        return "broad_confirmation_real"
    if stats["average_window_return_pct"] < -2.0 and stats["positive_return_share"] < 0.3:
        return "breadth_failed"
    return "continuation_not_upgraded"


def _phase_judgement(phase_name: str, breadth_alignment_state: str, anchor_presence_state: str) -> str:
    if phase_name == "december_forum_density_confirmation":
        return "conference_density_aligned_with_real_board_confirmation"
    if phase_name == "january_conference_continuation_check":
        return "continuation_anchor_present_but_board_breadth_not_upgraded"
    if anchor_presence_state == "no_new_major_anchor":
        return "no_new_anchor_and_board_failed_to_keep_chain_tradable"
    return "continuation_failed"


def _strict_conclusion(phase_name: str, breadth_alignment_state: str) -> str:
    if phase_name == "december_forum_density_confirmation":
        return "12月会议链不是空喊，确实伴随了较强板块确认，但这只能证明阶段性扩散成立。"
    if phase_name == "january_conference_continuation_check":
        return "1月继续有会议锚，但板块广度已经明显降下来，说明它没有把12月那波扩散升级成更强主腿。"
    if breadth_alignment_state == "breadth_failed":
        return "2月最关键的结论是：没有新锚、板块广度明显失效，所以会议链已经不足以维持可交易延续。"
    return "这段延续没有形成足够板块承接。"


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bars_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
    extract_path = (
        repo_root / "data" / "training" / "commercial_aerospace_202511_202604_backfill_evidence_extract_v1.csv"
    )
    by_symbol = _load_bars_by_symbol(bars_path)
    extract_rows = [
        row for row in _read_csv(extract_path) if row.get("linked_window_id") == "ca_train_window_008"
    ]
    output_rows: list[dict[str, Any]] = []
    for phase in PHASE_CONFIGS:
        stats = _window_stats(by_symbol, phase["trade_date_start"], phase["trade_date_end"])
        anchors = _anchor_rows_for_phase(extract_rows, phase["expected_anchor_dates"])
        anchor_presence_state = "anchors_present" if anchors else "no_new_major_anchor"
        breadth_alignment_state = _breadth_alignment_state(stats)
        output_rows.append(
            {
                "phase_id": phase["phase_id"],
                "sample_window_id": phase["sample_window_id"],
                "phase_name": phase["phase_name"],
                "trade_date_start": phase["trade_date_start"],
                "trade_date_end": phase["trade_date_end"],
                "anchor_count": len(anchors),
                "anchor_presence_state": anchor_presence_state,
                "anchor_titles": " | ".join(anchor["source_title"] for anchor in anchors) if anchors else "无新增强锚",
                "narrative_state": phase["narrative_state"],
                **stats,
                "breadth_alignment_state": breadth_alignment_state,
                "continuation_alignment_judgement": _phase_judgement(
                    phase["phase_name"], breadth_alignment_state, anchor_presence_state
                ),
                "strict_supervisor_conclusion": _strict_conclusion(
                    phase["phase_name"], breadth_alignment_state
                ),
            }
        )

    summary_rows = [
        {
            "sample_window_id": "ca_train_window_008",
            "december_alignment_state": output_rows[0]["breadth_alignment_state"],
            "january_alignment_state": output_rows[1]["breadth_alignment_state"],
            "february_alignment_state": output_rows[2]["breadth_alignment_state"],
            "final_window_judgement": (
                "december_confirmation_real_but_january_not_upgraded_and_february_failed"
            ),
            "final_training_admission": "subwindow_ready_but_full_window_not_ready",
            "strict_supervisor_conclusion": (
                "Window 008 is now evidence-locked as a real December confirmation followed by a weak January continuation and a failed February followthrough; it should train diffusion decay, not a durable primary leg."
            ),
        }
    ]
    return output_rows, summary_rows


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    output_rows, summary_rows = materialize(repo_root)
    output_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_continuation_breadth_alignment_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_continuation_breadth_alignment_summary_v1.csv"
    )
    _write_csv(output_path, output_rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(output_rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
