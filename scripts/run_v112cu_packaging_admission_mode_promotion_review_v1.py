from __future__ import annotations

from pathlib import Path

import yaml

from a_share_quant.strategy.v112cu_packaging_admission_mode_promotion_review_v1 import (
    V112CUPackagingAdmissionModePromotionReviewAnalyzer,
    load_json_report,
    write_v112cu_packaging_admission_mode_promotion_review_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "config" / "v112cu_packaging_admission_mode_promotion_review_v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    analyzer = V112CUPackagingAdmissionModePromotionReviewAnalyzer()
    result = analyzer.analyze(
        ch_payload=load_json_report(repo_root / config["ch_report_path"]),
        cs_payload=load_json_report(repo_root / config["cs_report_path"]),
        ct_payload=load_json_report(repo_root / config["ct_report_path"]),
    )
    output_path = write_v112cu_packaging_admission_mode_promotion_review_report(
        reports_dir=repo_root / config["reports_dir"],
        report_name=config["report_name"],
        result=result,
    )
    print(f"V1.12CU packaging admission mode promotion review report: {output_path.relative_to(repo_root)}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
