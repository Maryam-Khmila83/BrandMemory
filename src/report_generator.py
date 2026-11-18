from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)

from src.campaign_analytics import (
    load_fashionco_data,
    analyze_by_theme,
    analyze_by_platform,
    analyze_monthly_trends,
    generate_monthly_insights,
    detect_roas_anomalies,
)


# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_DIR / "reports" / "generated"
LOGO_PATH = PROJECT_DIR / "frontend" / "public" / "brand" / "brandmemory-icon.png"


# BrandMemory colors
PURPLE = colors.HexColor("#9275BD")
LIGHT_PURPLE = colors.HexColor("#F0EAFA")
DARK = colors.HexColor("#292536")
GREY = colors.HexColor("#777380")
BORDER = colors.HexColor("#EAE6F0")


def format_money(value):
    return f"${value:,.2f}"


def format_number(value):
    return f"{value:,.0f}"


def create_table(data, widths):
    """Create a consistently styled PDF table."""

    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_PURPLE),
            ("TEXTCOLOR", (0, 0), (-1, 0), DARK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 11),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#FAF9FC")]),
        ])
    )

    return table


def add_page_footer(canvas, document):
    """Add a footer to every PDF page."""

    canvas.saveState()

    canvas.setStrokeColor(BORDER)
    canvas.line(
        15 * mm,
        12 * mm,
        282 * mm,
        12 * mm,
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)

    canvas.drawString(
        15 * mm,
        7 * mm,
        "BrandMemory | FashionCo Marketing Intelligence",
    )

    canvas.drawRightString(
        282 * mm,
        7 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()


def generate_marketing_report():

    # Create output directory
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load campaign data
    df = load_fashionco_data()

    # Run existing analytics
    theme_results = analyze_by_theme(df)
    platform_results = analyze_by_platform(df)
    monthly_results = analyze_monthly_trends(df)

    monthly_insights = generate_monthly_insights(
        monthly_results
    )

    anomalies = detect_roas_anomalies(
        monthly_results
    )

    # Overall KPIs
    total_spend = df["spend"].sum()
    total_revenue = df["revenue"].sum()
    total_conversions = df["conversions"].sum()

    overall_roas = (
        total_revenue / total_spend
        if total_spend != 0
        else 0
    )

    first_date = df["first_date"].min()
    last_date = df["last_date"].max()

    # File name
    generated_at = datetime.now()
    filename = (
        f"fashionco_marketing_report_"
        f"{generated_at.strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    output_path = REPORTS_DIR / filename

    # Create PDF document
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=8 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            textColor=DARK,
            alignment=TA_CENTER,
            spaceAfter=14,
        )
    )

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        textColor=GREY,
        alignment=TA_CENTER,
        spaceAfter=18,
    ))

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=PURPLE,
            spaceBefore=16,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallNote",
            parent=styles["Normal"],
            fontSize=8,
            textColor=GREY,
            leading=11,
        )
    )

    story = []

    # BrandMemory icon
    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH), width=18 * mm, height=18 * mm)
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 5))

    # Report title
    story.append(
        Paragraph("FashionCo Marketing Performance", styles["ReportTitle"])
    )

    story.append(
        Paragraph("Marketing Intelligence Report", styles["ReportSubtitle"])
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Reporting period:</b> {first_date} to {last_date}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Generated:</b> "
            f"{generated_at.strftime('%d %B %Y, %H:%M')}",
            styles["Normal"],
        )
    )

    # =====================================
    # EXECUTIVE SUMMARY
    # =====================================

    story.append(
        Paragraph(
            "Executive Summary",
            styles["SectionTitle"],
        )
    )

    kpi_data = [
        ["Campaign Groups", "Total Spend", "Total Revenue",
         "Conversions", "Overall ROAS"],

        [
            format_number(len(df)),
            format_money(total_spend),
            format_money(total_revenue),
            format_number(total_conversions),
            f"{overall_roas:.2f}x",
        ],
    ]

    story.append(
        create_table(
            kpi_data,
            [45 * mm, 45 * mm, 45 * mm, 45 * mm, 45 * mm],
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "ROAS represents recorded revenue divided by advertising "
            "spend. It does not represent profit or prove that advertising "
            "caused the recorded revenue.",
            styles["SmallNote"],
        )
    )

    # =====================================
    # PERFORMANCE BY THEME
    # =====================================

    story.append(
        Paragraph(
            "Performance by Campaign Theme",
            styles["SectionTitle"],
        )
    )

    theme_data = [[
        "Theme",
        "Campaign Groups",
        "Spend",
        "Revenue",
        "Conversions",
        "ROAS",
    ]]

    for _, row in theme_results.iterrows():
        theme_data.append([
            str(row["theme"]),
            format_number(row["campaigns"]),
            format_money(row["total_spend"]),
            format_money(row["total_revenue"]),
            format_number(row["total_conversions"]),
            f'{row["roas"]:.2f}x',
        ])

    story.append(
        create_table(
            theme_data,
            [40 * mm, 35 * mm, 40 * mm, 40 * mm, 35 * mm, 25 * mm],
        )
    )

    # =====================================
    # PERFORMANCE BY PLATFORM
    # =====================================

    story.append(
        Paragraph(
            "Performance by Advertising Platform",
            styles["SectionTitle"],
        )
    )

    platform_data = [[
        "Platform",
        "Campaign Groups",
        "Spend",
        "Revenue",
        "Conversions",
        "ROAS",
    ]]

    for _, row in platform_results.iterrows():
        platform_data.append([
            str(row["platform"]),
            format_number(row["campaign_groups"]),
            format_money(row["total_spend"]),
            format_money(row["total_revenue"]),
            format_number(row["total_conversions"]),
            f'{row["roas"]:.2f}x',
        ])

    story.append(
        create_table(
            platform_data,
            [40 * mm, 35 * mm, 40 * mm, 40 * mm, 35 * mm, 25 * mm],
        )
    )

    # =====================================
    # MONTHLY TRENDS
    # =====================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Monthly Conversion Performance",
            styles["SectionTitle"],
        )
    )

    monthly_data = [[
        "Month",
        "Campaign Groups",
        "Spend",
        "Revenue",
        "Conversions",
        "ROAS",
    ]]

    for _, row in monthly_results.iterrows():
        monthly_data.append([
            str(row["month_date"]),
            format_number(row["campaign_groups"]),
            format_money(row["total_spend"]),
            format_money(row["total_revenue"]),
            format_number(row["total_conversions"]),
            f'{row["roas"]:.2f}x',
        ])

    story.append(
        create_table(
            monthly_data,
            [40 * mm, 35 * mm, 40 * mm, 40 * mm, 35 * mm, 25 * mm],
        )
    )

    # =====================================
    # AUTOMATIC INSIGHTS
    # =====================================

    story.append(
        Paragraph(
            "Monthly Performance Insights",
            styles["SectionTitle"],
        )
    )

    for insight in monthly_insights:
        story.append(
            Paragraph(
                f"• {insight}",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 4))

    # =====================================
    # ROAS ANOMALIES
    # =====================================

    story.append(
        Paragraph(
            "Unusual Monthly Performance",
            styles["SectionTitle"],
        )
    )

    if anomalies.empty:
        anomaly_text = "No statistical ROAS anomalies were detected."
    else:
        anomaly_text = ""

        for _, row in anomalies.iterrows():
            anomaly_text += (
                f"• {row['month_date']}: "
                f"ROAS {row['roas']:.2f}x (statistical outlier)<br/>"
            )

    story.append(
        Paragraph(
            anomaly_text,
            styles["Normal"],
        )
    )

    # =====================================
    # DATA DISCLAIMER
    # =====================================

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "Data Disclaimer",
            styles["SectionTitle"],
        )
    )

    story.append(
        Paragraph(
            "This report uses public dataset-derived and simulated "
            "FashionCo demonstration data. It does not represent verified "
            "results from a real company. ROAS is a revenue-to-advertising-"
            "spend ratio, not a measure of profit. Statistical anomalies "
            "identify unusual values and do not establish their causes. "
            "Performance comparisons should not be interpreted as proof "
            "of causation.",
            styles["SmallNote"],
        )
    )

    # Generate PDF
    document.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )

    return output_path