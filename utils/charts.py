"""
Interactive Plotly Visualization Generators for Packaging Decision Support.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def create_radar_comparison_chart(top_materials):
    """
    Creates a multi-axis Radar chart comparing the top 3 candidate materials.
    """
    categories = ['Barrier Match', 'Eco Sustainability', 'Cost Advantage', 'Mechanical Strength', 'Overall AI Index']
    
    fig = go.Figure()
    
    colors = ['#10B981', '#3B82F6', '#F59E0B']  # Emerald, Blue, Amber
    
    for idx, mat in enumerate(top_materials[:3]):
        values = [
            mat["barrier_score"],
            mat["sustainability_score"],
            mat["cost_score"],
            mat["mechanical_score"],
            mat["composite_score"]
        ]
        # Close the loop
        values.append(values[0])
        radar_cats = categories + [categories[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=radar_cats,
            fill='toself',
            name=mat["name"],
            line=dict(color=colors[idx % len(colors)], width=2.5),
            opacity=0.65 if idx == 0 else 0.4
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color="#6B7280"),
                linecolor="#E5E7EB"
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#1F2937", family="sans-serif")
            )
        ),
        showlegend=True,
        title=dict(
            text="Candidate Materials Multi-Criteria Performance Comparison",
            font=dict(size=15, color="#111827", family="sans-serif")
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
    )
    
    return fig


def create_shelf_life_chart(shelf_life_data, commodity_name):
    """
    Creates a stylized bar chart showing shelf-life expansion.
    """
    stages = ['Unpacked (Room Temp)', 'Conventional Pack', 'AI Intelligent Packaging']
    days = [
        shelf_life_data["unpacked_baseline_days"],
        shelf_life_data["conventional_pack_days"],
        shelf_life_data["ai_intelligent_pack_days"]
    ]
    colors = ['#EF4444', '#F59E0B', '#10B981']  # Red, Amber, Emerald
    
    fig = go.Figure(data=[
        go.Bar(
            x=stages,
            y=days,
            marker_color=colors,
            text=[f"{d} Days" for d in days],
            textposition='auto',
            textfont=dict(size=14, color='white', family='sans-serif'),
            width=0.45
        )
    ])
    
    fig.update_layout(
        title=f"Shelf-Life Extension Analysis: {commodity_name}",
        yaxis=dict(title="Estimated Safe Shelf Life (Days)", gridcolor="#F3F4F6"),
        xaxis=dict(tickfont=dict(size=12, color="#374151")),
        plot_bgcolor="white",
        margin=dict(l=30, r=30, t=50, b=40)
    )
    
    return fig


def create_gas_dynamics_chart(gas_sim_data, commodity_data):
    """
    Creates an interactive transient headspace gas equilibrium chart.
    """
    if not gas_sim_data:
        return None
        
    t = gas_sim_data["time_hours"]
    o2 = gas_sim_data["o2_curve"]
    co2 = gas_sim_data["co2_curve"]
    
    fig = go.Figure()
    
    # O2 curve
    fig.add_trace(go.Scatter(
        x=t,
        y=o2,
        mode='lines',
        name='Headspace O₂ (%)',
        line=dict(color='#2563EB', width=3)
    ))
    
    # CO2 curve
    fig.add_trace(go.Scatter(
        x=t,
        y=co2,
        mode='lines',
        name='Headspace CO₂ (%)',
        line=dict(color='#DC2626', width=3, dash='dash')
    ))
    
    # Target O2 optimal band
    o2_min = commodity_data.get("target_o2_min", 3.0)
    o2_max = commodity_data.get("target_o2_max", 5.0)
    fig.add_hrect(
        y0=o2_min, y1=o2_max,
        fillcolor="rgba(37, 99, 235, 0.12)", line_width=0,
        annotation_text="Target O₂ Zone (No Fermentation)", annotation_position="top right",
        annotation_font_size=10, annotation_font_color="#1D4ED8"
    )
    
    # Target CO2 optimal band
    co2_min = commodity_data.get("target_co2_min", 5.0)
    co2_max = commodity_data.get("target_co2_max", 10.0)
    fig.add_hrect(
        y0=co2_min, y1=co2_max,
        fillcolor="rgba(220, 38, 38, 0.10)", line_width=0,
        annotation_text="Target CO₂ Zone (Antimicrobial)", annotation_position="bottom right",
        annotation_font_size=10, annotation_font_color="#B91C1C"
    )
    
    fig.update_layout(
        title="EMAP Dynamic Gas Convergence Over Time (0 - 72 Hours)",
        xaxis=dict(title="Time (Hours Elapsed Post-Packaging)", gridcolor="#F3F4F6"),
        yaxis=dict(title="Gas Concentration (% Headspace Volume)", gridcolor="#F3F4F6", range=[0, max(25, max(co2) + 5)]),
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=30, r=30, t=60, b=40)
    )
    
    return fig


def create_cost_sustainability_scatter(all_materials, selected_material_name):
    """
    Creates a Tradeoff scatter plot: Cost vs Eco Sustainability.
    """
    df_data = []
    for mat in all_materials:
        df_data.append({
            "Name": mat["name"],
            "Category": mat["category"],
            "Cost (₹/kg)": mat["cost_inr_per_kg"],
            "Sustainability Score": mat["sustainability_score"],
            "Overall Score": mat["composite_score"],
            "Biodegradable": "Yes" if mat["is_biodegradable"] else "No",
            "IsSelected": mat["name"] == selected_material_name
        })
        
    df = pd.DataFrame(df_data)
    
    fig = px.scatter(
        df,
        x="Cost (₹/kg)",
        y="Sustainability Score",
        size="Overall Score",
        color="Category",
        hover_name="Name",
        hover_data=["Cost (₹/kg)", "Sustainability Score", "Overall Score", "Biodegradable"],
        title="Cost vs Sustainability Tradeoff Matrix across Packaging Materials"
    )
    
    fig.update_layout(
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#F3F4F6"),
        yaxis=dict(gridcolor="#F3F4F6", range=[20, 105]),
        margin=dict(l=30, r=30, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
    )
    
    return fig
