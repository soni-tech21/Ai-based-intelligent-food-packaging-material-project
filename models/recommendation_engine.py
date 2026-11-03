"""
Multi-Criteria AI Recommendation Engine for Food Packaging Materials.
Balances physiological barrier matching, eco-sustainability, economics, and mechanical strength.
"""

from data.packaging_materials import PACKAGING_MATERIALS_DB
from data.intelligent_tech import get_active_intelligent_recommendations
from models.respiration_kinetics import calculate_required_emap_permeability


STRATEGY_WEIGHTS = {
    "Balanced (Recommended)": {
        "barrier": 0.35,
        "sustainability": 0.30,
        "cost": 0.20,
        "mechanical": 0.15
    },
    "Maximum Shelf Life": {
        "barrier": 0.55,
        "sustainability": 0.15,
        "cost": 0.10,
        "mechanical": 0.20
    },
    "Green & Eco-Priority (MoFPI Mission)": {
        "barrier": 0.25,
        "sustainability": 0.55,
        "cost": 0.10,
        "mechanical": 0.10
    },
    "Economical / Smallholder FPO Priority": {
        "barrier": 0.30,
        "sustainability": 0.15,
        "cost": 0.45,
        "mechanical": 0.10
    }
}


def score_barrier_match(commodity_data, material, temp_c, weight_kg=1.0, area_m2=0.08):
    """
    Computes a 0-100 barrier suitability score based on commodity biochemical traits.
    """
    is_respiring = commodity_data.get("is_respiring", False)
    fat_pct = commodity_data.get("fat_pct", 0.0)
    moisture_pct = commodity_data.get("moisture_pct", 50.0)
    water_activity = commodity_data.get("water_activity", 0.7)
    
    m_otr = material["otr"]
    m_wvtr = material["wvtr"]
    
    if is_respiring:
        # Produce needs breathable gas transmission. Absolute barriers will cause anaerobic decay.
        emap_specs = calculate_required_emap_permeability(commodity_data, weight_kg, area_m2, temp_c)
        req_otr = emap_specs["required_otr"] if emap_specs else 2000.0
        
        # Penalize ultra-low barrier films for respiring produce
        if m_otr < 20.0:
            return 10.0  # Suffocation hazard
            
        # Logarithmic ratio error matching
        log_diff = abs(np_log10(max(1.0, m_otr)) - np_log10(max(1.0, req_otr)))
        barrier_score = max(20.0, 100.0 - (log_diff * 40.0))
        
        # Micro-perforated bonus for high-breathing produce
        if commodity_data.get("respiration_rate_20c", 0) > 80 and "Micro-Perforated" in material.get("description", ""):
            barrier_score = min(100.0, barrier_score + 15.0)
            
        return round(barrier_score, 1)
        
    else:
        # Non-respiring foods: High fat, high moisture or high aw requires high barrier
        score = 80.0
        
        # High fat requires low OTR to avoid rancidity
        if fat_pct > 20.0:
            if m_otr <= 2.0:
                score += 20.0
            elif m_otr <= 25.0:
                score += 10.0
            elif m_otr > 500.0:
                score -= 40.0
                
        # Dry crisp foods (chips, milk powder) require ultra-low WVTR
        if water_activity < 0.40 or moisture_pct < 5.0:
            if m_wvtr <= 1.5:
                score += 15.0
            elif m_wvtr > 10.0:
                score -= 45.0
                
        # High aw dairy/meat requires tight seal and good OTR
        if water_activity > 0.90:
            if m_otr <= 50.0:
                score += 10.0
            elif m_otr > 1000.0:
                score -= 35.0
                
        # UV light protection bonus for spices/fried chips
        if fat_pct > 15.0 or "Spices" in commodity_data.get("category", ""):
            if material.get("light_barrier_pct", 0) >= 90:
                score += 10.0
                
        return max(15.0, min(100.0, score))


def np_log10(x):
    import math
    return math.log10(max(1e-4, x))


