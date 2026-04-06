from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V130ZTransferProgramReopenReadinessStatusReport:
    summary: dict[str, Any]
    artifact_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "artifact_rows": self.artifact_rows,
            "interpretation": self.interpretation,
        }


class V130ZTransferProgramReopenReadinessStatusAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.protocol_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v130x_transfer_program_change_detection_protocol_v1.json"
        )

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def analyze(self) -> V130ZTransferProgramReopenReadinessStatusReport:
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))
        artifact_rows: list[dict[str, Any]] = []
        changed_count = 0
        missing_count = 0

        for row in protocol["artifact_rows"]:
            path = Path(row["path"])
            exists = path.exists()
            current_sha256 = self._hash_file(path) if exists else None
            changed = current_sha256 != row["sha256"]
            if changed:
                changed_count += 1
            if not exists:
                missing_count += 1
            artifact_rows.append(
                {
                    "artifact_role": row["artifact_role"],
                    "path": row["path"],
                    "exists": exists,
                    "baseline_sha256": row["sha256"],
                    "current_sha256": current_sha256,
                    "changed_since_protocol_freeze": changed,
                    "rerun_chain": row["rerun_chain"],
                }
            )

        rerun_required = changed_count > 0 or missing_count > 0
        summary = {
            "acceptance_posture": "freeze_v130z_transfer_program_reopen_readiness_status_v1",
            "artifact_count": len(artifact_rows),
            "changed_artifact_count": changed_count,
            "missing_artifact_count": missing_count,
            "rerun_required": rerun_required,
            "authoritative_status": (
                "rerun_transfer_program_gate_open"
                if rerun_required
                else "no_rerun_required_under_current_static_artifacts"
            ),
            "authoritative_rule": (
                "rerun_the_transfer_program_only_if_a_monitored_artifact_hash_changes_or_a_required_artifact_disappears"
            ),
        }
        interpretation = [
            "V1.30Z is the live status check on top of the static-data gate.",
            "When every monitored artifact still matches the frozen protocol, the correct posture is to do nothing rather than manufacture more board-transfer analysis.",
        ]
        return V130ZTransferProgramReopenReadinessStatusReport(
            summary=summary,
            artifact_rows=artifact_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V130ZTransferProgramReopenReadinessStatusReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V130ZTransferProgramReopenReadinessStatusAnalyzer(repo_root).analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130z_transfer_program_reopen_readiness_status_v1",
        result=result,
    )


if __name__ == "__main__":
    main()
