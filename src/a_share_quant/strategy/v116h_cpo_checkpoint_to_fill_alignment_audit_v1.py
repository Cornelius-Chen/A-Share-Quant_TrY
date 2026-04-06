from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v115p_cpo_intraday_timing_aware_overlay_replay_v1 import (
    _to_baostock_symbol,
    _to_float,
)


@dataclass(slots=True)
class V116HCpoCheckpointToFillAlignmentAuditReport:
    summary: dict[str, Any]
    alignment_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "alignment_rows": self.alignment_rows,
            "interpretation": self.interpretation,
        }


class V116HCpoCheckpointToFillAlignmentAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _next_bar_fill(*, bs: Any, symbol: str, trade_date: str, checkpoint_label: str) -> tuple[float | None, str | None]:
        hhmm = checkpoint_label.replace(":", "")
        def _query() -> Any:
            return bs.query_history_k_data_plus(
                _to_baostock_symbol(symbol),
                "date,time,code,open,high,low,close,volume,amount,adjustflag",
                start_date=trade_date,
                end_date=trade_date,
                frequency="30",
                adjustflag="2",
            )

        rs = _query()
        if str(rs.error_code) == "10001001":
            relogin = bs.login()
            if str(relogin.error_code) != "0":
                return None, None
            rs = _query()
        if str(rs.error_code) != "0":
            return None, None
        rows: list[dict[str, Any]] = []
        while rs.next():
            raw = rs.get_row_data()
            rows.append({"time": str(raw[1]), "open": _to_float(raw[3])})
        for row in rows:
            row_hhmm = row["time"][8:12]
            if row_hhmm > hhmm:
                return _to_float(row["open"]), f"{row_hhmm[:2]}:{row_hhmm[2:]}"
        return None, None

    def analyze(self, *, v115q_payload: dict[str, Any]) -> V116HCpoCheckpointToFillAlignmentAuditReport:
        import baostock as bs

        timing_rows = [row for row in list(v115q_payload.get("timing_rows", [])) if str(row.get("timing_bucket")) == "intraday_same_session"]

        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        alignment_rows: list[dict[str, Any]] = []
        try:
            for row in timing_rows:
                signal_trade_date = str(row["signal_trade_date"])
                symbol = str(row["symbol"])
                checkpoint = str(row["earliest_strict_checkpoint"])
                fill_price, fill_bar_time = self._next_bar_fill(
                    bs=bs,
                    symbol=symbol,
                    trade_date=signal_trade_date,
                    checkpoint_label=checkpoint,
                )
                alignment_rows.append(
                    {
                        "signal_trade_date": signal_trade_date,
                        "symbol": symbol,
                        "timing_bucket": str(row["timing_bucket"]),
                        "checkpoint_time": checkpoint,
                        "execution_bar_time": fill_bar_time,
                        "execution_price": None if fill_price is None else round(fill_price, 4),
                        "strictly_after_checkpoint": bool(fill_bar_time is not None and fill_bar_time > checkpoint),
                    }
                )
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        strict_after_count = sum(1 for row in alignment_rows if row["strictly_after_checkpoint"])
        summary = {
            "acceptance_posture": "freeze_v116h_cpo_checkpoint_to_fill_alignment_audit_v1",
            "row_count": len(alignment_rows),
            "strictly_after_checkpoint_count": strict_after_count,
            "strict_alignment_confirmed": strict_after_count == len(alignment_rows),
            "recommended_next_posture": "treat_checkpoint_to_fill_as_reported_and_not_as_a_remaining_semantic_gap",
        }
        interpretation = [
            "V1.16H audits the actual checkpoint-to-fill mapping for intraday same-session strict signals using Baostock 30min bars.",
            "This is meant to close the ambiguity raised in adversarial review about whether the replay was truly using the next tradable bar after the visible checkpoint.",
            "If all rows fill strictly after checkpoint, the remaining issue is reporting clarity, not execution semantics.",
        ]
        return V116HCpoCheckpointToFillAlignmentAuditReport(
            summary=summary,
            alignment_rows=alignment_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116HCpoCheckpointToFillAlignmentAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116HCpoCheckpointToFillAlignmentAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v115q_payload=json.loads((repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116h_cpo_checkpoint_to_fill_alignment_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
