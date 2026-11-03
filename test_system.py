"""
Verification Test Suite for PackWise AI Recommender System.
Tests data, kinetics calculations, recommendation engine, charts, and PDF generator.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from data.commodities import COMMODITIES_DB, get_categories, get_all_commodity_names
from data.packaging_materials import PACKAGING_MATERIALS_DB
from data.intelligent_tech import ACTIVE_INTELLIGENT_TECH_DB, get_active_intelligent_recommendations
from models.respiration_kinetics import calculate_required_emap_permeability, simulate_gas_dynamics_over_time
from models.recommendation_engine import recommend_packaging
from utils.charts import (
    create_radar_comparison_chart,
    create_shelf_life_chart,
    create_gas_dynamics_chart,
    create_cost_sustainability_scatter
)
from utils.pdf_generator import generate_dossier_pdf


def run_tests():
    print("=== STARTING PACKWISE AI SYSTEM TESTS ===", flush=True)
    
    # 1. Test Data Integrity
    commodity_names = get_all_commodity_names()
    print(f"✅ Loaded {len(commodity_names)} Food Commodities across {len(get_categories())} categories.", flush=True)
    assert len(commodity_names) >= 15, "Commodity database count too low!"
    
    mat_count = len(PACKAGING_MATERIALS_DB)
    print(f"✅ Loaded {mat_count} Packaging Materials & Biopolymers.", flush=True)
    assert mat_count >= 12, "Packaging materials count too low!"
    
    tech_count = len(ACTIVE_INTELLIGENT_TECH_DB)
    print(f"✅ Loaded {tech_count} Active & Intelligent Packaging Technologies.", flush=True)
    assert tech_count >= 8, "Intelligent tech count too low!"
    
    # 2. Test Respiration & EMAP Model
    mango_data = COMMODITIES_DB["Alphonso Mango"]
    mango_data["name"] = "Alphonso Mango"
    emap_result = calculate_required_emap_permeability(mango_data, weight_kg=1.0, package_surface_area_m2=0.08, temp_c=12.0)
    assert emap_result is not None
    assert emap_result["required_otr"] > 100
    print(f"✅ Respiration Model: Alphonso Mango at 12°C requires OTR={emap_result['required_otr']} cm3/m2*d*atm, CO2TR={emap_result['required_co2tr']}", flush=True)
    
    # 3. Test Gas Dynamics Simulation
    mat_ldpe = PACKAGING_MATERIALS_DB["LDPE (Low-Density Polyethylene)"]
    sim = simulate_gas_dynamics_over_time(mango_data, mat_ldpe, weight_kg=1.0, surface_area_m2=0.08, headspace_volume_l=0.5, temp_c=12.0, hours=48)
    assert sim is not None
    assert len(sim["o2_curve"]) == 100
    print(f"✅ Gas Simulation: 48h dynamic O2 curve ended at {sim['final_o2']}%, CO2 at {sim['final_co2']}% ({sim['status']})", flush=True)
    
    # 4. Test Multi-Criteria Recommendation Engine on Multiple Food Types
    test_commodities = ["Alphonso Mango", "Fresh Paneer (Cottage Cheese)", "Potato Chips (Fried)", "Button Mushrooms", "Strawberries"]
    for c_name in test_commodities:
        c_data = COMMODITIES_DB[c_name].copy()
        c_data["name"] = c_name
        res = recommend_packaging(c_data, storage_temp_c=c_data.get("opt_temp_min", 4.0))
        top_mat = res["top_material"]
        sl = res["shelf_life_analysis"]
        print(f"✅ Recommender: '{c_name}' -> Top: {top_mat['name']} (Score: {top_mat['composite_score']}/100) | Shelf-Life: {sl['unpacked_baseline_days']}d -> {sl['ai_intelligent_pack_days']}d (+{sl['extension_percentage']}%)", flush=True)
        assert top_mat["composite_score"] > 50
        
    # 5. Test Chart Generation
    res_mango = recommend_packaging(mango_data, storage_temp_c=12.0)
    fig_radar = create_radar_comparison_chart(res_mango["ranked_materials"])
    assert fig_radar is not None
    fig_shelf = create_shelf_life_chart(res_mango["shelf_life_analysis"], "Alphonso Mango")
    assert fig_shelf is not None
    fig_gas = create_gas_dynamics_chart(sim, mango_data)
    assert fig_gas is not None
    fig_scatter = create_cost_sustainability_scatter(res_mango["ranked_materials"], res_mango["top_material"]["name"])
    assert fig_scatter is not None
    print("✅ Plotly Visualizations: Radar, Shelf-Life, Gas Dynamics, and Cost/Eco Scatter generated successfully.", flush=True)
    
    # 6. Test PDF Dossier Generation
    pdf_bytes = generate_dossier_pdf(res_mango, mango_data, storage_temp_c=12.0, ambient_rh=85)
    assert len(pdf_bytes) > 2000, "PDF generation failed or output is empty!"
    print(f"✅ PDF Technical Dossier: Generated official PDF ({len(pdf_bytes)} bytes) successfully.", flush=True)
    
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The system is fully operational.", flush=True)


if __name__ == "__main__":
    run_tests()