def recommend_packaging(commodity_data, storage_temp_c, strategy_name="Balanced (Recommended)", weight_kg=0.5, surface_area_m2=0.06):
    """
    Main recommendation algorithm. Evaluates all materials and returns ranked recommendations.
    """
    weights = STRATEGY_WEIGHTS.get(strategy_name, STRATEGY_WEIGHTS["Balanced (Recommended)"])
    scored_materials = []
    
    # Pre-calculate cost normalization (cheapest gets 100, highest gets 40)
    all_costs = [m["cost_index_inr_per_kg"] for m in PACKAGING_MATERIALS_DB.values()]
    min_cost, max_cost = min(all_costs), max(all_costs)
    
    for name, mat in PACKAGING_MATERIALS_DB.items():
        # 1. Barrier score
        s_barrier = score_barrier_match(commodity_data, mat, storage_temp_c, weight_kg, surface_area_m2)
        
        # 2. Eco & Sustainability score
        s_eco = mat["sustainability_score"]
        
        # 3. Cost score (inversely proportional to INR/kg)
        s_cost = 100.0 - (((mat["cost_index_inr_per_kg"] - min_cost) / (max_cost - min_cost)) * 60.0)
        
        # 4. Mechanical score
        tensile = mat["tensile_strength_mpa"]
        s_mech = min(100.0, 30.0 + (tensile / 220.0) * 70.0)
        
        # Composite Weighted Multi-Criteria Score
        composite_score = (
            weights["barrier"] * s_barrier +
            weights["sustainability"] * s_eco +
            weights["cost"] * s_cost +
            weights["mechanical"] * s_mech
        )
        
        scored_materials.append({
            "name": name,
            "category": mat["category"],
            "composite_score": round(composite_score, 1),
            "barrier_score": round(s_barrier, 1),
            "sustainability_score": round(s_eco, 1),
            "cost_score": round(s_cost, 1),
            "mechanical_score": round(s_mech, 1),
            "thickness_um": mat["typical_thickness_um"],
            "otr": mat["otr"],
            "wvtr": mat["wvtr"],
            "co2tr": mat["co2tr"],
            "cost_inr_per_kg": mat["cost_index_inr_per_kg"],
            "is_biodegradable": mat["is_biodegradable"],
            "is_compostable": mat["is_compostable"],
            "is_recyclable": mat["is_recyclable"],
            "carbon_footprint": mat["carbon_footprint_kg_co2_per_kg"],
            "fssai_compliant": mat["fssai_compliant"],
            "suitable_for_map": mat["suitable_for_map"],
            "description": mat["description"]
        })
        
    # Rank descending by composite score
    ranked_materials = sorted(scored_materials, key=lambda x: x["composite_score"], reverse=True)
    top_material = ranked_materials[0]
    
    # Active & Intelligent packaging integrations
    active_tech = get_active_intelligent_recommendations(commodity_data, storage_temp_c)
    
    # Calculate shelf life predictions
    base_days = commodity_data.get("unpacked_shelf_life_days", 4)
    
    # Barrier improvement factor
    barrier_boost = 1.0 + (top_material["barrier_score"] / 100.0) * 2.5
    
    # Active tech improvement factor
    active_boost_pct = sum([tech.get("shelf_life_extension_pct", 0) for tech in active_tech if tech["type"] == "Active Packaging"])
    total_active_factor = 1.0 + (min(150.0, active_boost_pct) / 100.0)
    
    conventional_days = max(base_days + 1, round(base_days * 1.8))
    ai_smart_days = max(conventional_days + 2, round(base_days * barrier_boost * total_active_factor))
    
    # Packaging Hierarchy Specification
    secondary_packaging = generate_secondary_packaging(commodity_data, top_material)
    tertiary_packaging = generate_tertiary_packaging(commodity_data)
    
    return {
        "commodity_name": commodity_data.get("name", "Commodity"),
        "top_material": top_material,
        "ranked_materials": ranked_materials,
        "active_intelligent_tech": active_tech,
        "shelf_life_analysis": {
            "unpacked_baseline_days": base_days,
            "conventional_pack_days": conventional_days,
            "ai_intelligent_pack_days": ai_smart_days,
            "extension_percentage": round(((ai_smart_days - base_days) / max(1, base_days)) * 100.0, 1),
            "estimated_spoilage_reduction_pct": min(85.0, round(60.0 + (top_material["composite_score"] * 0.25), 1))
        },
        "secondary_packaging": secondary_packaging,
        "tertiary_packaging": tertiary_packaging
    }


