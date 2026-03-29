from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from a_share_quant.common.models import (
    ConceptMappingRecord,
    DailyBar,
    MainlineWindow,
    SectorMappingRecord,
    SectorSnapshot,
    StockSnapshot,
)
from a_share_quant.data.loaders import (
    load_concept_mapping_from_csv,
    load_sector_mapping_from_csv,
)


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _safe_stdev(values: list[float]) -> float:
    return pstdev(values) if len(values) > 1 else 0.0


def _relative_rank(value: float, values: list[float]) -> float:
    if len(values) <= 1:
        return 0.5
    ordered = sorted(values)
    matches = [index for index, candidate in enumerate(ordered) if candidate == value]
    if not matches:
        return 0.5
    average_index = sum(matches) / len(matches)
    return average_index / (len(ordered) - 1)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


@dataclass(slots=True)
class BootstrapDerivedConfig:
    bars_csv: Path
    mapping_input_csv: Path | None
    concept_mapping_input_csv: Path | None
    mapping_output_csv: Path
    sector_snapshots_output_csv: Path
    stock_snapshots_output_csv: Path
    mainline_windows_output_csv: Path
    mapping_source: str
    mapping_version: str
    protocol_version: str
    sector_assignments: dict[str, dict[str, str]]
    lookback: int
    top_sector_score_threshold: float
    top_sector_rank_limit: int
    min_window_length: int
    concept_support_late_quality_boost: float = 0.0
    concept_support_primary_weight_influence: float = 0.7
    concept_support_multi_concept_influence: float = 0.3
    concept_support_band_lower: float = 0.0
    concept_support_band_upper: float = 1.0
    concept_support_cap_to_band_upper: bool = False

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "BootstrapDerivedConfig":
        paths = config["paths"]
        sector_assignments = {
            str(symbol): {
                "sector_id": str(values["sector_id"]),
                "sector_name": str(values["sector_name"]),
            }
            for symbol, values in config.get("sector_assignments", {}).items()
        }
        rules = config.get("rules", {})
        return cls(
            bars_csv=Path(paths["bars_csv"]),
            mapping_input_csv=Path(paths["mapping_input_csv"]) if paths.get("mapping_input_csv") else None,
            concept_mapping_input_csv=Path(paths["concept_mapping_input_csv"]) if paths.get("concept_mapping_input_csv") else None,
            mapping_output_csv=Path(paths["mapping_output_csv"]),
            sector_snapshots_output_csv=Path(paths["sector_snapshots_output_csv"]),
            stock_snapshots_output_csv=Path(paths["stock_snapshots_output_csv"]),
            mainline_windows_output_csv=Path(paths["mainline_windows_output_csv"]),
            mapping_source=str(config.get("mapping_source", "manual_bootstrap")),
            mapping_version=str(config.get("mapping_version", "bootstrap_v1")),
            protocol_version=str(config.get("protocol_version", "protocol_v1.0")),
            sector_assignments=sector_assignments,
            lookback=int(rules.get("lookback", 5)),
            top_sector_score_threshold=float(rules.get("top_sector_score_threshold", 0.55)),
            top_sector_rank_limit=int(rules.get("top_sector_rank_limit", 1)),
            min_window_length=int(rules.get("min_window_length", 2)),
            concept_support_late_quality_boost=float(
                rules.get("concept_support_late_quality_boost", 0.0)
            ),
            concept_support_primary_weight_influence=float(
                rules.get("concept_support_primary_weight_influence", 0.7)
            ),
            concept_support_multi_concept_influence=float(
                rules.get("concept_support_multi_concept_influence", 0.3)
            ),
            concept_support_band_lower=float(rules.get("concept_support_band_lower", 0.0)),
            concept_support_band_upper=float(rules.get("concept_support_band_upper", 1.0)),
            concept_support_cap_to_band_upper=bool(
                rules.get("concept_support_cap_to_band_upper", False)
            ),
        )


