
from pathlib import Path

import pandas as pd
import re


# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_DIR / "data" / "processed" / "campaign_summary.csv"


# Campaign naming patterns
CAMPAIGN_PATTERN = re.compile(
    r"^Ecom_FashionCo_"
    r"(?P<theme>Brand Story|Product Launch|Influencer|Promo|Educational|UGC|Retargeting|Seasonal)_"
    r"(?P<objective>Awareness|Consideration|Conversion)_"
    r"(?P<platform>Google Display|Google Search|LinkedIn|TikTok|Meta|Snapchat)_"
    r"(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)_"
    r"(?P<year>20\d{2})$"
)


def load_fashionco_data():

    # Load the CSV
    df = pd.read_csv(DATA_PATH)

    # Keep FashionCo campaigns only
    df = df[df["account"] == "Ecom_FashionCo"].copy()

    # Extract campaign metadata
    extracted = df["campaign_name"].str.extract(CAMPAIGN_PATTERN)

    # Add extracted columns
    df = pd.concat([df, extracted], axis=1)

    return df


def analyze_by_theme(df):

    # Group campaigns by theme and aggregate their metrics
    results = (
        df.groupby("theme")
        .agg(
            campaigns=("campaign_name", "count"),
            total_spend=("spend", "sum"),
            total_conversions=("conversions", "sum"),
            total_revenue=("revenue", "sum")
        )
        .reset_index()
    )

    # Calculate overall ROAS from aggregated values
    results["roas"] = (
        results["total_revenue"] / results["total_spend"]
    ).where(results["total_spend"] != 0)

    # Display themes with the highest ROAS first
    results = results.sort_values(
        by="roas",
        ascending=False
    )

    return results


def analyze_by_platform(df):

    results = (
        df.groupby("platform")
        .agg(
            campaign_groups=("campaign_name", "count"),
            total_spend=("spend", "sum"),
            total_conversions=("conversions", "sum"),
            total_revenue=("revenue", "sum")
        )
        .reset_index()
    )

    results["roas"] = (
        results["total_revenue"] / results["total_spend"]
    ).where(results["total_spend"] != 0)

    results = results.sort_values(
        by="roas",
        ascending=False
    )

    return results


def analyze_platform_by_objective(df):

    results = (
        df.groupby(["platform", "objective"])
        .agg(
            campaign_groups=("campaign_name", "count"),
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            total_conversions=("conversions", "sum")
        )
        .reset_index()
    )

    results["roas"] = (
        results["total_revenue"] / results["total_spend"]
    ).where(
        (results["total_spend"] != 0)
        & (results["objective"] == "Conversion")
    )

    return results.sort_values(
        by=["objective", "roas"],
        ascending=[True, False]
    )


def analyze_monthly_trends(df):

    # Keep Conversion campaigns only
    conversion_df = df[df["objective"] == "Conversion"].copy()

    # Convert campaign dates into monthly periods
    conversion_df["month_date"] = (
        pd.to_datetime(conversion_df["first_date"])
        .dt.to_period("M")
        .astype(str)
    )

    # Aggregate metrics by month
    results = (
        conversion_df.groupby("month_date")
        .agg(
            campaign_groups=("campaign_name", "count"),
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            total_conversions=("conversions", "sum")
        )
        .reset_index()
    )

    # Calculate aggregated monthly ROAS
    results["roas"] = (
        results["total_revenue"] / results["total_spend"]
    ).where(results["total_spend"] != 0)

    return results.sort_values(by="month_date")


def generate_monthly_insights(monthly_analysis):

    valid = monthly_analysis.dropna(subset=["roas"])

    if valid.empty:
        return ["No valid monthly ROAS data available."]

    best_month = valid.loc[valid["roas"].idxmax()]
    worst_month = valid.loc[valid["roas"].idxmin()]

    insights = [
        (
            f"Highest monthly ROAS: {best_month['month_date']} "
            f"({best_month['roas']:.2f})."
        ),
        (
            f"Lowest monthly ROAS: {worst_month['month_date']} "
            f"({worst_month['roas']:.2f})."
        )
    ]

    latest = valid.iloc[-1]

    insights.append(
        f"Latest month analyzed: {latest['month_date']}, "
        f"with ROAS of {latest['roas']:.2f}."
    )

    return insights


def detect_roas_anomalies(monthly_analysis):

    # Keep months with valid ROAS values
    roas_values = monthly_analysis["roas"].dropna()

    if len(roas_values) < 4:
        return monthly_analysis.iloc[0:0]

    # Calculate quartiles and interquartile range
    q1 = roas_values.quantile(0.25)
    q3 = roas_values.quantile(0.75)
    iqr = q3 - q1

    # Define the statistical boundaries
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    # Identify unusually high or low values
    anomalies = monthly_analysis[
        (monthly_analysis["roas"] < lower_bound)
        | (monthly_analysis["roas"] > upper_bound)
    ].copy()

    return anomalies


def analyze_monthly_themes(df, year, month):

    # Filter one month and Conversion campaigns
    filtered = df[
        (df["year"] == str(year))
        & (df["month"] == month)
        & (df["objective"] == "Conversion")
    ].copy()

    # Aggregate performance by theme
    results = (
        filtered.groupby("theme")
        .agg(
            campaign_groups=("campaign_name", "count"),
            total_spend=("spend", "sum"),
            total_revenue=("revenue", "sum"),
            total_conversions=("conversions", "sum")
        )
        .reset_index()
    )

    # Calculate aggregated ROAS
    results["roas"] = (
        results["total_revenue"] / results["total_spend"]
    ).where(results["total_spend"] != 0)

    total_month_revenue = results["total_revenue"].sum()

    results["revenue_share_pct"] = (
        results["total_revenue"] / total_month_revenue * 100
    )

    return results.sort_values(
        by="total_revenue",
        ascending=False
    )


def get_theme_performance_summary(year, month):
    df = load_fashionco_data()

    results = analyze_monthly_themes(
        df,
        year=str(year),
        month=month
    )

    if results.empty:
        return "No campaign data found for this period."

    lines = [
        f"Campaign performance by theme — {month} {year}",
        "All figures are from demo data."
    ]

    for _, row in results.iterrows():
        lines.append(
            f"{row['theme']}: "
            f"ROAS {row['roas']:.2f}, "
            f"Revenue {row['total_revenue']:,.2f}, "
            f"Revenue share {row['revenue_share_pct']:.1f}%."
        )

    return "\n".join(lines)



