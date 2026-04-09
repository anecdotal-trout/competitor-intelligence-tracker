"""
Competitor Intelligence Tracker
================================
Tracks competitor pricing changes, feature launches, and positioning over time.
Designed for growth and strategy teams that need to:
- Monitor pricing moves across the competitive landscape
- Track feature parity and gaps
- Spot trends in competitor go-to-market strategy
- Brief leadership on competitive dynamics

Works with periodic manual snapshots — in practice you'd automate data
collection with a scraper, but the analysis logic is the same.
"""

import sqlite3
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_data():
    """Load pricing snapshots and changelog into SQLite."""
    pricing = pd.read_csv(os.path.join(DATA_DIR, "pricing_snapshots.csv"))
    changelog = pd.read_csv(os.path.join(DATA_DIR, "changelog.csv"), parse_dates=["date"])

    conn = sqlite3.connect(":memory:")
    pricing.to_sql("pricing", conn, if_exists="replace", index=False)
    changelog.to_sql("changelog", conn, if_exists="replace", index=False)

    return conn, pricing, changelog


# ---------------------------------------------------------------------------
# SQL QUERIES
# ---------------------------------------------------------------------------

PRICE_CHANGES_SQL = """
    SELECT
        p1.competitor,
        p1.product_tier,
        p1.monthly_price_usd AS price_jan,
        p2.monthly_price_usd AS price_mar,
        p3.monthly_price_usd AS price_jun,
        CASE
            WHEN p1.monthly_price_usd > 0
            THEN ROUND((p3.monthly_price_usd - p1.monthly_price_usd) * 100.0
                        / p1.monthly_price_usd, 1)
            ELSE NULL
        END AS pct_change_jan_to_jun
    FROM pricing p1
    JOIN pricing p2
        ON p1.competitor = p2.competitor
        AND p1.product_tier = p2.product_tier
        AND p2.snapshot_date = '2025-03-15'
    JOIN pricing p3
        ON p1.competitor = p3.competitor
        AND p1.product_tier = p3.product_tier
        AND p3.snapshot_date = '2025-06-15'
    WHERE p1.snapshot_date = '2025-01-15'
    ORDER BY p1.competitor, p1.monthly_price_usd
"""

CHANGELOG_SUMMARY_SQL = """
    SELECT
        competitor,
        change_type,
        COUNT(*) AS count,
        SUM(CASE WHEN impact_level = 'high' THEN 1 ELSE 0 END) AS high_impact
    FROM changelog
    GROUP BY competitor, change_type
    ORDER BY competitor, count DESC
"""

MONTHLY_ACTIVITY_SQL = """
    SELECT
        strftime('%Y-%m', date) AS month,
        competitor,
        COUNT(*) AS changes,
        GROUP_CONCAT(change_type, ', ') AS types
    FROM changelog
    GROUP BY month, competitor
    ORDER BY month, competitor
"""

FEATURE_TIMELINE_SQL = """
    SELECT
        date,
        competitor,
        description,
        impact_level
    FROM changelog
    WHERE change_type = 'feature_launch'
    ORDER BY date
"""


# ---------------------------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------------------------

def analyze_feature_parity(pricing_df):
    """Compare features across competitors at latest snapshot."""
    latest = pricing_df[pricing_df["snapshot_date"] == "2025-06-15"].copy()

    results = []
    for _, row in latest.iterrows():
        features = [f.strip() for f in row["key_features"].split(",")]
        results.append({
            "competitor": row["competitor"],
            "tier": row["product_tier"],
            "price": row["monthly_price_usd"],
            "units": f"{row['included_units']} {row['unit_type']}",
            "num_features": len(features),
            "has_voice_cloning": any("voice cloning" in f.lower() for f in features),
            "has_api": any("api" in f.lower() for f in features),
            "has_analytics": any("analytics" in f.lower() or "dashboard" in f.lower() for f in features),
            "enterprise_ready": row["enterprise_available"] == "yes",
        })

    return pd.DataFrame(results)


