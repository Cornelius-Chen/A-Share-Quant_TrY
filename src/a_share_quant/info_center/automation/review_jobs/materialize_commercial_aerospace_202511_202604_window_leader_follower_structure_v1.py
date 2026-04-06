from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@dataclass(frozen=True, slots=True)
class LeaderFollowerRule:
    subwindow_id: str
    symbol: str
    structure_phase: str
    leader_follower_class: str
    classification_reason: str
    continuation_state: str
    strict_supervisor_conclusion: str


RULES: tuple[LeaderFollowerRule, ...] = (
    LeaderFollowerRule(
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        symbol="688568",
        structure_phase="december_forum_diffusion",
        leader_follower_class="leader",
        classification_reason="formal_data_application_name_cleared_platform_and_held_positive_net_flow",
        continuation_state="local_breakout_confirmed",
        strict_supervisor_conclusion="中科星图是会议链里最像领涨核心的正式组样本，但它证明的只是子方向扩散，不是全面板块点火。",
    ),
    LeaderFollowerRule(
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        symbol="300045",
        structure_phase="december_forum_diffusion",
        leader_follower_class="follower",
        classification_reason="active_front_row_name_joined_breakout_but_stayed_structural_response_instead_of_formal_core_leadership",
        continuation_state="active_followthrough_only",
        strict_supervisor_conclusion="华力创通可以保留在样本里，但更适合作为活跃前排跟随，而不是正式领涨核心。",
    ),
    LeaderFollowerRule(
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        symbol="688066",
        structure_phase="december_forum_diffusion",
        leader_follower_class="follower",
        classification_reason="formal_remote_sensing_name_participated_but_failed_to_clear_prior_supply",
        continuation_state="selective_followthrough_only",
        strict_supervisor_conclusion="航天宏图方向上跟对了，但结构没站上来，所以更适合作为跟随样本。",
    ),
    LeaderFollowerRule(
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        symbol="002465",
        structure_phase="december_forum_diffusion",
        leader_follower_class="follower",
        classification_reason="supporting_comm_nav_name_broke_platform_but_amplitude_and board_role_stayed_secondary",
        continuation_state="supportive_expansion_only",
        strict_supervisor_conclusion="海格通信说明会议链会把配套方向带活，但强度仍不足以定义全面重估。",
    ),
    LeaderFollowerRule(
        subwindow_id="ca008_feb_followthrough_20260203_20260213",
        symbol="688568",
        structure_phase="february_failed_followthrough",
        leader_follower_class="leader_deterioration",
        classification_reason="the_best_december_leader_failed_to_hold_and_became_the clearest continuation breakdown signal",
        continuation_state="leader_broken",
        strict_supervisor_conclusion="2月最重要的负证据不是谁反弹，而是中科星图这个领涨核心都没能续上。",
    ),
    LeaderFollowerRule(
        subwindow_id="ca008_feb_followthrough_20260203_20260213",
        symbol="688066",
        structure_phase="february_failed_followthrough",
        leader_follower_class="follower_failure",
        classification_reason="remote_sensing follower remained a weak repair and never upgraded into a tradable new leg",
        continuation_state="follower_failed",
        strict_supervisor_conclusion="航天宏图在2月只给出弱修复，证明会议链无法自然升级成持续主升。",
    ),
    LeaderFollowerRule(
        subwindow_id="ca008_feb_followthrough_20260203_20260213",
        symbol="002465",
        structure_phase="february_failed_followthrough",
        leader_follower_class="follower_failure",
        classification_reason="comm_nav support faded into weak repair without capital confirmation",
        continuation_state="follower_failed",
        strict_supervisor_conclusion="海格通信的2月表现说明配套方向也没形成新的承接。",
    ),
)


