from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130XTransferProgramChangeDetectionProtocolReport:
    summary: dict[str, Any]
    artifact_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "artifact_rows": self.artifact_rows,
            "interpretation": self.interpretation,
        }


class V130XTransferProgramChangeDetectionProtocolAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv_path = repo_root / "data" / "training" / "transfer_program_change_detection_protocol_v1.csv"
        self.artifacts = [
            {
                "artifact_role": "v6_stock_snapshot",
                "path": repo_root / "data" / "derived" / "stock_snapshots" / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv",
                "rerun_chain": "v130g_to_v130w",
            },
            {
                "artifact_role": "v5_stock_snapshot",
                "path": repo_root / "data" / "derived" / "stock_snapshots" / "market_research_stock_snapshots_v5_carry_row_diversity_refresh.csv",
                "rerun_chain": "v129y_to_v130w",
            },
            {
                "artifact_role": "v6_sector_snapshot",
                "path": repo_root / "data" / "derived" / "sector_snapshots" / "market_research_sector_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv",
                "rerun_chain": "v130g_to_v130w",
            },
            {
                "artifact_role": "bk0808_watch_timeline_600118",
                "path": repo_root / "reports" / "analysis" / "market_v6_q3_symbol_timeline_600118_capture_c_v1.json",
                "rerun_chain": "v130n_to_v130w",
            },
            {
                "artifact_role": "bk0808_bridge_timeline_600760",
                "path": repo_root / "reports" / "analysis" / "market_v5_q2_symbol_timeline_600760_capture_b_v1.json",
                "rerun_chain": "v130n_to_v130w",
            },
        ]

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def analyze(self) -> V130XTransferProgramChangeDetectionProtocolReport:
        artifact_rows: list[dict[str, Any]] = []
        for artifact in self.artifacts:
            path = artifact["path"]
            stat = path.stat()
            artifact_rows.append(
                {
                    "artifact_role": artifact["artifact_role"],
                    "path": str(path),
                    "exists": path.exists(),
                    "size_bytes": stat.st_size,
                    "modified_epoch": round(stat.st_mtime, 6),
                    "sha256": self._hash_file(path),
                    "rerun_chain": artifact["rerun_chain"],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v130x_transfer_program_change_detection_protocol_v1",
            "artifact_count": len(artifact_rows),
            "authoritative_status": "transfer_program_frozen_until_monitored_artifacts_change",
            "authoritative_rule": "do_not_restart_board_transfer_analysis_under_static_artifacts; rerun_only_after_a_monitored_source_file_changes",
        }
        interpretation = [
            "V1.30X turns the transfer freeze into a concrete change-detection protocol.",
            "The point is to stop discretionary re-analysis under unchanged data and to make the rerun boundary explicit and mechanical.",
        ]
        return V130XTransferProgramChangeDetectionProtocolReport(
            summary=summary,
            artifact_rows=artifact_rows,
            interpretation=interpretation,
        )

    def write_protocol_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130XTransferProgramChangeDetectionProtocolReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130XTransferProgramChangeDetectionProtocolAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130x_transfer_program_change_detection_protocol_v1",
        result=result,
    )
    analyzer.write_protocol_csv(result.artifact_rows)


if __name__ == "__main__":
    main()
