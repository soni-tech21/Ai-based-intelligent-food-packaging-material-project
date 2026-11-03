"""
Intelligent and Active Packaging Technologies Database.
Covers scavengers, emitters, freshness indicators, TTIs, and smart traceability.
"""

ACTIVE_INTELLIGENT_TECH_DB = {
    # --- ACTIVE PACKAGING SYSTEMS ---
    "Iron-Based Oxygen Absorber Sachet (50-100cc)": {
        "type": "Active Packaging",
        "category": "Oxygen Scavenger",
        "mechanism": "Irreversible oxidation of food-grade powdered iron (Fe + O2 + H2O -> Fe2O3*xH2O), reducing package O2 to < 0.01%.",
        "best_suited_for": ["Bakery & Confectionery", "Dairy & Fermented Foods", "Snacks & Fried Foods"],
        "shelf_life_extension_pct": 120,
        "cost_impact_inr_per_pack": 0.65,
        "food_contact_safety": "Approved (Must include 'Do Not Eat' warning on non-toxic permeable pouch)",
        "action_mode": "Prevents lipid oxidation rancidity, mold growth, and off-flavors."
    },
    "Potassium Permanganate Ethylene Scrubber (KMnO4)": {
        "type": "Active Packaging",
        "category": "Ethylene Absorber",
        "mechanism": "Oxidizes plant-emitted ethylene gas (C2H4) into CO2 and H2O across an active alumina/zeolite carrier substrate.",
        "best_suited_for": ["Fresh Produce (Fruits & Vegetables)"],
        "shelf_life_extension_pct": 80,
        "cost_impact_inr_per_pack": 0.85,
        "food_contact_safety": "Approved for enclosed secondary/sachet use (no direct food migration)",
        "action_mode": "Halts climacteric ripening cascades in mangoes, bananas, tomatoes, and apples."
    },
    "Dual-Action Relative Humidity Regulator Pad (65-85% RH)": {
        "type": "Active Packaging",
        "category": "Moisture Absorber",
        "mechanism": "Natural bentonite clay / food-grade calcium chloride hydrogel absorbing excess condensation or releasing moisture to prevent transpiration wilting.",
        "best_suited_for": ["Fresh Produce (Fruits & Vegetables)", "Bakery & Confectionery"],
        "shelf_life_extension_pct": 50,
        "cost_impact_inr_per_pack": 0.45,
        "food_contact_safety": "Direct food contact safe",
        "action_mode": "Eliminates free water droplets inside pouch, suppressing water-soaking and fungal rot."
    },
    "Sodium Bicarbonate / Citric Acid CO2 Emitter Pad": {
        "type": "Active Packaging",
        "category": "CO2 Emitter",
        "mechanism": "Absorbs natural meat/poultry exudate purge, triggering reaction that releases gaseous CO2 into headspace to maintain 20-30% CO2.",
        "best_suited_for": ["Meat, Poultry & Seafood"],
        "shelf_life_extension_pct": 90,
        "cost_impact_inr_per_pack": 1.20,
        "food_contact_safety": "Direct food contact certified (absorbent pad format)",
        "action_mode": "Inhibits Gram-negative psychrotrophic bacteria (Pseudomonas) in chilled poultry and red meat."
    },
    "Bio-Active Oregano & Thyme Essential Oil Vapor Pad": {
        "type": "Active Packaging",
        "category": "Antimicrobial Release System",
        "mechanism": "Controlled slow-release of natural carvacrol and thymol volatiles disrupting microbial cell membranes without chemical synthetic preservatives.",
        "best_suited_for": ["Dairy & Fermented Foods", "Bakery & Confectionery", "Fresh Produce (Fruits & Vegetables)"],
        "shelf_life_extension_pct": 75,
        "cost_impact_inr_per_pack": 1.10,
        "food_contact_safety": "GRAS (Generally Recognized As Safe) organic compliant",
        "action_mode": "Suppresses yeast, Penicillium mold, and Listeria monocytogenes on paneer and berries."
    },

    # --- INTELLIGENT PACKAGING INDICATORS ---
    "Enzymatic / Chemical Time-Temperature Indicator (TTI Label)": {
        "type": "Intelligent Packaging",
        "category": "Cold Chain Integrity Monitor",
        "mechanism": "Polymerization or enzymatic substrate color shift (Green -> Amber -> Red) correlating directly with cumulative thermal exposure and Arrhenius degradation.",
        "best_suited_for": ["Dairy & Fermented Foods", "Meat, Poultry & Seafood", "Fresh Produce (Fruits & Vegetables)"],
        "shelf_life_extension_pct": 0,  # Monitoring only
        "cost_impact_inr_per_pack": 1.50,
        "food_contact_safety": "External surface adhesive label",
        "action_mode": "Alerts supply chain handlers and consumers if cold chain was breached during transit."
    },
    "Natural Anthocyanin-Based pH Freshness Indicator": {
        "type": "Intelligent Packaging",
        "category": "Spoilage & Freshness Sensor",
        "mechanism": "Plant-derived anthocyanin / curcumin dye changing from purple/red to green/yellow upon reacting with Total Volatile Basic Nitrogen (TVB-N) gases.",
        "best_suited_for": ["Meat, Poultry & Seafood", "Dairy & Fermented Foods"],
        "shelf_life_extension_pct": 0,
        "cost_impact_inr_per_pack": 0.90,
        "food_contact_safety": "Non-toxic biodegradable cellulose substrate",
        "action_mode": "Provides real-time visual verification of meat freshness without opening the hermetic seal."
    },
    "Colorimetric Oxygen Leak Indicator Tab": {
        "type": "Intelligent Packaging",
        "category": "Hermetic Seal & MAP Integrity",
        "mechanism": "Redox dye tablet (e.g. methylene blue / cysteine) that stays pink in <0.1% O2 and turns dark blue immediately upon air ingress.",
        "best_suited_for": ["Bakery & Confectionery", "Snacks & Fried Foods", "Dairy & Fermented Foods"],
        "shelf_life_extension_pct": 0,
        "cost_impact_inr_per_pack": 0.75,
        "food_contact_safety": "Placed in visible blister window inside headspace",
        "action_mode": "Detects pinholes, micro-leaks, or faulty heat seals before retail sale."
    },
    "Smart Dynamic QR Code with Batch Traceability & Harvest Metadata": {
        "type": "Intelligent Packaging",
        "category": "Digital Farm-to-Fork Traceability",
        "mechanism": "GS1 Digital Link 2D barcode encoding FSSAI batch number, farm geocode, pack date, simulated dynamic shelf-life, and storage guidelines.",
        "best_suited_for": ["All Commodities"],
        "shelf_life_extension_pct": 15,  # Better FIFO logistics
        "cost_impact_inr_per_pack": 0.15,
        "food_contact_safety": "Food-grade vegetable ink printed on outer label",
        "action_mode": "Enables farmers/FPOs to verify origin, fetch premium pricing, and track inventory."
    }
}


