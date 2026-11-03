"""
PackWise AI - Intelligent Food Packaging Material Recommendation System
Ministry of Food Processing Industries (MoFPI) | Smart India Hackathon (SIH26236)
Theme: Agriculture, FoodTech & Rural Development
"""

import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="PackWise AI | MoFPI Food Packaging Recommender",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

from data.commodities import COMMODITIES_DB, get_categories, get_commodities_by_category
from data.packaging_materials import PACKAGING_MATERIALS_DB
from data.intelligent_tech import ACTIVE_INTELLIGENT_TECH_DB
from models.recommendation_engine import recommend_packaging, STRATEGY_WEIGHTS
from models.respiration_kinetics import calculate_required_emap_permeability, simulate_gas_dynamics_over_time
from utils.charts import (
    create_radar_comparison_chart,
    create_shelf_life_chart,
    create_gas_dynamics_chart,
    create_cost_sustainability_scatter
)
from utils.pdf_generator import generate_dossier_pdf


# Custom CSS for polished government & tech aesthetic
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 50%, #047857 100%);
        padding: 20px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .gov-badge {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .rec-card {
        background-color: #F0FDF4;
        border: 2px solid #10B981;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .metric-chip {
        background: #F3F4F6;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
        border: 1px solid #E5E7EB;
    }
    .tech-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .pill-active { background-color: #DBEAFE; color: #1E40AF; }
    .pill-intel { background-color: #FEF3C7; color: #92400E; }
    .pill-eco { background-color: #D1FAE5; color: #065F46; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px 6px 0px 0px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# --- HEADER BANNER ---
st.markdown("""
<div class="main-header">
    <div class="gov-badge">🇮🇳 MINISTRY OF FOOD PROCESSING INDUSTRIES (MoFPI) • GOVT. OF INDIA</div>
    <h1 style="margin: 0; font-size: 2.1rem; color: #FFFFFF;">PackWise AI : Intelligent Food Packaging Recommender</h1>
    <p style="margin: 6px 0 0 0; opacity: 0.92; font-size: 1.02rem;">
        Decision-support system matching commodity bio-physiology with active, intelligent & sustainable packaging films (SIH26236)
    </p>
</div>
""", unsafe_allow_html=True)


# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=600&q=80", use_container_width=True)
    st.markdown("### ⚙️ System Configuration")
    
    app_mode = st.radio(
        "Select User Persona / Mode:",
        ["👨‍🌾 Farmer / FPO Fast-Track Mode", "🔬 Food Technologist / R&D Mode"],
        help="Fast-Track mode uses pre-validated commodity defaults. R&D mode allows micro-tuning of physiological parameters."
    )
    
    st.divider()
    st.markdown("#### 🥦 Select Food Commodity")
    
    categories = get_categories()
    selected_category = st.selectbox("Commodity Category", categories, index=0)
    
    commodities_in_cat = get_commodities_by_category(selected_category)
    selected_commodity_name = st.selectbox("Commodity", commodities_in_cat, index=0)
    
    commodity_data = COMMODITIES_DB[selected_commodity_name].copy()
    commodity_data["name"] = selected_commodity_name
    
    st.caption(f"**Hindi Name:** {commodity_data.get('hindi_name', 'N/A')}")
    st.caption(f"*{commodity_data.get('description', '')}*")
    
    st.divider()
    st.markdown("#### 🎯 Optimization Priority")
    strategy = st.selectbox(
        "Decision Strategy",
        list(STRATEGY_WEIGHTS.keys()),
        index=0,
        help="Adjusts relative weights for barrier protection, sustainability, cost, and mechanical durability."
    )
    
    st.divider()
    st.markdown("#### 🌡️ Environmental & Logistics Parameters")
    
    default_temp = float(commodity_data.get("opt_temp_min", 4.0))
    storage_temp = st.slider("Storage / Transit Temp (°C)", -5.0, 38.0, default_temp, 0.5)
    
    default_rh = int(commodity_data.get("opt_rh_min", 85))
    ambient_rh = st.slider("Ambient Relative Humidity (%)", 20, 98, default_rh, 5)
    
    package_weight_g = st.number_input("Unit Pack Net Weight (g)", min_value=25, max_value=25000, value=int(commodity_data.get("typical_package_weight_g", 500)), step=50)
    weight_kg = package_weight_g / 1000.0
    
    # Custom parameter overrides in R&D mode
    if "Food Technologist" in app_mode:
        with st.expander("🔬 Fine-Tune Biochemical Parameters", expanded=False):
            commodity_data["moisture_pct"] = st.slider("Moisture Content (%)", 1.0, 98.0, float(commodity_data["moisture_pct"]))
            commodity_data["fat_pct"] = st.slider("Fat / Lipid Content (%)", 0.0, 70.0, float(commodity_data["fat_pct"]))
            commodity_data["water_activity"] = st.slider("Water Activity (aw)", 0.15, 0.99, float(commodity_data["water_activity"]))
            commodity_data["ph"] = st.slider("pH Level", 2.0, 8.5, float(commodity_data["ph"]))
            
            if commodity_data.get("is_respiring", False):
                commodity_data["respiration_rate_20c"] = st.number_input("Respiration Rate at 20°C (mg CO2/kg*hr)", 5.0, 300.0, float(commodity_data["respiration_rate_20c"]))
                commodity_data["q10_factor"] = st.slider("Q10 Sensitivity Factor", 1.5, 3.2, float(commodity_data["q10_factor"]), 0.1)

    # Estimate standard surface area for pouch/tray
    surface_area_m2 = max(0.02, 0.08 * (weight_kg ** 0.67))


# --- RUN RECOMMENDATION ENGINE ---
rec_result = recommend_packaging(
    commodity_data=commodity_data,
    storage_temp_c=storage_temp,
    strategy_name=strategy,
    weight_kg=weight_kg,
    surface_area_m2=surface_area_m2
)

top_mat = rec_result["top_material"]
sl = rec_result["shelf_life_analysis"]
active_tech = rec_result["active_intelligent_tech"]


# --- TOP SUMMARY METRIC ROW ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(
        label="🏆 Top Packaging Film",
        value=top_mat["name"].split("(")[0].strip(),
        delta=f"AI Score: {top_mat['composite_score']}/100"
    )
with col_m2:
    st.metric(
        label="📅 Safe Shelf-Life",
        value=f"{sl['ai_intelligent_pack_days']} Days",
        delta=f"+{sl['extension_percentage']}% vs Unpacked"
    )
with col_m3:
    st.metric(
        label="📉 Spoilage Loss Prevention",
        value=f"~{sl['estimated_spoilage_reduction_pct']}%",
        delta="Farm-to-Fork Reduction"
    )
with col_m4:
    eco_label = "100% Bio-Compostable" if top_mat["is_compostable"] else ("Recyclable Circular" if top_mat["is_recyclable"] else "Multi-layer High-Barrier")
    st.metric(
        label="🌱 Eco Sustainability",
        value=f"{top_mat['sustainability_score']}/100",
        delta=eco_label
    )

st.write("")


# --- TABS INTERFACE ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 AI Recommendation",
    "🔬 Respiration & EMAP Simulator",
    "💡 Active & Smart Systems",
    "🌱 Eco & Cost Analysis",
    "📑 MoFPI Technical Dossier",
    "🏛️ Government Schemes & Subsidies"
])


# =========================================================
# TAB 1: AI RECOMMENDATION
# =========================================================
with tab1:
    col_rec_left, col_rec_right = st.columns([1.1, 0.9])
    
    with col_rec_left:
        st.markdown(f"""
        <div class="rec-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.25rem; font-weight: 700; color: #065F46;">
                    Primary Recommended Film: {top_mat['name']}
                </span>
                <span style="background-color: #10B981; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.85rem;">
                    Match: {top_mat['composite_score']}%
                </span>
            </div>
            <p style="color: #374151; font-size: 0.92rem; margin-bottom: 12px;">
                {top_mat['description']}
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                <span class="tech-pill pill-eco">🌱 Eco-Score: {top_mat['sustainability_score']}/100</span>
                <span class="tech-pill pill-active">🛡️ Barrier Match: {top_mat['barrier_score']}/100</span>
                <span class="tech-pill pill-intel">💰 Cost: ₹{top_mat['cost_inr_per_kg']:.1f}/kg</span>
                <span class="tech-pill pill-active">💪 Strength: {top_mat['mechanical_score']}/100</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Physical & Barrier Specs Table
        st.markdown("#### 📐 Barrier & Engineering Specifications")
        spec_df = pd.DataFrame({
            "Engineering Metric": [
                "Film Thickness (Gauge)",
                "Oxygen Transmission Rate (OTR)",
                "Water Vapor Transmission Rate (WVTR)",
                "CO₂ Transmission Rate (CO₂TR)",
                "Gas Selectivity Ratio (β = CO₂TR/OTR)",
                "Plastic Waste EPR Status",
                "FSSAI Compliance"
            ],
            "Value": [
                f"{top_mat['thickness_um']} µm",
                f"{top_mat['otr']} cm³/m²·24h·atm",
                f"{top_mat['wvtr']} g/m²·24h",
                f"{top_mat['co2tr']} cm³/m²·24h·atm",
                f"{(top_mat['co2tr'] / max(1.0, top_mat['otr'])):.2f}",
                "IS/ISO 17088 Certified Compostable" if top_mat["is_compostable"] else "PWM EPR Recyclable",
                "✅ Certified Food Grade Contact"
            ]
        })
        st.dataframe(spec_df, hide_index=True, use_container_width=True)
        
        # Packaging Hierarchy Cards
        st.markdown("#### 📦 Packaging Hierarchy (Secondary & Master Logistics)")
        sec = rec_result["secondary_packaging"]
        tert = rec_result["tertiary_packaging"]
        
        c_sec, c_tert = st.columns(2)
        with c_sec:
            st.info(f"**Secondary Unit Pack:**\n\n• **Format:** {sec['type']}\n• **Gas Flush:** {sec['gas_flush_mix']}\n• **Cushioning:** {sec['cushioning']}")
        with c_tert:
            st.success(f"**Tertiary Master Shipper:**\n\n• **Carton:** {tert['master_carton']}\n• **Ventilation:** {tert['ventilation']}\n• **Cold-Chain:** {tert['cold_chain_setpoint']}")

    with col_rec_right:
        st.markdown("#### 📊 Shelf-Life Extension Horizon")
        fig_shelf = create_shelf_life_chart(sl, commodity_data["name"])
        st.plotly_chart(fig_shelf, use_container_width=True)
        
        st.markdown("#### 🕸️ Candidate Material Multi-Criteria Radar")
        fig_radar = create_radar_comparison_chart(rec_result["ranked_materials"])
        st.plotly_chart(fig_radar, use_container_width=True)


# =========================================================
# TAB 2: RESPIRATION KINETICS & EMAP SIMULATOR
# =========================================================
with tab2:
    st.markdown("### 🔬 Equilibrium Modified Atmosphere Packaging (EMAP) Simulator")
    
    if not commodity_data.get("is_respiring", False):
        st.warning(f"ℹ️ **{commodity_data['name']}** is a non-respiring food item (processed/dairy/dry food). EMAP respiration kinetics apply primarily to fresh fruits, vegetables, mushrooms, and greens. See Tab 1 and Tab 3 for barrier and active preservation.")
    else:
        emap_specs = calculate_required_emap_permeability(commodity_data, weight_kg, surface_area_m2, storage_temp)
        
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
            st.metric("Respiration Rate at T", f"{emap_specs['respiration_rate_mg_co2_per_kg_hr']} mg/kg·h", f"Storage at {storage_temp}°C")
        with col_e2:
            st.metric("Required Film OTR", f"{emap_specs['required_otr']} cm³/m²·d·atm", f"Target O₂: {emap_specs['target_o2_pct']}%")
        with col_e3:
            st.metric("Required Film CO₂TR", f"{emap_specs['required_co2tr']} cm³/m²·d·atm", f"Target CO₂: {emap_specs['target_co2_pct']}%")
        with col_e4:
            st.metric("Ideal Permeability Ratio (β)", f"{emap_specs['ideal_selectivity_beta']}", "CO₂TR / OTR")
            
        st.divider()
        st.markdown("#### ⏱️ Headspace Gas Transient Equilibrium Dynamics (0 - 72 Hours)")
        
        headspace_vol = st.slider("Package Headspace Gas Volume (Liters)", 0.1, 5.0, 0.4, 0.1)
        sim_data = simulate_gas_dynamics_over_time(commodity_data, top_mat, weight_kg, surface_area_m2, headspace_vol, storage_temp)
        
        col_sim_graph, col_sim_info = st.columns([1.3, 0.7])
        with col_sim_graph:
            fig_gas = create_gas_dynamics_chart(sim_data, commodity_data)
            st.plotly_chart(fig_gas, use_container_width=True)
        with col_sim_info:
            st.markdown(f"**Equilibrium Status:**\n### {sim_data['status']}")
            st.markdown(f"""
            - **Final Headspace O₂:** `{sim_data['final_o2']}%` (Target: {commodity_data.get('target_o2_min')}-{commodity_data.get('target_o2_max')}%)
            - **Final Headspace CO₂:** `{sim_data['final_co2']}%` (Tolerance: <{commodity_data.get('max_co2_tolerance')}%)
            
            **Biochemical Explanation:**
            Respiring produce consumes O2 and generates CO2. If packaging film permeance is too low (OTR < 50), oxygen is depleted to < 1%, triggering anaerobic fermentation, ethanol/acetaldehyde off-flavors, and tissue breakdown.
            
            *PackWise AI selected **{top_mat['name']}** to match the respiration rate and maintain safe aerobic equilibrium.*
            """)


# =========================================================
# TAB 3: ACTIVE & SMART SYSTEMS
# =========================================================
with tab3:
    st.markdown("### 💡 Recommended Active & Intelligent Packaging Add-ons")
    st.markdown("Active packaging actively alters internal conditions, while intelligent packaging monitors product condition and safety.")
    
    col_act, col_intel = st.columns(2)
    
    active_items = [t for t in active_tech if t["type"] == "Active Packaging"]
    intel_items = [t for t in active_tech if t["type"] == "Intelligent Packaging"]
    
    with col_act:
        st.markdown("#### ⚡ Active Scavengers & Regulators")
        if not active_items:
            st.info("No active additives required for this commodity profile.")
        for item in active_items:
            with st.expander(f"🔹 {item['category']}", expanded=True):
                st.markdown(f"**Mechanism:** {item['mechanism']}")
                st.markdown(f"**Preservation Action:** {item['action_mode']}")
                st.markdown(f"**Shelf-Life Boost:** `+{item['shelf_life_extension_pct']}%` | **Cost Impact:** `₹{item['cost_impact_inr_per_pack']:.2f}/pack`")
                st.caption(f"🛡️ Safety: {item['food_contact_safety']}")
                
    with col_intel:
        st.markdown("#### 🏷️ Intelligent Sensors & Digital Traceability")
        for item in intel_items:
            with st.expander(f"🔹 {item['category']}", expanded=True):
                st.markdown(f"**Working Principle:** {item['mechanism']}")
                st.markdown(f"**Function:** {item['action_mode']}")
                st.markdown(f"**Unit Cost:** `₹{item['cost_impact_inr_per_pack']:.2f}/pack`")
                st.caption(f"🛡️ Safety: {item['food_contact_safety']}")


# =========================================================
# TAB 4: ECO & COST ANALYSIS
# =========================================================
with tab4:
    st.markdown("### 🌱 Sustainability & Cost Tradeoff Matrix")
    
    fig_scatter = create_cost_sustainability_scatter(rec_result["ranked_materials"], top_mat["name"])
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("#### 📋 Full Candidate Materials Benchmark Table")
    df_ranked = pd.DataFrame(rec_result["ranked_materials"])[
        ["name", "category", "composite_score", "barrier_score", "sustainability_score", "cost_score", "cost_inr_per_kg", "is_biodegradable", "is_compostable"]
    ].rename(columns={
        "name": "Material Name",
        "category": "Classification",
        "composite_score": "AI Score",
        "barrier_score": "Barrier Score",
        "sustainability_score": "Eco Score",
        "cost_score": "Cost Score",
        "cost_inr_per_kg": "Cost (₹/kg)",
        "is_biodegradable": "Biodegradable",
        "is_compostable": "Compostable"
    })
    
    st.dataframe(df_ranked, hide_index=True, use_container_width=True)


# =========================================================
# TAB 5: TECHNICAL DOSSIER & PDF EXPORT
# =========================================================
with tab5:
    st.markdown("### 📑 MoFPI Technical Packaging Specification Dossier")
    st.markdown("Generate and download a comprehensive, lab-ready packaging technical dossier compliant with **FSSAI Food Contact Guidelines** and **MoFPI PMKSY/PMFME Standards**.")
    
    # Generate PDF in memory
    pdf_bytes = generate_dossier_pdf(rec_result, commodity_data, storage_temp, ambient_rh)
    
    c_down1, c_down2 = st.columns([0.6, 0.4])
    with c_down1:
        st.download_button(
            label="📥 Download Official Technical Dossier (PDF)",
            data=pdf_bytes,
            file_name=f"PackWise_MoFPI_Dossier_{selected_commodity_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    with c_down2:
        st.success("✅ Generated in accordance with MoFPI & IIP Packaging Norms")
        
    st.divider()
    
    # Dossier Preview in UI
    st.markdown("#### 📄 Document Preview")
    st.markdown(f"""
    **Document Code:** `MoFPI-SIH26236-{commodity_data['name'][:3].upper()}-2026`  
    **Commodity:** {commodity_data['name']} (*{commodity_data.get('hindi_name')}*)  
    **Category:** {commodity_data['category']}  
    **Recommended Primary Film:** {top_mat['name']} ({top_mat['thickness_um']} µm)  
    **Gas Transmission Profile:** OTR = {top_mat['otr']} cm³/m²·d·atm | WVTR = {top_mat['wvtr']} g/m²·d  
    **Active Packaging:** {', '.join([t['category'] for t in active_tech[:3]])}  
    **Traceability:** GS1 Digital Link dynamic QR code with harvest origin metadata  
    **Expected Shelf Life:** Extended from **{sl['unpacked_baseline_days']} Days** to **{sl['ai_intelligent_pack_days']} Days** (+{sl['extension_percentage']}%)  
    """)


# =========================================================
# TAB 6: GOVERNMENT SCHEMES & SUBSIDIES
# =========================================================
with tab6:
    st.markdown("### 🏛️ Ministry of Food Processing Industries (MoFPI) Schemes")
    st.markdown("Financial assistance, capital grants, and testing infrastructure available for Farmers, FPOs, and Food Processors adopting intelligent packaging.")
    
    col_sch1, col_sch2 = st.columns(2)
    
    with col_sch1:
        st.markdown("""
        #### 1. PM Kisan SAMPADA Yojana (PMKSY)
        **Integrated Cold Chain and Value Addition Infrastructure**
        - **Grant:** 35% to 50% capital grant for storage, pre-cooling, MAP packaging equipment, and reefer vans.
        - **Max Assistance:** Up to **₹10 Crore** per project.
        - **Target:** FPOs, Self-Help Groups (SHGs), Cooperatives, and Private Agri-Enterprises.
        - **Application:** Online via [MoFPI SAMPADA Portal](https://www.mofpi.gov.in).
        """)
        
        st.markdown("""
        #### 2. PMFME Scheme (Micro Food Processing Enterprises)
        **One District One Product (ODOP) Packaging Support**
        - **Subsidy:** 35% credit-linked capital subsidy up to **₹10 Lakh** per micro-enterprise.
        - **Special Focus:** Packaging upgradation, branding, and quality certification (FSSAI).
        - **Capacity Building:** Handholding through District Resource Persons (DRPs).
        """)
        
    with col_sch2:
        st.markdown("""
        #### 3. MoFPI R&D and Testing Institutes
        Access subsidized pilot-plant testing, migration testing, and shelf-life studies at:
        - **NIFTEM Kundli (Haryana):** National Institute of Food Technology Entrepreneurship and Management.
        - **NIFTEM Thanjavur (Tamil Nadu):** Advanced bio-packaging & cold chain testing labs.
        - **Indian Institute of Packaging (IIP Mumbai & Delhi):** Biodegradability & material testing.
        """)
        
        st.markdown("""
        #### 4. Plastic Waste Management (PWM) EPR Compliance
        - Under MoFPI and MoEFCC guidelines, food processors using certified compostable biopolymers (IS/ISO 17088) or mono-material recyclable films are eligible for Extended Producer Responsibility (EPR) green credits.
        """)

# Footer
st.divider()
st.caption("PackWise AI • MoFPI Smart India Hackathon (SIH26236) • Agriculture, FoodTech & Rural Development • Developed with Python, Streamlit & Plotly")
