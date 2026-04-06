from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_overlap_resolver import (
    resolve_theme_governance,
)


OFFICIAL_GUIDANCE_KEYWORDS = (
    "国务院",
    "国常会",
    "证监会",
    "中国人民银行",
    "央行",
    "财政部",
    "发改委",
    "工信部",
    "商务部",
    "国资委",
    "上交所",
    "深交所",
    "金融监管总局",
    "国家统计局",
    "海关总署",
)

MACRO_CALENDAR_KEYWORDS = (
    "CPI",
    "PPI",
    "外汇储备",
    "非农",
    "利率决议",
    "议息",
)

NEGATIVE_SHOCK_KEYWORDS = (
    "被击中",
    "战争",
    "冲突",
    "停牌",
    "减持",
    "处罚",
    "制裁",
    "下调",
    "暴跌",
    "风险",
)

POSITIVE_TRIGGER_KEYWORDS = (
    "支持",
    "实施",
    "发射",
    "中标",
    "订单",
    "回购",
    "增持",
    "突破",
    "上调",
    "利好",
)

BOARD_EXPLICIT_HINTS = ("板块", "概念", "题材", "行业", "赛道")

THEME_KEYWORDS = {
    "商业航天": ("商业航天", "commercial_aerospace"),
    "航天": ("商业航天", "commercial_aerospace"),
    "卫星": ("商业航天", "commercial_aerospace"),
    "火箭": ("商业航天", "commercial_aerospace"),
    "军工": ("军工", "defense_industry"),
    "导弹": ("军工", "defense_industry"),
    "无人机": ("军工", "defense_industry"),
    "原油": ("油气", "oil_gas"),
    "天然气": ("油气", "oil_gas"),
    "石油": ("油气", "oil_gas"),
    "黄金": ("黄金", "gold"),
    "AI": ("人工智能", "ai"),
    "OpenAI": ("人工智能", "ai"),
    "算力": ("人工智能", "ai"),
    "芯片": ("半导体", "semiconductor"),
    "半导体": ("半导体", "semiconductor"),
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _latest_concept_symbol_map(concept_rows: list[dict[str, str]]) -> dict[str, list[str]]:
    if not concept_rows:
        return {}
    latest_trade_date = max(row["trade_date"] for row in concept_rows)
    filtered = [row for row in concept_rows if row["trade_date"] == latest_trade_date]
    grouped: dict[str, list[tuple[str, float, int]]] = {}
    for row in filtered:
        concept_name = row["concept_name"]
        weight = float(row["weight"] or 0.0)
        primary_rank = 1 if str(row["is_primary_concept"]).lower() == "true" else 0
        grouped.setdefault(concept_name, []).append((row["symbol"], weight, primary_rank))

    result: dict[str, list[str]] = {}
    for concept_name, values in grouped.items():
        ranked = sorted(values, key=lambda item: (-item[2], -item[1], item[0]))
        deduped: list[str] = []
        for symbol, _, _ in ranked:
            if symbol not in deduped:
                deduped.append(symbol)
        result[concept_name] = deduped
    return result


def _classify_domain(text: str) -> str:
    if _contains_any(text, OFFICIAL_GUIDANCE_KEYWORDS):
        return "policy_regulatory"
    if _contains_any(text, MACRO_CALENDAR_KEYWORDS):
        return "macro_calendar"
    if _contains_any(text, ("原油", "天然气", "石油", "黄金")):
        return "commodity_macro"
    if _contains_any(text, ("伊朗", "美国", "以色列", "俄罗斯", "乌克兰", "中东", "哈马斯", "特朗普")):
        return "geopolitical_macro"
    if any(keyword in text for keyword in THEME_KEYWORDS):
        return "theme_specific"
    return "general_market_news"


def _detect_theme(text: str, domain: str) -> tuple[str, str, str]:
    explicit_theme_context = _contains_any(text, BOARD_EXPLICIT_HINTS)
    for keyword, mapped in THEME_KEYWORDS.items():
        if keyword not in text:
            continue
        if domain in {"geopolitical_macro", "commodity_macro", "macro_calendar"} and not explicit_theme_context:
            continue
        confidence = "high" if explicit_theme_context else "medium"
        return mapped[0], mapped[1], confidence
    return ("全市场", "broad_market", "none")


def _classify_direction(text: str) -> str:
    if _contains_any(text, NEGATIVE_SHOCK_KEYWORDS):
        return "negative_or_risk_off"
    if _contains_any(text, POSITIVE_TRIGGER_KEYWORDS):
        return "positive_or_risk_on"
    if _contains_any(text, MACRO_CALENDAR_KEYWORDS):
        return "scheduled_watch"
    return "uncertain"


def _classify_strength(signal_class: str, domain: str, text: str) -> str:
    if domain in {"policy_regulatory", "macro_calendar"}:
        return "decisive"
    if signal_class == "market_moving_candidate":
        return "strong"
    if _contains_any(text, ("突发", "重磅", "紧急")):
        return "strong"
    return "moderate"


def _classify_guidance_class(domain: str, direction: str, target_theme_slug: str) -> str:
    if domain in {"policy_regulatory", "macro_calendar"}:
        return "guidance_event"
    if domain in {"commodity_macro", "geopolitical_macro"}:
        return "risk_event"
    if target_theme_slug != "broad_market" and direction == "positive_or_risk_on":
        return "trigger_event"
    if target_theme_slug != "broad_market":
        return "watch_only_guidance"
    return "confirmation_event"


def _target_scope(domain: str, target_theme_slug: str) -> str:
    if domain in {"policy_regulatory", "macro_calendar", "commodity_macro", "geopolitical_macro"}:
        return "market_or_macro"
    if target_theme_slug != "broad_market":
        return "board_theme"
    return "market_watch"


def _routing_bucket(guidance_class: str, strength: str) -> str:
    if guidance_class == "guidance_event":
        return "guidance_layer"
    if guidance_class == "risk_event":
        return "risk_layer"
    if guidance_class == "trigger_event" and strength in {"strong", "decisive"}:
        return "board_trigger_layer"
    return "watch_layer"


def _guidance_priority(guidance_class: str, strength: str) -> str:
    if guidance_class == "guidance_event" and strength == "decisive":
        return "p0"
    if guidance_class in {"risk_event", "trigger_event"} and strength in {"strong", "decisive"}:
        return "p1"
    if guidance_class in {"risk_event", "trigger_event", "watch_only_guidance"}:
        return "p2"
    return "p3"


def _action_bias(guidance_class: str, direction: str, target_theme_slug: str) -> str:
    if guidance_class == "guidance_event":
        return "update_market_guidance"
    if guidance_class == "risk_event":
        return "tighten_risk_or_board_veto"
    if guidance_class == "trigger_event" and target_theme_slug != "broad_market":
        return "upgrade_board_watch"
    if direction == "scheduled_watch":
        return "calendar_watch"
    return "observe_only"


def _authority_weight(source_name: str, event_domain: str) -> float:
    if event_domain == "policy_regulatory":
        return 1.0
    if source_name == "财联社电报":
        return 0.8
    return 0.6


def _direction_score(event_direction: str) -> float:
    if event_direction == "positive_or_risk_on":
        return 1.0
    if event_direction == "negative_or_risk_off":
        return -1.0
    return 0.0


def _strength_score(event_strength: str) -> float:
    if event_strength == "decisive":
        return 3.0
    if event_strength == "strong":
        return 2.0
    return 1.0


def _class_weight(guidance_class: str) -> float:
    if guidance_class == "guidance_event":
        return 1.3
    if guidance_class == "trigger_event":
        return 1.1
    if guidance_class == "risk_event":
        return 1.0
    return 0.6


def _decision_direction_score(guidance_class: str, event_direction: str) -> float:
    if guidance_class == "risk_event":
        if event_direction == "uncertain":
            return -0.5
        return -1.0
    return _direction_score(event_direction)


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsTradingGuidanceV1:
    summary: dict[str, Any]
    guidance_rows: list[dict[str, Any]]
    board_rows: list[dict[str, Any]]
    market_guidance_rows: list[dict[str, Any]]
    board_signal_rows: list[dict[str, Any]]
    risk_queue_rows: list[dict[str, Any]]
    decision_signal_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsTradingGuidanceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.fastlane_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_fastlane_surface_v1.csv"
        )
        self.concept_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_concept_membership_v1.csv"
        )
        self.guidance_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_trading_guidance_surface_v1.csv"
        )
        self.board_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_board_guidance_summary_v1.csv"
        )
        self.market_guidance_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_market_guidance_surface_v1.csv"
        )
        self.board_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_board_signal_surface_v1.csv"
        )
        self.risk_queue_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_risk_queue_surface_v1.csv"
        )
        self.decision_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_decision_signal_surface_v1.csv"
        )
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_trading_guidance_view_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else ["row_state"]
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsTradingGuidanceV1:
        fastlane_rows = _read_csv(self.fastlane_path)
        concept_rows = _read_csv(self.concept_path)
        concept_symbol_map = _latest_concept_symbol_map(concept_rows)

        guidance_rows: list[dict[str, Any]] = []
        board_summary: dict[str, dict[str, Any]] = {}

        for row in fastlane_rows:
            text = f"{row['title']} {row['brief']}"
            domain = _classify_domain(text)
            target_board, target_theme_slug, theme_binding_confidence = _detect_theme(text, domain)
            primary_theme_slug, secondary_theme_slug, theme_governance_state = resolve_theme_governance(
                self.repo_root,
                target_theme_slug,
            )
            direction = _classify_direction(text)
            strength = _classify_strength(row["signal_class"], domain, text)
            guidance_class = _classify_guidance_class(domain, direction, target_theme_slug)
            scope = _target_scope(domain, target_theme_slug)
            routing_bucket = _routing_bucket(guidance_class, strength)
            guidance_priority = _guidance_priority(guidance_class, strength)
            action_bias = _action_bias(guidance_class, direction, target_theme_slug)
            candidate_symbols = (
                "|".join(concept_symbol_map.get(target_board, [])[:5])
                if target_board != "全市场" and theme_binding_confidence != "none"
                else ""
            )

            guidance_rows.append(
                {
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "source_name": row["source_name"],
                    "source_role": "fast_news_primary",
                    "event_domain": domain,
                    "target_scope": scope,
                    "target_board": target_board,
                    "target_theme_slug": target_theme_slug,
                    "primary_theme_slug": primary_theme_slug,
                    "secondary_theme_slug": secondary_theme_slug,
                    "theme_governance_state": theme_governance_state,
                    "theme_binding_confidence": theme_binding_confidence,
                    "guidance_class": guidance_class,
                    "event_direction": direction,
                    "event_strength": strength,
                    "guidance_priority": guidance_priority,
                    "action_bias": action_bias,
                    "routing_bucket": routing_bucket,
                    "candidate_beneficiary_symbols": candidate_symbols,
                    "delivery_state": "trading_guidance_surface_ready",
                    "title": row["title"],
                    "brief": row["brief"],
                }
            )

            summary_row = board_summary.setdefault(
                target_theme_slug,
                {
                    "target_theme_slug": target_theme_slug,
                    "primary_theme_slug": primary_theme_slug,
                    "secondary_theme_slug": secondary_theme_slug,
                    "theme_governance_state": theme_governance_state,
                    "target_board": target_board,
                    "theme_binding_confidence": theme_binding_confidence,
                    "guidance_event_count": 0,
                    "risk_event_count": 0,
                    "trigger_event_count": 0,
                    "watch_event_count": 0,
                },
            )
            if guidance_class == "guidance_event":
                summary_row["guidance_event_count"] += 1
            elif guidance_class == "risk_event":
                summary_row["risk_event_count"] += 1
            elif guidance_class == "trigger_event":
                summary_row["trigger_event_count"] += 1
            else:
                summary_row["watch_event_count"] += 1

        board_rows = list(board_summary.values())

        market_guidance_rows = [
            {
                "telegraph_id": row["telegraph_id"],
                "public_ts": row["public_ts"],
                "target_scope": row["target_scope"],
                "target_board": row["target_board"],
                "target_theme_slug": row["target_theme_slug"],
                "primary_theme_slug": row["primary_theme_slug"],
                "secondary_theme_slug": row["secondary_theme_slug"],
                "theme_governance_state": row["theme_governance_state"],
                "guidance_class": row["guidance_class"],
                "event_direction": row["event_direction"],
                "event_strength": row["event_strength"],
                "guidance_priority": row["guidance_priority"],
                "action_bias": row["action_bias"],
                "delivery_state": "market_guidance_ready",
                "title": row["title"],
            }
            for row in guidance_rows
            if row["guidance_class"] == "guidance_event"
        ]

        board_signal_rows = [
            {
                "telegraph_id": row["telegraph_id"],
                "public_ts": row["public_ts"],
                "target_board": row["target_board"],
                "target_theme_slug": row["target_theme_slug"],
                "primary_theme_slug": row["primary_theme_slug"],
                "secondary_theme_slug": row["secondary_theme_slug"],
                "theme_governance_state": row["theme_governance_state"],
                "theme_binding_confidence": row["theme_binding_confidence"],
                "guidance_class": row["guidance_class"],
                "event_direction": row["event_direction"],
                "event_strength": row["event_strength"],
                "guidance_priority": row["guidance_priority"],
                "candidate_beneficiary_symbols": row["candidate_beneficiary_symbols"],
                "delivery_state": "board_signal_ready",
                "title": row["title"],
            }
            for row in guidance_rows
            if row["target_theme_slug"] != "broad_market"
        ]

        risk_queue_rows = [
            {
                "telegraph_id": row["telegraph_id"],
                "public_ts": row["public_ts"],
                "event_domain": row["event_domain"],
                "target_scope": row["target_scope"],
                "event_direction": row["event_direction"],
                "event_strength": row["event_strength"],
                "guidance_priority": row["guidance_priority"],
                "action_bias": row["action_bias"],
                "delivery_state": "risk_queue_ready",
                "title": row["title"],
            }
            for row in guidance_rows
            if row["guidance_class"] == "risk_event"
        ]

        decision_signal_rows = []
        for row in guidance_rows:
            authority_weight = _authority_weight(row["source_name"], row["event_domain"])
            direction_score = _decision_direction_score(row["guidance_class"], row["event_direction"])
            strength_score = _strength_score(row["event_strength"])
            class_weight = _class_weight(row["guidance_class"])
            decision_signal_score = round(authority_weight * direction_score * strength_score * class_weight, 4)
            decision_signal_rows.append(
                {
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "target_scope": row["target_scope"],
                    "target_board": row["target_board"],
                    "target_theme_slug": row["target_theme_slug"],
                    "primary_theme_slug": row["primary_theme_slug"],
                    "secondary_theme_slug": row["secondary_theme_slug"],
                    "theme_governance_state": row["theme_governance_state"],
                    "guidance_class": row["guidance_class"],
                    "event_direction": row["event_direction"],
                    "event_strength": row["event_strength"],
                    "guidance_priority": row["guidance_priority"],
                    "action_bias": row["action_bias"],
                    "authority_weight": f"{authority_weight:.2f}",
                    "direction_score": f"{direction_score:.1f}",
                    "strength_score": f"{strength_score:.1f}",
                    "class_weight": f"{class_weight:.2f}",
                    "decision_signal_score": f"{decision_signal_score:.4f}",
                    "delivery_state": "decision_signal_ready",
                    "title": row["title"],
                }
            )

        self._write_csv(self.guidance_path, guidance_rows)
        self._write_csv(self.board_path, board_rows)
        self._write_csv(self.market_guidance_path, market_guidance_rows)
        self._write_csv(self.board_signal_path, board_signal_rows)
        self._write_csv(self.risk_queue_path, risk_queue_rows)
        self._write_csv(self.decision_signal_path, decision_signal_rows)

        serving_rows = [
            {
                "view_id": "internal_hot_news_trading_guidance_surface",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.guidance_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            },
            {
                "view_id": "internal_hot_news_market_guidance_surface",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.market_guidance_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            },
            {
                "view_id": "internal_hot_news_board_signal_surface",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.board_signal_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            },
            {
                "view_id": "internal_hot_news_risk_queue_surface",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.risk_queue_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            },
            {
                "view_id": "internal_hot_news_decision_signal_surface",
                "consumer_mode": "research_shadow",
                "artifact_path": str(self.decision_signal_path.relative_to(self.repo_root)),
                "view_state": "read_ready_internal_only",
            },
        ]
        self.serving_path.parent.mkdir(parents=True, exist_ok=True)
        with self.serving_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(serving_rows[0].keys()))
            writer.writeheader()
            writer.writerows(serving_rows)

        summary = {
            "guidance_row_count": len(guidance_rows),
            "board_summary_count": len(board_rows),
            "guidance_event_count": sum(row["guidance_class"] == "guidance_event" for row in guidance_rows),
            "risk_event_count": sum(row["guidance_class"] == "risk_event" for row in guidance_rows),
            "trigger_event_count": sum(row["guidance_class"] == "trigger_event" for row in guidance_rows),
            "market_guidance_row_count": len(market_guidance_rows),
            "board_signal_row_count": len(board_signal_rows),
            "risk_queue_row_count": len(risk_queue_rows),
            "decision_signal_row_count": len(decision_signal_rows),
            "artifact_path": str(self.guidance_path.relative_to(self.repo_root)),
            "board_summary_path": str(self.board_path.relative_to(self.repo_root)),
        }
        return MaterializedAShareInternalHotNewsTradingGuidanceV1(
            summary=summary,
            guidance_rows=guidance_rows,
            board_rows=board_rows,
            market_guidance_rows=market_guidance_rows,
            board_signal_rows=board_signal_rows,
            risk_queue_rows=risk_queue_rows,
            decision_signal_rows=decision_signal_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsTradingGuidanceV1(repo_root).materialize()
    print(result.summary["artifact_path"])


if __name__ == "__main__":
    main()
