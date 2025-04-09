from preswald import connect, get_df, text, table, plotly, sidebar,slider
import pandas as pd
import plotly.express as px

connect()
df = get_df("avocado")

if df is None:
    text("❌ Failed to load avocado dataset.")
else:
    sidebar()
    text("# 🥑 Avocado Market Dashboard")

    # Format date
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date_str"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Summary by type
    summary = df.groupby("type").agg({
        "Total Volume": "mean",
        "AveragePrice": "mean"
    }).reset_index()
    summary.columns = ["Type", "Avg Volume", "Avg Price"]

    text("""
    🥑 Summary Insights: Avocado Types
     💡 Key Observations

    - Organic avocados are consistently more expensive than their conventional counterparts.
        - Average Price (Organic): ~$1.65
        - Average Price (Conventional): ~$1.15

    - Conventional avocados dominate the market in terms of total volume.
        - They account for over 97% of total avocado volume sold.
        - This suggests that while organic avocados command higher prices, their market share remains niche.

     📦 Market Dynamics

    This divergence in volume vs. price reflects an interesting market pattern:
    - Consumers are willing to pay more for organic avocados, but
    - The majority of buyers opt for conventional due to availability and affordability.

     📈 Business Implication

    If you're a retailer:
    - Consider stocking a smaller, curated selection of organic avocados for premium customers.
    - But keep a robust supply of conventional avocados to satisfy mass demand.
    """)

    table(summary, limit=2)

    text("""
    📈 National Avocado Price Trends

    The chart below shows how average avocado prices evolved between 2015 and early 2018, for:

    - 🟦 Conventional avocados
    - 🟥 Organic avocados

    Key insights:
    • Organic avocados consistently remained more expensive due to higher production costs and niche demand.
    • There was a noticeable price spike in mid-2017, likely due to seasonal or supply chain disruptions.
    • Toward late 2017, the price gap between organic and conventional avocados narrowed.
    • Both types of avocados generally show an upward trend, possibly driven by rising popularity and inflation.

    These insights set the stage for deeper analysis, including seasonality, regional differences, and forecasting future price movements.
    """)

    price_by_date = df.groupby(["Date", "type"])["AveragePrice"].mean().reset_index()
    price_by_date["Date_str"] = price_by_date["Date"].dt.strftime("%Y-%m-%d")

    # Line chart - Clean average price trends
    text(" 📈 Average Price Over Time by Type")
    price_fig = px.line(price_by_date, x="Date_str", y="AveragePrice", color="type",
                        title="National Average Avocado Price Over Time",
                        line_shape="spline",
                        render_mode="svg")
    plotly(price_fig)

    text("""
    🧺 Avocado Volume Trends Over Time

    This chart visualizes the monthly total volume of avocados sold from 2015 to early 2018, segmented by type:

    - 🟦 Conventional avocados dominate the market in volume, with massive monthly sales consistently over time.
    - 🟥 Organic avocados, while growing steadily, make up a small fraction of total sales — highlighting their niche market.

    Notable observations:
    • Volume peaks are seasonal — with surges seen around early and mid-year, possibly tied to harvest cycles or demand events.
    • Despite price volatility, volume trends remain relatively stable for conventional avocados.
    • Organic avocado volume, while lower, shows a gradual upward trend, hinting at growing consumer preference.

    These volume trends are essential for interpreting price dynamics and supply-demand relationships.
    """)

    # Volume bar chart over time (monthly)
    df_monthly = df.copy()
    df_monthly["month"] = df_monthly["Date"].dt.to_period("M").dt.to_timestamp()
    df_monthly["month_str"] = df_monthly["month"].dt.strftime("%Y-%m")
    volume_df = df_monthly.groupby(["month_str", "type"]).agg({"Total Volume": "sum"}).reset_index()

    text(" 🧺 Total Volume Sold Over Time")
    volume_fig = px.bar(volume_df, x="month_str", y="Total Volume", color="type",
                        title="Monthly Total Volume of Avocados Sold",
                        barmode="group")
    plotly(volume_fig)

    # Price vs Volume Scatter per Region

    text("""
    📍 Regional Price vs Volume Insights

    This scatter plot shows how avocado prices and total volumes vary across U.S. regions (most recent date in the dataset):

    • Regions with higher volumes (e.g., DallasFtWorth, California) tend to exhibit lower average prices, suggesting economies of scale and supply-chain efficiency.

    • Smaller markets (lower volume) often show higher price points, possibly due to transportation costs, limited supply, or boutique market demand.

    • Circle size reflects average price — larger circles = higher prices. Notice how many high-price regions also sell fewer avocados.

    Overall, this chart highlights regional disparities in avocado economics — useful for retailers, suppliers, and market analysts exploring localized strategies.
    """)
    recent = df[df["Date"] == df["Date"].max()]
    scatter_fig = px.scatter(recent, x="Total Volume", y="AveragePrice", color="region",
                             size="AveragePrice", title="Price vs Volume by Region",
                             hover_name="region")
    plotly(scatter_fig)

    # Moving average trend (basic smoothing)
    text("""
    🧮 Smoothed Avocado Price Trends

    The 7-day moving average chart helps smooth out daily volatility, revealing clearer trends in avocado pricing by type:

    • Organic avocados consistently show higher prices, aligning with their premium positioning and niche demand.

    • A distinct seasonal rise in prices occurs mid-2017 for both types, with a sharp peak for conventional avocados — possibly due to supply constraints or seasonal buying patterns.

    • Post-2017, both curves decline slightly, though organic remains elevated — suggesting strong long-term consumer preference.

    This smoothed view is crucial for identifying trend inflections and informing strategic buying or pricing decisions.
    """)

    df_sorted = df.sort_values("Date")
    df_sorted["MA7"] = df_sorted.groupby("type")["AveragePrice"].transform(lambda x: x.rolling(7).mean())
    df_sorted["Date_str"] = df_sorted["Date"].dt.strftime("%Y-%m-%d")

    ma_fig = px.line(df_sorted, x="Date_str", y="MA7", color="type",
                     title="7-Day Moving Average of Avocado Prices")
    plotly(ma_fig)

    # Slider for interactive date filter (single year)
    text("""
    🧭 Yearly Avocado Price Journey

    Use the slider above to explore avocado price trends for any specific year in the dataset.

    In the example shown for 2017:

    • Organic avocados maintained a higher price point throughout the year, peaking around August–September.

    • Conventional avocados exhibited a notable price climb during the first half of the year, with a mid-year high followed by a gentle decline.

    • This pattern suggests seasonal influences or shifts in supply chains, with prices adjusting to market forces across both avocado types.

    This interactive tool helps identify yearly patterns, anomalies, or potential seasonal pricing cycles.
    """)
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    selected_year = slider("Select Year", min_date.year, max_date.year, 1)

    filtered = df[df["Date"].dt.year == selected_year]
    filtered_summary = filtered.groupby(["Date", "type"])["AveragePrice"].mean().reset_index()
    filtered_summary["Date_str"] = filtered_summary["Date"].dt.strftime("%Y-%m-%d")

    interactive_fig = px.line(filtered_summary, x="Date_str", y="AveragePrice", color="type",
                              title=f"Avocado Prices in {selected_year}")
    plotly(interactive_fig)