def generate_secondary_packaging(commodity_data, primary_material):
    """
    Generates tailored secondary packaging and MAP gas mix recommendations.
    """
    cat = commodity_data.get("category", "")
    is_respiring = commodity_data.get("is_respiring", False)
    
    if is_respiring:
        return {
            "type": "Ventilated Micro-Flute Corrugated Tray / Punnet with Lid",
            "gas_flush_mix": f"{commodity_data.get('target_o2_min', 3)}% - {commodity_data.get('target_o2_max', 5)}% O2, {commodity_data.get('target_co2_min', 5)}% - {commodity_data.get('target_co2_max', 10)}% CO2, Balance N2",
            "cushioning": "Recycled molded paper pulp divider or honeycomb cushioning",
            "humidity_control": "Dual-sided anti-fog coating on lid film to prevent condensation droplets"
        }
    elif cat in ["Meat, Poultry & Seafood"]:
        return {
            "type": "Rigid Barrier Thermoformed Tray (rPET/EVOH) with Heat-Sealed Top Web",
            "gas_flush_mix": "30% CO2 + 70% N2 (or 70% O2 + 30% CO2 for high-ox red meat blooming)",
            "cushioning": "Superabsorbent Cellulose exudate drip pad",
            "humidity_control": "Hermetic MAP vacuum-skin seal"
        }
    elif cat in ["Snacks & Fried Foods"]:
        return {
            "type": "Nitrogen Gas Flushed Pillow Pouch / Doypack with Resealable Zipper",
            "gas_flush_mix": "99.5% High-Purity Food-Grade N2 (< 0.5% Residual Headspace O2)",
            "cushioning": "Gas pillow serves as pneumatic shock cushion protecting fragile chips",
            "humidity_control": "Desiccant integration in secondary carton if export shipment"
        }
    elif cat in ["Dairy & Fermented Foods"]:
        return {
            "type": "Vacuum-Formed Rigid / Flexible Barrier Skin Pack",
            "gas_flush_mix": "Vacuum sealed or 20-30% CO2 + 70-80% N2 headspace",
            "cushioning": "Interleaved food-grade parchment liners between sliced portions",
            "humidity_control": "Active moisture barrier"
        }
    else:
        return {
            "type": "Multi-wall Kraft Paper Outer Bag / Corrugated folding carton",
            "gas_flush_mix": "Ambient or Nitrogen purged",
            "cushioning": "Inner food-grade liners",
            "humidity_control": "Dry ambient storage"
        }


def generate_tertiary_packaging(commodity_data):
    """
    Generates palletizing, transport, and MoFPI cold-chain logistics specs.
    """
    temp_min = commodity_data.get("opt_temp_min", 4.0)
    temp_max = commodity_data.get("opt_temp_max", 10.0)
    rh_min = commodity_data.get("opt_rh_min", 85)
    rh_max = commodity_data.get("opt_rh_max", 90)
    
    return {
        "master_carton": "5-Ply Heavy-Duty Corrugated Fibreboard (CFB) Box (Bursting Strength > 14 kg/cm²)",
        "ventilation": "5-8% side wall circular vent holes aligned for cold-chain forced-air cooling" if commodity_data.get("is_respiring") else "Fully sealed glued flap carton",
        "palletization": "Standard Euro/ISO Wooden Pallet (1200 x 1000 mm), stretch-wrapped with corner edge-protectors",
        "cold_chain_setpoint": f"{temp_min}°C to {temp_max}°C (Continuous automated GPS/TTI data logging)",
        "relative_humidity_setpoint": f"{rh_min}% to {rh_max}% RH",
        "mofpi_scheme_alignment": "Eligible for MoFPI Pradhan Mantri Kisan SAMPADA Yojana (PMKSY) Integrated Cold Chain & Value Addition Infrastructure Subsidy (up to 50% capital grant)"
    }