class BootstrapDerivedDataBuilder:
    """Build first-pass derived research tables from local bootstrap bars."""

    def __init__(self, config: BootstrapDerivedConfig) -> None:
        self.config = config

    def build(self, bars: list[DailyBar]) -> dict[str, Path]:
        mappings = self._build_sector_mappings(bars)
        sector_snapshots = self._build_sector_snapshots(bars, mappings)
        concept_records = self._load_concept_records()
        stock_snapshots = self._build_stock_snapshots(
            bars,
            mappings,
            sector_snapshots,
            concept_records,
        )
        mainline_windows = self._build_mainline_windows(bars, mappings, sector_snapshots)
        return {
            "sector_mapping_daily": self._write_sector_mappings(mappings),
            "sector_snapshots": self._write_sector_snapshots(sector_snapshots),
            "stock_snapshots": self._write_stock_snapshots(stock_snapshots),
            "mainline_windows": self._write_mainline_windows(mainline_windows),
        }

    def _build_sector_mappings(self, bars: list[DailyBar]) -> list[SectorMappingRecord]:
        base_records: list[SectorMappingRecord]
        if self.config.mapping_input_csv is not None and self.config.mapping_input_csv.exists():
            base_records = load_sector_mapping_from_csv(self.config.mapping_input_csv)
        else:
            rows: list[SectorMappingRecord] = []
            for bar in bars:
                assignment = self.config.sector_assignments.get(bar.symbol)
                if assignment is None:
                    continue
                rows.append(
                    SectorMappingRecord(
                        trade_date=bar.trade_date,
                        symbol=bar.symbol,
                        sector_id=assignment["sector_id"],
                        sector_name=assignment["sector_name"],
                        mapping_source=self.config.mapping_source,
                        mapping_version=self.config.mapping_version,
                    )
                )
            base_records = rows

        if self.config.concept_mapping_input_csv is not None and self.config.concept_mapping_input_csv.exists():
            concept_records = load_concept_mapping_from_csv(self.config.concept_mapping_input_csv)
            return self._overlay_primary_concepts(base_records, concept_records)

        return base_records

    def _overlay_primary_concepts(
        self,
        base_records: list[SectorMappingRecord],
        concept_records: list[ConceptMappingRecord],
    ) -> list[SectorMappingRecord]:
        primary_concepts = {
            (record.trade_date, record.symbol): record
            for record in concept_records
            if record.is_primary_concept
        }
        records: list[SectorMappingRecord] = []
        for record in base_records:
            concept = primary_concepts.get((record.trade_date, record.symbol))
            if concept is None:
                records.append(record)
                continue
            records.append(
                SectorMappingRecord(
                    trade_date=record.trade_date,
                    symbol=record.symbol,
                    sector_id=concept.concept_id,
                    sector_name=concept.concept_name,
                    mapping_source=concept.mapping_source,
                    mapping_version=concept.mapping_version,
                )
            )
        return records

    def _build_sector_snapshots(
        self,
        bars: list[DailyBar],
        mappings: list[SectorMappingRecord],
    ) -> list[SectorSnapshot]:
        bars_by_symbol = self._bars_by_symbol(bars)
        mapping_by_date_sector: dict[tuple[date, str], list[SectorMappingRecord]] = {}
        for mapping in mappings:
            mapping_by_date_sector.setdefault((mapping.trade_date, mapping.sector_id), []).append(mapping)

        trade_dates = sorted({bar.trade_date for bar in bars})
        snapshots: list[SectorSnapshot] = []
        for trade_date in trade_dates:
            trade_date_records = {
                key[1]: records
                for key, records in mapping_by_date_sector.items()
                if key[0] == trade_date
            }
            if not trade_date_records:
                continue

            day_sector_returns: dict[str, list[float]] = {}
            day_sector_turnovers: dict[str, list[float]] = {}
            cross_section_returns: list[float] = []
            for sector_id, records in trade_date_records.items():
                for mapping in records:
                    bar = self._bar_on_date(bars_by_symbol.get(mapping.symbol, []), trade_date)
                    if bar is None or bar.pre_close <= 0:
                        continue
                    daily_return = (bar.close / bar.pre_close) - 1.0
                    cross_section_returns.append(daily_return)
                    day_sector_returns.setdefault(sector_id, []).append(daily_return)
                    day_sector_turnovers.setdefault(sector_id, []).append(bar.turnover)

            if not cross_section_returns:
                continue

            max_turnover = max(
                sum(turnovers) for turnovers in day_sector_turnovers.values() if turnovers
            ) or 1.0
            market_avg_return = _safe_mean(cross_section_returns)

            for sector_id, records in trade_date_records.items():
                sector_name = records[0].sector_name
                symbols = [record.symbol for record in records]
                trailing_returns = [
                    self._trailing_return(bars_by_symbol.get(symbol, []), trade_date)
                    for symbol in symbols
                ]
                trailing_returns = [value for value in trailing_returns if value is not None]
                daily_returns = day_sector_returns.get(sector_id, [])
                if not daily_returns:
                    continue
                persistence = _clamp(sum(value > 0 for value in trailing_returns) / max(len(trailing_returns), 1))
                diffusion = _clamp(sum(value > 0 for value in daily_returns) / len(daily_returns))
                money_making = _clamp((_safe_mean(daily_returns) + 0.05) / 0.10)
                leader_strength = _clamp((max(daily_returns) + 0.05) / 0.10)
                relative_strength = _clamp(((_safe_mean(daily_returns) - market_avg_return) + 0.05) / 0.10)
                activity = _clamp(sum(day_sector_turnovers.get(sector_id, [])) / max_turnover)
                snapshots.append(
                    SectorSnapshot(
                        trade_date=trade_date,
                        sector_id=sector_id,
                        sector_name=sector_name,
                        persistence=round(persistence, 6),
                        diffusion=round(diffusion, 6),
                        money_making=round(money_making, 6),
                        leader_strength=round(leader_strength, 6),
                        relative_strength=round(relative_strength, 6),
                        activity=round(activity, 6),
                    )
                )
        return snapshots

    def _build_stock_snapshots(
        self,
        bars: list[DailyBar],
        mappings: list[SectorMappingRecord],
        sector_snapshots: list[SectorSnapshot],
        concept_records: list[ConceptMappingRecord] | None = None,
    ) -> list[StockSnapshot]:
        bars_by_symbol = self._bars_by_symbol(bars)
        sector_strength_by_date = {
            (snapshot.trade_date, snapshot.sector_id): snapshot
            for snapshot in sector_snapshots
        }
        concept_support_by_key = self._concept_support_by_key(concept_records or [])
        trade_dates = sorted({bar.trade_date for bar in bars})
        total_turnover_by_date = {
            trade_date: sum(bar.turnover for bar in bars if bar.trade_date == trade_date) or 1.0
            for trade_date in trade_dates
        }
        mappings_by_date_sector: dict[tuple[date, str], list[SectorMappingRecord]] = {}
        for mapping in mappings:
            mappings_by_date_sector.setdefault((mapping.trade_date, mapping.sector_id), []).append(mapping)

        snapshots: list[StockSnapshot] = []
        for (trade_date, sector_id), sector_mappings in sorted(mappings_by_date_sector.items()):
            sector_snapshot = sector_strength_by_date.get((trade_date, sector_id))
            sector_strength = (
                (
                    sector_snapshot.persistence
                    + sector_snapshot.diffusion
                    + sector_snapshot.money_making
                    + sector_snapshot.leader_strength
                    + sector_snapshot.relative_strength
                    + sector_snapshot.activity
                )
                / 6.0
                if sector_snapshot is not None
                else 0.5
            )
            sector_heat = (
                (
                    sector_snapshot.activity
                    + sector_snapshot.leader_strength
                    + sector_snapshot.money_making
                    + sector_snapshot.relative_strength
                )
                / 4.0
                if sector_snapshot is not None
                else 0.5
            )
            sector_breadth = (
                (sector_snapshot.persistence + sector_snapshot.diffusion) / 2.0
                if sector_snapshot is not None
                else 0.5
            )

            raw_metrics: list[tuple[SectorMappingRecord, DailyBar, float, float, float]] = []
            for mapping in sector_mappings:
                bar_series = bars_by_symbol.get(mapping.symbol, [])
                bar = self._bar_on_date(bar_series, trade_date)
                if bar is None or bar.pre_close <= 0:
                    continue
                trailing_return = self._trailing_return(bar_series, trade_date) or 0.0
                current_return = (bar.close / bar.pre_close) - 1.0
                volatility = _safe_stdev(self._trailing_window_returns(bar_series, trade_date))
                raw_metrics.append((mapping, bar, trailing_return, current_return, volatility))

            if not raw_metrics:
                continue

            trailing_returns = [item[2] for item in raw_metrics]
            current_returns = [item[3] for item in raw_metrics]
            turnovers = [item[1].turnover for item in raw_metrics]
            sector_turnover_total = sum(turnovers) or 1.0
            sector_top_turnover_share = max(turnovers) / sector_turnover_total
            sector_mean_turnover_share = sector_turnover_total / len(turnovers) / sector_turnover_total

            for mapping, bar, trailing_return, current_return, volatility in raw_metrics:
                trailing_rank = _relative_rank(trailing_return, trailing_returns)
                current_rank = _relative_rank(current_return, current_returns)
                turnover_rank = _relative_rank(bar.turnover, turnovers)
                sector_turnover_share = _clamp(bar.turnover / sector_turnover_total)
                turnover_concentration = _clamp(
                    0.65 * sector_top_turnover_share
                    + 0.35 * max(0.0, sector_top_turnover_share - sector_mean_turnover_share)
                )

                expected_upside = _clamp(
                    0.65 * _clamp((trailing_return + 0.10) / 0.20)
                    + 0.35 * trailing_rank
                )
                drive_strength = _clamp(
                    0.65 * _clamp((current_return + 0.05) / 0.10)
                    + 0.35 * current_rank
                )
                stability = _clamp(1.0 - (volatility / 0.06))
                turnover_share = _clamp(bar.turnover / total_turnover_by_date[trade_date])
                liquidity = _clamp(
                    0.60 * turnover_share
                    + 0.40 * turnover_rank
                )
                lag_balance = _clamp(1.0 - (abs(trailing_rank - 0.45) / 0.45))
                trend_support = _clamp((trailing_return + 0.02) / 0.12)
                late_quality_sector_contribution = 0.30 * sector_strength
                late_quality_stability_contribution = 0.25 * stability
                late_quality_liquidity_contribution = 0.20 * liquidity
                late_quality_lag_contribution = 0.15 * lag_balance
                late_quality_trend_contribution = 0.10 * trend_support
                late_quality_raw_score = _clamp(
                    late_quality_sector_contribution
                    + late_quality_stability_contribution
                    + late_quality_liquidity_contribution
                    + late_quality_lag_contribution
                    + late_quality_trend_contribution
                )
                late_mover_quality = late_quality_raw_score
                concept_metrics = concept_support_by_key.get((trade_date, mapping.symbol), {})
                concept_support = float(concept_metrics.get("concept_support", 0.0))
                theme_density = _clamp(
                    concept_support
                    * min(float(concept_metrics.get("concept_count", 0)) / 3.0, 1.0)
                )
                theme_turnover_interaction = _clamp(
                    0.60 * theme_density + 0.40 * turnover_concentration
                )
                concept_boost = 0.0
                if (
                    self.config.concept_support_band_lower
                    <= late_mover_quality
                    < self.config.concept_support_band_upper
                ):
                    concept_boost = self.config.concept_support_late_quality_boost * concept_support
                    late_mover_quality = late_mover_quality + concept_boost
                    if self.config.concept_support_cap_to_band_upper:
                        late_mover_quality = min(
                            late_mover_quality,
                            self.config.concept_support_band_upper,
                        )
                    late_mover_quality = _clamp(late_mover_quality)
                resonance = _clamp(
                    0.35 * sector_strength
                    + 0.25 * expected_upside
                    + 0.20 * drive_strength
                    + 0.20 * stability
                )
                leader_component_score = _clamp(
                    0.45 * expected_upside
                    + 0.35 * drive_strength
                    + 0.20 * resonance
                )
                core_component_score = _clamp(
                    0.40 * stability
                    + 0.35 * liquidity
                    + 0.25 * resonance
                )
                late_component_score = _clamp(
                    0.40 * late_mover_quality
                    + 0.30 * expected_upside
                    + 0.30 * resonance
                )
                non_junk_composite_score = max(
                    leader_component_score,
                    core_component_score,
                    late_component_score,
                )
                snapshots.append(
                    StockSnapshot(
                        trade_date=trade_date,
                        symbol=mapping.symbol,
                        sector_id=mapping.sector_id,
                        sector_name=mapping.sector_name,
                        expected_upside=round(expected_upside, 6),
                        drive_strength=round(drive_strength, 6),
                        stability=round(stability, 6),
                        liquidity=round(liquidity, 6),
                        late_mover_quality=round(late_mover_quality, 6),
                        resonance=round(resonance, 6),
                        concept_support=round(concept_support, 6),
                        primary_concept_weight=round(
                            float(concept_metrics.get("primary_concept_weight", 0.0)),
                            6,
                        ),
                        concept_count=int(concept_metrics.get("concept_count", 0)),
                        concept_concentration_ratio=round(
                            float(concept_metrics.get("concept_concentration_ratio", 0.0)),
                            6,
                        ),
                        leader_component_score=round(leader_component_score, 6),
                        core_component_score=round(core_component_score, 6),
                        late_component_score=round(late_component_score, 6),
                        non_junk_composite_score=round(non_junk_composite_score, 6),
                        late_quality_raw_score=round(late_quality_raw_score, 6),
                        late_quality_concept_boost=round(concept_boost, 6),
                        late_quality_sector_strength=round(sector_strength, 6),
                        late_quality_lag_balance=round(lag_balance, 6),
                        late_quality_trend_support=round(trend_support, 6),
                        stability_volatility=round(volatility, 6),
                        liquidity_turnover_share=round(turnover_share, 6),
                        liquidity_turnover_rank=round(turnover_rank, 6),
                        liquidity_sector_turnover_share=round(sector_turnover_share, 6),
                        liquidity_sector_top_turnover_share=round(
                            sector_top_turnover_share, 6
                        ),
                        liquidity_sector_mean_turnover_share=round(
                            sector_mean_turnover_share, 6
                        ),
                        liquidity_sector_turnover_share_gap=round(
                            sector_top_turnover_share - sector_turnover_share,
                            6,
                        ),
                        liquidity_sector_symbol_count=len(raw_metrics),
                        context_theme_density=round(theme_density, 6),
                        context_turnover_concentration=round(
                            turnover_concentration, 6
                        ),
                        context_theme_turnover_interaction=round(
                            theme_turnover_interaction, 6
                        ),
                        context_sector_heat=round(sector_heat, 6),
                        context_sector_breadth=round(sector_breadth, 6),
                        late_quality_sector_contribution=round(
                            late_quality_sector_contribution, 6
                        ),
                        late_quality_stability_contribution=round(
                            late_quality_stability_contribution, 6
                        ),
                        late_quality_liquidity_contribution=round(
                            late_quality_liquidity_contribution, 6
                        ),
                        late_quality_lag_contribution=round(
                            late_quality_lag_contribution, 6
                        ),
                        late_quality_trend_contribution=round(
                            late_quality_trend_contribution, 6
                        ),
                    )
                )
        return snapshots

    def _load_concept_records(self) -> list[ConceptMappingRecord]:
        if self.config.concept_mapping_input_csv is None or not self.config.concept_mapping_input_csv.exists():
            return []
        return load_concept_mapping_from_csv(self.config.concept_mapping_input_csv)

    def _concept_support_by_key(
        self,
        concept_records: list[ConceptMappingRecord],
    ) -> dict[tuple[date, str], dict[str, float | int]]:
        grouped: dict[tuple[date, str], list[ConceptMappingRecord]] = {}
        for record in concept_records:
            grouped.setdefault((record.trade_date, record.symbol), []).append(record)

        support_by_key: dict[tuple[date, str], dict[str, float | int]] = {}
        for key, records in grouped.items():
            primary_weight = max(
                (
                    float(record.weight)
                    for record in records
                    if record.is_primary_concept
                ),
                default=0.0,
            )
            multi_concept_score = _clamp((len(records) - 1) / 2.0)
            support = _clamp(
                (self.config.concept_support_primary_weight_influence * primary_weight)
                + (self.config.concept_support_multi_concept_influence * multi_concept_score)
            )
            total_weight = sum(float(record.weight) for record in records)
            concentration_ratio = _clamp(primary_weight / total_weight) if total_weight > 0 else 0.0
            support_by_key[key] = {
                "concept_support": support,
                "primary_concept_weight": primary_weight,
                "concept_count": len(records),
                "concept_concentration_ratio": concentration_ratio,
            }
        return support_by_key

    def _build_mainline_windows(
        self,
        bars: list[DailyBar],
        mappings: list[SectorMappingRecord],
        sector_snapshots: list[SectorSnapshot],
    ) -> list[MainlineWindow]:
        bars_by_symbol = self._bars_by_symbol(bars)
        scored_by_date: dict[date, list[tuple[str, float]]] = {}
        for snapshot in sector_snapshots:
            composite = (
                snapshot.persistence
                + snapshot.diffusion
                + snapshot.money_making
                + snapshot.leader_strength
                + snapshot.relative_strength
                + snapshot.activity
            ) / 6.0
            scored_by_date.setdefault(snapshot.trade_date, []).append((snapshot.sector_id, composite))

        qualifying_sectors_by_date: dict[date, set[str]] = {}
        for trade_date, scores in scored_by_date.items():
            ranked = sorted(scores, key=lambda item: item[1], reverse=True)
            qualifying_sectors_by_date[trade_date] = {
                sector_id
                for index, (sector_id, score) in enumerate(ranked, start=1)
                if index <= self.config.top_sector_rank_limit
                and score >= self.config.top_sector_score_threshold
            }

        trade_dates_by_symbol: dict[str, list[date]] = {}
        for mapping in mappings:
            if mapping.sector_id in qualifying_sectors_by_date.get(mapping.trade_date, set()):
                trade_dates_by_symbol.setdefault(mapping.symbol, []).append(mapping.trade_date)

        windows: list[MainlineWindow] = []
        for symbol, trade_dates in trade_dates_by_symbol.items():
            grouped = self._group_consecutive_dates(sorted(trade_dates))
            for index, window_dates in enumerate(grouped, start=1):
                if len(window_dates) < self.config.min_window_length:
                    continue
                start_date = window_dates[0]
                end_date = window_dates[-1]
                series = bars_by_symbol.get(symbol, [])
                start_bar = self._bar_on_date(series, start_date)
                end_bar = self._bar_on_date(series, end_date)
                if start_bar is None or end_bar is None or start_bar.close <= 0:
                    continue
                capturable_return = (end_bar.close / start_bar.close) - 1.0
                windows.append(
                    MainlineWindow(
                        window_id=f"{symbol.lower()}_{index}",
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                        capturable_return=round(capturable_return, 6),
                    )
                )
        return windows

    def _bars_by_symbol(self, bars: list[DailyBar]) -> dict[str, list[DailyBar]]:
        grouped: dict[str, list[DailyBar]] = {}
        for bar in sorted(bars, key=lambda item: (item.symbol, item.trade_date)):
            grouped.setdefault(bar.symbol, []).append(bar)
        return grouped

    def _bar_on_date(self, bars: list[DailyBar], trade_date: date) -> DailyBar | None:
        for bar in bars:
            if bar.trade_date == trade_date:
                return bar
        return None

    def _trailing_return(self, bars: list[DailyBar], trade_date: date) -> float | None:
        window = self._recent_bars(bars, trade_date)
        if len(window) < 2 or window[0].close <= 0:
            return None
        return (window[-1].close / window[0].close) - 1.0

    def _trailing_window_returns(self, bars: list[DailyBar], trade_date: date) -> list[float]:
        window = self._recent_bars(bars, trade_date)
        returns: list[float] = []
        for bar in window:
            if bar.pre_close > 0:
                returns.append((bar.close / bar.pre_close) - 1.0)
        return returns

    def _recent_bars(self, bars: list[DailyBar], trade_date: date) -> list[DailyBar]:
        eligible = [bar for bar in bars if bar.trade_date <= trade_date]
        return eligible[-self.config.lookback :]

    def _group_consecutive_dates(self, trade_dates: list[date]) -> list[list[date]]:
        if not trade_dates:
            return []
        groups: list[list[date]] = [[trade_dates[0]]]
        for current in trade_dates[1:]:
            previous = groups[-1][-1]
            if (current - previous).days <= 4:
                groups[-1].append(current)
            else:
                groups.append([current])
        return groups

    def _write_sector_mappings(self, mappings: list[SectorMappingRecord]) -> Path:
        rows = [
            {
                "trade_date": record.trade_date.isoformat(),
                "symbol": record.symbol,
                "sector_id": record.sector_id,
                "sector_name": record.sector_name,
                "mapping_source": record.mapping_source,
                "mapping_version": record.mapping_version,
            }
            for record in mappings
        ]
        return _write_csv(
            self.config.mapping_output_csv,
            ["trade_date", "symbol", "sector_id", "sector_name", "mapping_source", "mapping_version"],
            rows,
        )

    def _write_sector_snapshots(self, snapshots: list[SectorSnapshot]) -> Path:
        rows = [
            {
                "trade_date": snapshot.trade_date.isoformat(),
                "sector_id": snapshot.sector_id,
                "sector_name": snapshot.sector_name,
                "persistence": snapshot.persistence,
                "diffusion": snapshot.diffusion,
                "money_making": snapshot.money_making,
                "leader_strength": snapshot.leader_strength,
                "relative_strength": snapshot.relative_strength,
                "activity": snapshot.activity,
            }
            for snapshot in snapshots
        ]
        return _write_csv(
            self.config.sector_snapshots_output_csv,
            ["trade_date", "sector_id", "sector_name", "persistence", "diffusion", "money_making", "leader_strength", "relative_strength", "activity"],
            rows,
        )

    def _write_stock_snapshots(self, snapshots: list[StockSnapshot]) -> Path:
        rows = [
            {
                "trade_date": snapshot.trade_date.isoformat(),
                "symbol": snapshot.symbol,
                "sector_id": snapshot.sector_id,
                "sector_name": snapshot.sector_name,
                "expected_upside": snapshot.expected_upside,
                "drive_strength": snapshot.drive_strength,
                "stability": snapshot.stability,
                "liquidity": snapshot.liquidity,
                "late_mover_quality": snapshot.late_mover_quality,
                "resonance": snapshot.resonance,
                "concept_support": snapshot.concept_support,
                "primary_concept_weight": snapshot.primary_concept_weight,
                "concept_count": snapshot.concept_count,
                "concept_concentration_ratio": snapshot.concept_concentration_ratio,
                "leader_component_score": snapshot.leader_component_score,
                "core_component_score": snapshot.core_component_score,
                "late_component_score": snapshot.late_component_score,
                "non_junk_composite_score": snapshot.non_junk_composite_score,
                "late_quality_raw_score": snapshot.late_quality_raw_score,
                "late_quality_concept_boost": snapshot.late_quality_concept_boost,
                "late_quality_sector_strength": snapshot.late_quality_sector_strength,
                "late_quality_lag_balance": snapshot.late_quality_lag_balance,
                "late_quality_trend_support": snapshot.late_quality_trend_support,
                "stability_volatility": snapshot.stability_volatility,
                "liquidity_turnover_share": snapshot.liquidity_turnover_share,
                "liquidity_turnover_rank": snapshot.liquidity_turnover_rank,
                "liquidity_sector_turnover_share": snapshot.liquidity_sector_turnover_share,
                "liquidity_sector_top_turnover_share": snapshot.liquidity_sector_top_turnover_share,
                "liquidity_sector_mean_turnover_share": snapshot.liquidity_sector_mean_turnover_share,
                "liquidity_sector_turnover_share_gap": snapshot.liquidity_sector_turnover_share_gap,
                "liquidity_sector_symbol_count": snapshot.liquidity_sector_symbol_count,
                "context_theme_density": snapshot.context_theme_density,
                "context_turnover_concentration": snapshot.context_turnover_concentration,
                "context_theme_turnover_interaction": snapshot.context_theme_turnover_interaction,
                "context_sector_heat": snapshot.context_sector_heat,
                "context_sector_breadth": snapshot.context_sector_breadth,
                "late_quality_sector_contribution": snapshot.late_quality_sector_contribution,
                "late_quality_stability_contribution": snapshot.late_quality_stability_contribution,
                "late_quality_liquidity_contribution": snapshot.late_quality_liquidity_contribution,
                "late_quality_lag_contribution": snapshot.late_quality_lag_contribution,
                "late_quality_trend_contribution": snapshot.late_quality_trend_contribution,
            }
            for snapshot in snapshots
        ]
        return _write_csv(
            self.config.stock_snapshots_output_csv,
            [
                "trade_date",
                "symbol",
                "sector_id",
                "sector_name",
                "expected_upside",
                "drive_strength",
                "stability",
                "liquidity",
                "late_mover_quality",
                "resonance",
                "concept_support",
                "primary_concept_weight",
                "concept_count",
                "concept_concentration_ratio",
                "leader_component_score",
                "core_component_score",
                "late_component_score",
                "non_junk_composite_score",
                "late_quality_raw_score",
                "late_quality_concept_boost",
                "late_quality_sector_strength",
                "late_quality_lag_balance",
                "late_quality_trend_support",
                "stability_volatility",
                "liquidity_turnover_share",
                "liquidity_turnover_rank",
                "liquidity_sector_turnover_share",
                "liquidity_sector_top_turnover_share",
                "liquidity_sector_mean_turnover_share",
                "liquidity_sector_turnover_share_gap",
                "liquidity_sector_symbol_count",
                "context_theme_density",
                "context_turnover_concentration",
                "context_theme_turnover_interaction",
                "context_sector_heat",
                "context_sector_breadth",
                "late_quality_sector_contribution",
                "late_quality_stability_contribution",
                "late_quality_liquidity_contribution",
                "late_quality_lag_contribution",
                "late_quality_trend_contribution",
            ],
            rows,
        )

    def _write_mainline_windows(self, windows: list[MainlineWindow]) -> Path:
        rows = [
            {
                "window_id": window.window_id,
                "symbol": window.symbol,
                "start_date": window.start_date.isoformat(),
                "end_date": window.end_date.isoformat(),
                "capturable_return": window.capturable_return,
            }
            for window in windows
        ]
        return _write_csv(
            self.config.mainline_windows_output_csv,
            ["window_id", "symbol", "start_date", "end_date", "capturable_return"],
            rows,
        )
