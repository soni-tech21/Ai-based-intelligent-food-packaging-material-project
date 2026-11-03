"""
Equilibrium Modified Atmosphere Packaging (EMAP) Respiration Kinetics Engine.
Calculates temperature-dependent respiration rates, required OTR/CO2TR, and gas equilibrium dynamics.
"""

import numpy as np

MG_CO2_TO_CM3_O2 = 0.509  # 1 mg CO2 at STP is approx 0.509 cm3 gas

def calculate_temperature_adjusted_respiration(base_rate_20c, q10, temp_c):
    """
    Calculates respiration rate at target temperature using Arrhenius Q10 model.
    R(T) = R(20) * Q10^((T - 20) / 10)
    """
    return base_rate_20c * (q10 ** ((temp_c - 20.0) / 10.0))


def calculate_required_emap_permeability(commodity_data, weight_kg, package_surface_area_m2, temp_c):
    """
    Calculates required OTR and CO2TR of packaging film to achieve optimal headspace atmosphere.
    Returns:
        dict with required_otr, required_co2tr, target_o2, target_co2, current_respiration_rate
    """
    if not commodity_data.get("is_respiring", False):
        return None
        
    base_rate = commodity_data.get("respiration_rate_20c", 40.0)
    q10 = commodity_data.get("q10_factor", 2.0)
    rq = commodity_data.get("rq", 1.0)
    
    # Respiration in mg CO2/kg*hr at current storage temperature
    r_t_mg = calculate_temperature_adjusted_respiration(base_rate, q10, temp_c)
    
    # Convert to cm3 O2 consumed per kg per hour
    r_o2_cm3_hr = (r_t_mg / rq) * MG_CO2_TO_CM3_O2
    r_co2_cm3_hr = r_t_mg * MG_CO2_TO_CM3_O2
    
    # Target optimal gas concentrations (fractions)
    target_o2_pct = (commodity_data.get("target_o2_min", 3.0) + commodity_data.get("target_o2_max", 5.0)) / 2.0
    target_co2_pct = (commodity_data.get("target_co2_min", 5.0) + commodity_data.get("target_co2_max", 8.0)) / 2.0
    
    y_o2 = target_o2_pct / 100.0
    y_co2 = target_co2_pct / 100.0
    ambient_o2 = 0.209
    ambient_co2 = 0.0004
    
    # Driving gradient: (ambient - internal)
    delta_o2 = max(0.01, ambient_o2 - y_o2)
    delta_co2 = max(0.01, y_co2 - ambient_co2)
    
    # Required OTR in cm3 / m2 * 24h * atm
    # Permeation = (OTR * Area * delta_p) / 24h = Consumption = Weight * R_O2
    required_otr = (weight_kg * r_o2_cm3_hr * 24.0) / (package_surface_area_m2 * delta_o2)
    required_co2tr = (weight_kg * r_co2_cm3_hr * 24.0) / (package_surface_area_m2 * delta_co2)
    
    ideal_selectivity = required_co2tr / max(1.0, required_otr)
    
    return {
        "storage_temp_c": temp_c,
        "respiration_rate_mg_co2_per_kg_hr": round(r_t_mg, 2),
        "r_o2_cm3_per_kg_hr": round(r_o2_cm3_hr, 2),
        "target_o2_pct": target_o2_pct,
        "target_co2_pct": target_co2_pct,
        "required_otr": round(required_otr, 1),
        "required_co2tr": round(required_co2tr, 1),
        "ideal_selectivity_beta": round(ideal_selectivity, 2)
    }


def simulate_gas_dynamics_over_time(commodity_data, material_data, weight_kg, surface_area_m2, headspace_volume_l, temp_c, hours=72):
    """
    Simulates transient O2 and CO2 concentration in the headspace over time.
    Returns:
        time_steps, o2_curve (pct), co2_curve (pct), status ('Equilibrium', 'Hypoxia Risk', 'Aerobic Stagnation')
    """
    if not commodity_data.get("is_respiring", False):
        return None
        
    time_pts = np.linspace(0, hours, 100)
    dt = time_pts[1] - time_pts[0]  # hours
    
    base_rate = commodity_data.get("respiration_rate_20c", 40.0)
    q10 = commodity_data.get("q10_factor", 2.0)
    rq = commodity_data.get("rq", 1.0)
    r_t_mg = calculate_temperature_adjusted_respiration(base_rate, q10, temp_c)
    
    v_hs_cm3 = headspace_volume_l * 1000.0  # cm3
    otr_per_hr = (material_data["otr"] * surface_area_m2) / 24.0  # cm3/hr*atm
    co2tr_per_hr = (material_data["co2tr"] * surface_area_m2) / 24.0
    
    # Initial ambient conditions
    o2_pct = 20.9
    co2_pct = 0.04
    
    o2_history = []
    co2_history = []
    
    # Michaelis-Menten respiration inhibition at low O2: Km ~ 0.5-1.5% O2
    km_o2 = 1.0
    
    for t in time_pts:
        o2_history.append(o2_pct)
        co2_history.append(co2_pct)
        
        # Enzyme activity factor based on Michaelis-Menten kinetics
        activity_factor = max(0.05, o2_pct / (km_o2 + o2_pct))
        
        consumed_o2 = weight_kg * (r_t_mg / rq) * MG_CO2_TO_CM3_O2 * activity_factor * dt
        produced_co2 = weight_kg * r_t_mg * MG_CO2_TO_CM3_O2 * activity_factor * dt
        
        ingress_o2 = otr_per_hr * ((20.9 - o2_pct) / 100.0) * dt
        egress_co2 = co2tr_per_hr * ((co2_pct - 0.04) / 100.0) * dt
        
        net_delta_o2_cm3 = ingress_o2 - consumed_o2
        net_delta_co2_cm3 = produced_co2 - egress_co2
        
        # Update percentage concentrations
        o2_pct = max(0.1, min(20.9, o2_pct + (net_delta_o2_cm3 / v_hs_cm3) * 100.0))
        co2_pct = max(0.04, min(30.0, co2_pct + (net_delta_co2_cm3 / v_hs_cm3) * 100.0))
        
    final_o2 = o2_history[-1]
    final_co2 = co2_history[-1]
    
    if final_o2 < 1.5:
        risk_status = "⚠️ Anaerobic Risk (Fermentation / Off-Odors)"
    elif final_co2 > commodity_data.get("max_co2_tolerance", 15.0):
        risk_status = "⚠️ CO2 Injury Risk (Tissue Breakdown)"
    elif 2.0 <= final_o2 <= 8.0 and 2.0 <= final_co2 <= 15.0:
        risk_status = " Optimal Equilibrium MAP Achieved"
    else:
        risk_status = "ℹ️ Moderate Aerobic Plateau"
        
    return {
        "time_hours": time_pts.tolist(),
        "o2_curve": [round(x, 2) for x in o2_history],
        "co2_curve": [round(x, 2) for x in co2_history],
        "final_o2": round(final_o2, 2),
        "final_co2": round(final_co2, 2),
        "status": risk_status
    }
