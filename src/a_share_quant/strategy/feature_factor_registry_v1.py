from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_BUCKETS = {
    "retained_feature",
    "explanatory_only_feature",
    "candidate_factor",
}


@dataclass(slots=True)
class FeatureFactorRegistryEntry:
    entry_name: str
    bucket: str
    source_type: str
    posture: str
    rationale: str
    evidence_paths: list[str]
    evidence_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "entry_name": self.entry_name,
            "bucket": self.bucket,
            "source_type": self.source_type,
            "posture": self.posture,
            "rationale": self.rationale,
            "evidence_paths": self.evidence_paths,
            "evidence_count": self.evidence_count,
        }


@dataclass(slots=True)
class FeatureFactorRegistryReport:
    summary: dict[str, Any]
    registry_rows: list[FeatureFactorRegistryEntry]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": [row.as_dict() for row in self.registry_rows],
            "interpretation": self.interpretation,
        }


class FeatureFactorRegistryAnalyzer:
    """Build the first explicit V1.2 feature/factor registry from current evidence."""

    def analyze(
        self,
        *,
        root_dir: Path,
        entries: list[dict[str, Any]],
    ) -> FeatureFactorRegistryReport:
        registry_rows: list[FeatureFactorRegistryEntry] = []
        bucket_counts = {bucket: 0 for bucket in sorted(ALLOWED_BUCKETS)}

        for item in entries:
            entry_name = str(item["entry_name"])
            bucket = str(item["bucket"])
            if bucket not in ALLOWED_BUCKETS:
                raise ValueError(f"Unsupported registry bucket: {bucket}")
            source_type = str(item["source_type"])
            posture = str(item["posture"])
            rationale = str(item["rationale"])
            evidence_paths = [str(path) for path in item.get("evidence_paths", [])]
            if not evidence_paths:
                raise ValueError(f"{entry_name} must include at least one evidence path.")
            for relative_path in evidence_paths:
                path = root_dir / relative_path
                if not path.exists():
                    raise FileNotFoundError(f"Missing evidence path for {entry_name}: {path}")

            registry_rows.append(
                FeatureFactorRegistryEntry(
                    entry_name=entry_name,
                    bucket=bucket,
                    source_type=source_type,
                    posture=posture,
                    rationale=rationale,
                    evidence_paths=evidence_paths,
                    evidence_count=len(evidence_paths),
                )
            )
            bucket_counts[bucket] += 1

        summary = {
            "registry_entry_count": len(registry_rows),
            "retained_feature_count": bucket_counts["retained_feature"],
            "explanatory_only_feature_count": bucket_counts["explanatory_only_feature"],
            "candidate_factor_count": bucket_counts["candidate_factor"],
            "ready_for_factor_evaluation_protocol": bucket_counts["retained_feature"] > 0
            and bucket_counts["candidate_factor"] > 0,
        }
        interpretation = [
            "Retained features are the current reusable feature pool: they already have enough structural evidence to survive beyond one local pocket.",
            "Explanatory-only features stay in the research stack, but they should not be promoted into retained strategy rules or factor inputs yet.",
            "Candidate factors are worth formal evaluation next; they are promising enough to preserve, but not stable enough to call retained features.",
        ]
        return FeatureFactorRegistryReport(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_feature_factor_registry_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeatureFactorRegistryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