def get_active_intelligent_recommendations(commodity_data, storage_temp):
    """
    Rule-based intelligent filtering of active and smart tech for given food commodity.
    """
    category = commodity_data.get("category", "")
    is_respiring = commodity_data.get("is_respiring", False)
    fat_pct = commodity_data.get("fat_pct", 0)
    moisture_pct = commodity_data.get("moisture_pct", 0)
    water_activity = commodity_data.get("water_activity", 0.5)
    ethylene_prod = commodity_data.get("ethylene_production", "None")
    
    recommended_tech = []
    
    # 1. Ethylene scrubber check
    if is_respiring and ethylene_prod in ["Moderate", "High", "Very High"]:
        recommended_tech.append("Potassium Permanganate Ethylene Scrubber (KMnO4)")
        
    # 2. Moisture regulator check
    if is_respiring and moisture_pct > 80:
        recommended_tech.append("Dual-Action Relative Humidity Regulator Pad (65-85% RH)")
        
    # 3. Oxygen absorber check for high fat / low moisture or mold prone
    if (fat_pct >= 15.0 or category in ["Bakery & Confectionery", "Dairy & Fermented Foods"]) and not is_respiring:
        recommended_tech.append("Iron-Based Oxygen Absorber Sachet (50-100cc)")
        
    # 4. CO2 emitter for meat/seafood
    if category == "Meat, Poultry & Seafood":
        recommended_tech.append("Sodium Bicarbonate / Citric Acid CO2 Emitter Pad")
        recommended_tech.append("Natural Anthocyanin-Based pH Freshness Indicator")
        
    # 5. Cold chain TTI
    if storage_temp <= 10.0 or category in ["Meat, Poultry & Seafood", "Dairy & Fermented Foods"]:
        recommended_tech.append("Enzymatic / Chemical Time-Temperature Indicator (TTI Label)")
        
    # 6. Antimicrobial pad for moisture sensitive dairy/berry
    if water_activity > 0.90 and category in ["Dairy & Fermented Foods", "Fresh Produce (Fruits & Vegetables)"]:
        recommended_tech.append("Bio-Active Oregano & Thyme Essential Oil Vapor Pad")
        
    # 7. Leak indicator for MAP/gas flushed products
    if not is_respiring and category in ["Bakery & Confectionery", "Snacks & Fried Foods"]:
        recommended_tech.append("Colorimetric Oxygen Leak Indicator Tab")
        
    # Always include smart QR traceability
    recommended_tech.append("Smart Dynamic QR Code with Batch Traceability & Harvest Metadata")
    
    return [ACTIVE_INTELLIGENT_TECH_DB[k] for k in recommended_tech if k in ACTIVE_INTELLIGENT_TECH_DB]