def pricing_trend_analysis(conn):
    """Identify the direction of pricing across the market."""
    df = pd.read_sql(PRICE_CHANGES_SQL, conn)

    increases = df[df["pct_change_jan_to_jun"].notna() & (df["pct_change_jan_to_jun"] > 0)]
    decreases = df[df["pct_change_jan_to_jun"].notna() & (df["pct_change_jan_to_jun"] < 0)]
    flat = df[df["pct_change_jan_to_jun"].notna() & (df["pct_change_jan_to_jun"] == 0)]

    return {
        "price_increases": len(increases),
        "price_decreases": len(decreases),
        "unchanged": len(flat),
        "avg_increase_pct": increases["pct_change_jan_to_jun"].mean() if not increases.empty else 0,
        "market_direction": "prices rising" if len(increases) > len(decreases) else "prices falling",
    }


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def main():
    conn, pricing_df, changelog_df = load_data()

    print("\n" + "="*80)
    print("  COMPETITOR INTELLIGENCE REPORT")
    print("  AI Voice Market — H1 2025")
    print("="*80)

    # --- Pricing Changes Over Time ---
    print_section("PRICING CHANGES (Jan → Mar → Jun 2025)")
    price_df = pd.read_sql(PRICE_CHANGES_SQL, conn)
    print(price_df.to_string(index=False))

    # --- Pricing Trend ---
    print_section("MARKET PRICING TREND")
    trend = pricing_trend_analysis(conn)
    print(f"  Price increases: {trend['price_increases']}")
    print(f"  Price decreases: {trend['price_decreases']}")
    print(f"  Unchanged:       {trend['unchanged']}")
    print(f"  Avg increase:    {trend['avg_increase_pct']:.1f}%")
    print(f"  Direction:       {trend['market_direction']}")

    # --- Feature Parity ---
    print_section("FEATURE COMPARISON (latest snapshot)")
    parity_df = analyze_feature_parity(pricing_df)
    print(parity_df.to_string(index=False))

    # --- Changelog Summary ---
    print_section("COMPETITIVE ACTIVITY BY TYPE")
    activity_df = pd.read_sql(CHANGELOG_SUMMARY_SQL, conn)
    print(activity_df.to_string(index=False))

    # --- Monthly Activity ---
    print_section("MONTHLY COMPETITIVE ACTIVITY")
    monthly_df = pd.read_sql(MONTHLY_ACTIVITY_SQL, conn)
    print(monthly_df.to_string(index=False))

    # --- Feature Launch Timeline ---
    print_section("FEATURE LAUNCH TIMELINE")
    features_df = pd.read_sql(FEATURE_TIMELINE_SQL, conn)
    for _, row in features_df.iterrows():
        impact = "🔴" if row["impact_level"] == "high" else "🟡" if row["impact_level"] == "medium" else "⚪"
        print(f"  {impact}  {row['date'][:10]}  {row['competitor']:15s}  {row['description']}")

    # --- Strategic Insights ---
    print_section("STRATEGIC INSIGHTS")
    insights = [
        "1. PRICES ARE RISING — All three competitors raised paid tier prices in H1.",
        "   This suggests the market is moving past land-grab pricing into monetisation.",
        "   Opportunity: competitive pricing on mid-tier could capture switchers.",
        "",
        "2. VOICE CLONING IS TABLE STAKES — All competitors now offer it in paid tiers.",
        "   Feature differentiation needs to come from quality, not availability.",
        "",
        "3. COMPETITOR A IS MOST AGGRESSIVE — 8 changes in H1 including pricing, features,",
        "   and partnerships. They appear to be pursuing an enterprise strategy (SSO, Salesforce).",
        "",
        "4. API ACCESS EXPANDING DOWN-MARKET — Previously enterprise-only, now available",
        "   in mid-tier plans. Signals growing developer/builder audience segment.",
        "",
        "5. ENTERPRISE COMPLIANCE EMERGING — SOC2, SSO, on-prem options appearing.",
        "   Enterprise buyers are entering the market.",
    ]
    for line in insights:
        print(f"  {line}")

    conn.close()
    print(f"\n{'='*80}")
    print("  Report complete.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
