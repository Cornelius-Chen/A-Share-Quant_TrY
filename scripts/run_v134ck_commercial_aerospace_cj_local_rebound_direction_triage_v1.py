from pathlib import Path

from a_share_quant.strategy.v134cj_commercial_aerospace_local_rebound_residue_registry_v1 import (
    V134CJCommercialAerospaceLocalReboundResidueRegistryV1Analyzer,
    write_report as write_registry_report,
)
from a_share_quant.strategy.v134ck_commercial_aerospace_cj_local_rebound_direction_triage_v1 import (
    V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    registry = V134CJCommercialAerospaceLocalReboundResidueRegistryV1Analyzer(repo_root).analyze()
    write_registry_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cj_commercial_aerospace_local_rebound_residue_registry_v1",
        result=registry,
    )
    result = V134CKCommercialAerospaceCJLocalReboundDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ck_commercial_aerospace_cj_local_rebound_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