FIELDNAMES = [
    "sample_window_id",
    "subwindow_id",
    "trade_date_start",
    "trade_date_end",
    "symbol",
    "display_name",
    "symbol_role",
    "structure_phase",
    "leader_follower_class",
    "classification_reason",
    "continuation_state",
    "end_return_pct",
    "window_high_vs_pre20_high_pct",
    "volume_ratio_vs_pre5",
    "window_net_mf_amount",
    "breakout_state",
    "breadth_state",
    "capital_state",
    "tradability_label",
    "final_training_admission",
    "strict_supervisor_conclusion",
]

SUMMARY_FIELDNAMES = [
    "sample_window_id",
    "december_leader_count",
    "december_follower_count",
    "february_leader_deterioration_count",
    "february_follower_failure_count",
    "excluded_soft_candidate_count",
    "final_training_admission",
    "strict_supervisor_conclusion",
]


def _rule_map() -> dict[tuple[str, str], LeaderFollowerRule]:
    return {(rule.subwindow_id, rule.symbol): rule for rule in RULES}


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    structure_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_structure_slice_v1.csv"
    )
    rows = _read_csv(structure_path)
    if not rows:
        raise FileNotFoundError(structure_path)

    relevant_rows = [row for row in rows if row["sample_window_id"] == "ca_train_window_008"]
    rule_map = _rule_map()
    output_rows: list[dict[str, Any]] = []
    for row in relevant_rows:
        rule = rule_map.get((row["subwindow_id"], row["symbol"]))
        if rule is None:
            continue
        output_rows.append(
            {
                "sample_window_id": row["sample_window_id"],
                "subwindow_id": row["subwindow_id"],
                "trade_date_start": row["trade_date_start"],
                "trade_date_end": row["trade_date_end"],
                "symbol": row["symbol"],
                "display_name": row["display_name"],
                "symbol_role": row["symbol_role"],
                "structure_phase": rule.structure_phase,
                "leader_follower_class": rule.leader_follower_class,
                "classification_reason": rule.classification_reason,
                "continuation_state": rule.continuation_state,
                "end_return_pct": row["end_return_pct"],
                "window_high_vs_pre20_high_pct": row["window_high_vs_pre20_high_pct"],
                "volume_ratio_vs_pre5": row["volume_ratio_vs_pre5"],
                "window_net_mf_amount": row["window_net_mf_amount"],
                "breakout_state": row["breakout_state"],
                "breadth_state": row["breadth_state"],
                "capital_state": row["capital_state"],
                "tradability_label": row["tradability_label"],
                "final_training_admission": row["final_training_admission"],
                "strict_supervisor_conclusion": rule.strict_supervisor_conclusion,
            }
        )

    if len(output_rows) != len(RULES):
        raise ValueError("Leader/follower mapping for window 008 is incomplete.")

    summary_rows = [
        {
            "sample_window_id": "ca_train_window_008",
            "december_leader_count": sum(
                1
                for row in output_rows
                if row["structure_phase"] == "december_forum_diffusion"
                and row["leader_follower_class"] == "leader"
            ),
            "december_follower_count": sum(
                1
                for row in output_rows
                if row["structure_phase"] == "december_forum_diffusion"
                and row["leader_follower_class"] == "follower"
            ),
            "february_leader_deterioration_count": sum(
                1 for row in output_rows if row["leader_follower_class"] == "leader_deterioration"
            ),
            "february_follower_failure_count": sum(
                1 for row in output_rows if row["leader_follower_class"] == "follower_failure"
            ),
            "excluded_soft_candidate_count": 1,
            "final_training_admission": "subwindow_ready_but_full_window_not_ready",
            "strict_supervisor_conclusion": (
                "Window 008 now has one December leader, three December followers, and a February failure map; "
                "this is enough to study diffusion-versus-failed-followthrough, but still not enough for a full-window final-training pass."
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
        / "commercial_aerospace_202511_202604_window_leader_follower_structure_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_leader_follower_summary_v1.csv"
    )
    _write_csv(output_path, output_rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(output_rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
