from __future__ import annotations


def normalize_beneficiary_role(*, beneficiary_role: str, mapping_confidence: str) -> tuple[str, str]:
    role = (beneficiary_role or "").strip()
    confidence = (mapping_confidence or "").strip().lower()

    if not role:
        if confidence == "low":
            return "weak_association", "weak_association"
        return "unmapped", "unmapped"

    if role.startswith("direct_"):
        return "direct_theme_proxy", "direct_beneficiary"

    if role in {
        "core_supply_chain_proxy",
        "adjacent_supply_chain",
        "adjacent_equipment_proxy",
        "adjacent_infrastructure",
        "adjacent_innovative_drug_proxy",
        "adjacent_rare_earth_proxy",
        "adjacent_shipbuilding_proxy",
        "adjacent_battery_metal_proxy",
        "adjacent_battery_proxy",
        "adjacent_new_energy_proxy",
        "adjacent_defense_proxy",
        "adjacent_consumer_proxy",
        "adjacent_medical_digitization_proxy",
    }:
        if confidence == "low":
            return "adjacent_proxy", "weak_association"
        return "adjacent_proxy", "proxy_beneficiary"

    if role in {
        "adjacent_material_proxy",
    }:
        if confidence == "low":
            return "material_proxy", "weak_association"
        return "material_proxy", "proxy_beneficiary"

    if confidence == "low":
        return "other_proxy", "weak_association"
    return "other_proxy", "proxy_beneficiary"
