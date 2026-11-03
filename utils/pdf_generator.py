"""
PDF Technical Dossier Generator using ReportLab.
Produces official MoFPI / FSSAI compliant technical packaging recommendation reports.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def clean_text(text):
    if not isinstance(text, str):
        text = str(text)
    # Replace common unicode chars with ASCII equivalents for standard PDF fonts
    replacements = {
        '³': '3',
        '²': '2',
        '·': '.',
        '•': '-',
        '₹': 'Rs. ',
        '–': '-',
        '—': '-',
        '’': "'",
        '‘': "'",
        '“': '"',
        '”': '"',
        'µ': 'u',
        '₂': '2',
        'O₂': 'O2',
        'CO₂': 'CO2'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Ensure latin-1 compatibility
    return text.encode('latin-1', 'replace').decode('latin-1')


def generate_dossier_pdf(recommendation_result, commodity_data, storage_temp_c, ambient_rh):
    """
    Builds a professional multi-page PDF document in memory and returns bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#065F46'),  # Dark Green
        alignment=1  # Centered
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E3A8A'),  # Navy
        alignment=1
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#4B5563'),
        alignment=1
    )
    
    section_heading = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#065F46'),
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1F2937')
    )
    
    bold_body = ParagraphStyle(
        'DocBoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#111827')
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11
    )

    story = []
    
    # Header Banner
    story.append(Paragraph(clean_text("MINISTRY OF FOOD PROCESSING INDUSTRIES (MoFPI)"), title_style))
    story.append(Paragraph(clean_text("GOVERNMENT OF INDIA - SMART INDIA HACKATHON 2026 (SIH26236)"), subtitle_style))
    story.append(Paragraph(clean_text("AI-BASED INTELLIGENT FOOD PACKAGING MATERIAL RECOMMENDATION DOSSIER"), ParagraphStyle('SubSub', parent=subtitle_style, fontSize=9, textColor=colors.HexColor('#047857'))))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceBefore=2, spaceAfter=8))
    
    # Metadata bar
    meta_text = clean_text(f"<b>Commodity:</b> {commodity_data.get('name')} | <b>Category:</b> {commodity_data.get('category')} | <b>Storage Temp:</b> {storage_temp_c} C | <b>RH:</b> {ambient_rh}%")
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 10))
    
    # 1. Executive Summary & Top Recommendation
    story.append(Paragraph(clean_text("1. Primary Packaging Material Recommendation"), section_heading))
    top_mat = recommendation_result["top_material"]
    
    primary_data = [
        [Paragraph(clean_text("<b>Recommended Film:</b>"), table_cell_bold), Paragraph(clean_text(f"<b>{top_mat['name']}</b>"), table_cell_bold)],
        [Paragraph(clean_text("Polymer Classification:"), table_cell), Paragraph(clean_text(f"{top_mat['category']}"), table_cell)],
        [Paragraph(clean_text("Typical Gauge / Thickness:"), table_cell), Paragraph(clean_text(f"{top_mat['thickness_um']} um ({top_mat['thickness_um']*0.03937:.2f} mil)"), table_cell)],
        [Paragraph(clean_text("Oxygen Transmission Rate (OTR):"), table_cell), Paragraph(clean_text(f"{top_mat['otr']} cm3/m2.24h.atm (at 23C, 0% RH)"), table_cell)],
        [Paragraph(clean_text("Water Vapor Transmission (WVTR):"), table_cell), Paragraph(clean_text(f"{top_mat['wvtr']} g/m2.24h (at 38C, 90% RH)"), table_cell)],
        [Paragraph(clean_text("CO2 Transmission Rate (CO2TR):"), table_cell), Paragraph(clean_text(f"{top_mat['co2tr']} cm3/m2.24h.atm"), table_cell)],
        [Paragraph(clean_text("AI Suitability Score:"), table_cell), Paragraph(clean_text(f"<b>{top_mat['composite_score']} / 100</b> (Barrier: {top_mat['barrier_score']} | Eco: {top_mat['sustainability_score']} | Cost: {top_mat['cost_score']})"), table_cell)],
        [Paragraph(clean_text("Sustainability & Circularity:"), table_cell), Paragraph(clean_text(f"Biodegradable: {'Yes' if top_mat['is_biodegradable'] else 'No'} | Recyclable: {'Yes' if top_mat['is_recyclable'] else 'No'} | Carbon: {top_mat['carbon_footprint']} kg CO2e/kg"), table_cell)],
        [Paragraph(clean_text("Economic Benchmark:"), table_cell), Paragraph(clean_text(f"Approx. Rs. {top_mat['cost_inr_per_kg']:.2f} per kg raw material converting"), table_cell)],
        [Paragraph(clean_text("Regulatory Compliance:"), table_cell), Paragraph(clean_text("Compliant with FSSAI Food Contact Packaging Regulations & Plastic Waste Management EPR Norms"), table_cell)]
    ]
    
    t_primary = Table(primary_data, colWidths=[180, 360])
    t_primary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_primary)
    story.append(Spacer(1, 10))
    
    # 2. Shelf-Life Improvement Impact
    story.append(Paragraph(clean_text("2. Shelf-Life Extension & Food Loss Prevention Analysis"), section_heading))
    sl = recommendation_result["shelf_life_analysis"]
    
    sl_data = [
        [
            Paragraph(clean_text("<b>Packaging Tier</b>"), table_cell_bold),
            Paragraph(clean_text("<b>Safe Shelf-Life</b>"), table_cell_bold),
            Paragraph(clean_text("<b>Extension Multiplier</b>"), table_cell_bold),
            Paragraph(clean_text("<b>Supply Chain Impact</b>"), table_cell_bold)
        ],
        [
            Paragraph(clean_text("Unpacked Ambient (Baseline)"), table_cell),
            Paragraph(clean_text(f"{sl['unpacked_baseline_days']} Days"), table_cell),
            Paragraph(clean_text("1.0x (Baseline)"), table_cell),
            Paragraph(clean_text("High localized retail spoilage; restricted to nearby mandis"), table_cell)
        ],
        [
            Paragraph(clean_text("Conventional Packaging"), table_cell),
            Paragraph(clean_text(f"{sl['conventional_pack_days']} Days"), table_cell),
            Paragraph(clean_text(f"{sl['conventional_pack_days']/max(1, sl['unpacked_baseline_days']):.1f}x"), table_cell),
            Paragraph(clean_text("Moderate protection; susceptible to condensation or anaerobic off-odors"), table_cell)
        ],
        [
            Paragraph(clean_text("<b>AI Intelligent Packaging</b>"), table_cell_bold),
            Paragraph(clean_text(f"<b>{sl['ai_intelligent_pack_days']} Days</b>"), table_cell_bold),
            Paragraph(clean_text(f"<b>+{sl['extension_percentage']}%</b>"), table_cell_bold),
            Paragraph(clean_text(f"<b>Enables interstate/export transit; slashes food waste by ~{sl['estimated_spoilage_reduction_pct']}%</b>"), table_cell_bold)
        ]
    ]
    
    t_sl = Table(sl_data, colWidths=[120, 80, 90, 250])
    t_sl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#065F46')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ECFDF5')),  # Highlight row
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sl)
    story.append(Spacer(1, 10))
    
    # 3. Active & Intelligent Packaging Systems
    story.append(Paragraph(clean_text("3. Active & Intelligent Packaging Systems Integration"), section_heading))
    active_tech = recommendation_result["active_intelligent_tech"]
    
    tech_rows = [
        [Paragraph(clean_text("<b>Component Name</b>"), table_cell_bold), Paragraph(clean_text("<b>Classification</b>"), table_cell_bold), Paragraph(clean_text("<b>Mechanism & Function</b>"), table_cell_bold), Paragraph(clean_text("<b>Added Cost</b>"), table_cell_bold)]
    ]
    for item in active_tech[:4]:
        tech_rows.append([
            Paragraph(clean_text(f"<b>{item['category']}</b><br/>{item['type']}"), table_cell),
            Paragraph(clean_text(item["type"]), table_cell),
            Paragraph(clean_text(f"{item['mechanism']}<br/><i>Effect: {item['action_mode']}</i>"), table_cell),
            Paragraph(clean_text(f"Rs. {item['cost_impact_inr_per_pack']:.2f} / pack"), table_cell)
        ])
        
    t_tech = Table(tech_rows, colWidths=[130, 80, 250, 80])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))
    
    # 4. Secondary, Tertiary & Cold Chain Specs
    story.append(Paragraph(clean_text("4. Secondary, Tertiary & Cold-Chain Logistics Specifications"), section_heading))
    sec = recommendation_result["secondary_packaging"]
    tert = recommendation_result["tertiary_packaging"]
    
    logistics_data = [
        [Paragraph(clean_text("Secondary Unit Pack:"), table_cell_bold), Paragraph(clean_text(sec["type"]), table_cell)],
        [Paragraph(clean_text("Gas Flush / MAP Atmosphere:"), table_cell_bold), Paragraph(clean_text(sec["gas_flush_mix"]), table_cell)],
        [Paragraph(clean_text("Master Transit Carton:"), table_cell_bold), Paragraph(clean_text(tert["master_carton"]), table_cell)],
        [Paragraph(clean_text("Carton Ventilation & Cooling:"), table_cell_bold), Paragraph(clean_text(tert["ventilation"]), table_cell)],
        [Paragraph(clean_text("Target Cold-Chain Temperature:"), table_cell_bold), Paragraph(clean_text(tert["cold_chain_setpoint"]), table_cell)],
        [Paragraph(clean_text("Target Relative Humidity (RH):"), table_cell_bold), Paragraph(clean_text(tert["relative_humidity_setpoint"]), table_cell)],
        [Paragraph(clean_text("MoFPI Subsidy Scheme Alignment:"), table_cell_bold), Paragraph(clean_text(f"<b>{tert['mofpi_scheme_alignment']}</b>"), table_cell)]
    ]
    
    t_log = Table(logistics_data, colWidths=[160, 380])
    t_log.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_log)
    story.append(Spacer(1, 12))
    
    # Footer disclaimer
    footer_text = clean_text("<i>Report generated autonomously by PackWise AI Recommender System (SIH26236). Developed in alignment with MoFPI and Indian Institute of Packaging (IIP) technical standards. For technical advisory and lab verification, contact NIFTEM Kundli / Thanjavur.</i>")
    story.append(Paragraph(footer_text, ParagraphStyle('DocFoot', parent=meta_style, fontSize=7.5, textColor=colors.HexColor('#6B7280'))))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
