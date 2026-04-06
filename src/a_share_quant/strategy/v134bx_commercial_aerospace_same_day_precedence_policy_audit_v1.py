from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Report:
    summary: dict[str, Any]
    policy_rows: list[dict[str, Any]]
    collision_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "policy_rows": self.policy_rows,
            "collision_rows": self.collision_rows,
            "interpretation": self.interpretation,
        }


class V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.primary_orders_path = (
            repo_root / "data" / "training" / "commercial_aerospace_tail_weakdrift_full_orders_v1.csv"
        )
        self.holdings_audit_path = (
            repo_root / "reports" / "analysis" / "v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_same_day_precedence_policy_audit_v1.csv"
        )

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Report:
        primary_orders = self._load_csv(self.primary_orders_path)
        holdings_audit = json.loads(self.holdings_audit_path.read_text(encoding="utf-8"))
        orders_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in primary_orders:
            orders_by_key[(row["execution_trade_date"], row["symbol"])].append(row)

        collisions = [
            row
            for row in holdings_audit["session_rows"]
            if int(row["same_day_primary_action_count"]) > 0
        ]

        collision_rows: list[dict[str, Any]] = []
        family_counter: Counter[str] = Counter()
        for row in collisions:
            actions = sorted({order["action"] for order in orders_by_key[(row["trade_date"], row["symbol"])]})
            family = "|".join(actions)
            family_counter[family] += 1
            collision_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "predicted_tier": row["predicted_tier"],
                    "holding_status": row["holding_status"],
                    "collision_family": family,
                    "policy_implication": (
                        "same_day_new_lots_protected"
                        if any(action in {"open", "add"} for action in actions)
                        else "intraday_sells_must_preconsume_before_eod_reduce_close_reconciliation"
                    ),
                }
            )

        policy_rows = [
            {
                "policy_name": "open_add_protection",
                "status": "mandatory",
                "rule": "same-day open/add lots enter the new-lots bucket and are not sellable by the intraday sell lane on that day",
            },
            {
                "policy_name": "intraday_first_consumption_on_carried_inventory",
                "status": "mandatory",
                "rule": "intraday sell triggers consume only carried start-of-day inventory in trigger-time order",
            },
            {
                "policy_name": "eod_reduce_close_reconciliation",
                "status": "mandatory",
                "rule": "same-day EOD reduce/close actions must reconcile against residual carried inventory after intraday sells, not against original morning inventory",
            },
            {
                "policy_name": "mixed_collision_explicit_noop_or_clip",
                "status": "mandatory",
                "rule": "if same-day primary actions exceed residual eligible quantity, the shadow lane must emit clipped or noop reconciliation rows instead of negative inventory",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(collision_rows[0].keys()))
            writer.writeheader()
            writer.writerows(collision_rows)

        summary = {
            "acceptance_posture": "freeze_v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1",
            "collision_session_count": len(collision_rows),
            "collision_family_count": len(family_counter),
            "open_or_add_collision_count": sum(count for family, count in family_counter.items() if "open" in family or "add" in family),
            "reduce_or_close_collision_count": sum(count for family, count in family_counter.items() if "reduce" in family or "close" in family),
            "largest_collision_family": family_counter.most_common(1)[0][0] if family_counter else "",
            "collision_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_same_day_precedence_policy_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BX turns same-day primary collisions into explicit policy families instead of leaving them as an implementation afterthought.",
            "The binding lane must protect same-day new lots and reconcile later EOD reduce/close actions against residual carried inventory only.",
        ]
        return V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Report(
            summary=summary,
            policy_rows=policy_rows,
            collision_rows=collision_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
