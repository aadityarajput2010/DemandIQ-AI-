
from pathlib import Path

import pandas as pd
import streamlit as st
import mysql.connector


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="DemandIQ AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM DESIGN
# ==========================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 16px;
        border-radius: 12px;
    }

    h1, h2, h3 {
        font-weight: 650;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# HEADER
# ==========================================

st.title("📦 DemandIQ AI")

st.caption(
    "AI-Powered Sales Forecasting & Inventory Optimization"
)

st.write(
    "A centralized platform to monitor product demand, "
    "forecast future sales, analyze inventory health, "
    "and generate replenishment recommendations "
    "across multiple stores."
)

st.divider()


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("📦 DemandIQ AI")
st.sidebar.caption("Multi-Store Analytics")

selected_page = st.sidebar.radio(
    "Go to",
    [
        "Executive Dashboard",
        "Store Analytics",
        "Inventory Analytics",
        "Forecast Analysis",
        "Model Performance"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Database Connection")

mysql_password = st.sidebar.text_input(
    "MySQL Root Password",
    type="password"
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

if not mysql_password:

    st.info(
        "Enter your MySQL password in the sidebar "
        "to access the DemandIQ dashboard."
    )

    st.stop()


connection = None

try:

    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=mysql_password,
        database="demandiq"
    )

    st.sidebar.success("MySQL Connected")

    # ==========================================
    # LOAD MULTI-STORE INVENTORY
    # ==========================================

    inventory_query = """
        SELECT
            item_id,
            store_id,
            average_historical_demand,
            demand_std,
            average_forecast_demand,
            total_forecast_demand,
            safety_stock,
            lead_time_demand,
            reorder_point,
            current_stock,
            stock_on_order,
            reserved_stock,
            net_stock_position,
            target_stock,
            status,
            recommended_order_qty
        FROM multi_store_inventory_recommendations
    """

    multi_inventory = pd.read_sql(
        inventory_query,
        connection
    )

    # ==========================================
    # LOAD MULTI-STORE FORECASTS
    # ==========================================

    forecast_query = """
        SELECT
            item_id,
            store_id,
            day_number,
            predicted_sales AS forecast_sales
        FROM multi_store_sales_forecasts
    """

    forecast_data = pd.read_sql(
        forecast_query,
        connection
    )

    if multi_inventory.empty:

        st.warning(
            "No multi-store inventory records found."
        )

        st.stop()

    # ==========================================
    # PREPARE DATA
    # ==========================================

    forecast_summary = (
        forecast_data.groupby(
            ["item_id", "store_id"]
        )["forecast_sales"]
        .sum()
        .reset_index(name="forecast_28_day_demand")
    )

    multi_inventory = multi_inventory.merge(
        forecast_summary,
        on=["item_id", "store_id"],
        how="left"
    )

    multi_inventory["forecast_28_day_demand"] = (
        multi_inventory["forecast_28_day_demand"].fillna(0)
    )

    st.sidebar.success("Multi-Store Data Loaded")

    # ==========================================
    # STORE FILTER
    # ==========================================

    available_stores = sorted(
        multi_inventory["store_id"].unique().tolist()
    )

    selected_store = st.sidebar.selectbox(
        "Select Store",
        ["All Stores"] + available_stores
    )

    if selected_store == "All Stores":

        filtered_inventory = multi_inventory.copy()
        filtered_forecast = forecast_data.copy()

    else:

        filtered_inventory = multi_inventory[
            multi_inventory["store_id"] == selected_store
        ].copy()

        filtered_forecast = forecast_data[
            forecast_data["store_id"] == selected_store
        ].copy()

    # ==========================================
    # COMMON CALCULATIONS
    # ==========================================

    total_combinations = len(filtered_inventory)

    total_products = filtered_inventory["item_id"].nunique()

    total_forecast_demand = (
        filtered_inventory["forecast_28_day_demand"].sum()
    )

    products_requiring_reorder = (
        filtered_inventory["status"]
        .eq("REORDER REQUIRED")
        .sum()
    )

    total_recommended_order = (
        filtered_inventory["recommended_order_qty"].sum()
    )

    # ==========================================
    # PAGE 1: EXECUTIVE DASHBOARD
    # ==========================================

    if selected_page == "Executive Dashboard":

        st.header("📊 Executive Dashboard")

        st.write(
            "Monitor overall demand forecasting "
            "and inventory performance."
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Products Monitored",
            f"{total_products:,}"
        )

        col2.metric(
            "Stores Monitored",
            filtered_inventory["store_id"].nunique()
        )

        col3.metric(
            "28-Day Forecast Demand",
            f"{total_forecast_demand:,.2f}"
        )

        col4.metric(
            "Reorder Required",
            f"{products_requiring_reorder:,}"
        )

        st.divider()

        st.subheader("Inventory Health Overview")

        status_counts = (
            filtered_inventory["status"]
            .value_counts()
            .reindex(
                ["STOCK SUFFICIENT", "REORDER REQUIRED"],
                fill_value=0
            )
            .reset_index()
        )

        status_counts.columns = [
            "Inventory Status",
            "Number of Combinations"
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.bar_chart(
                status_counts,
                x="Inventory Status",
                y="Number of Combinations"
            )

        with col2:

            st.dataframe(
                status_counts,
                hide_index=True,
                width="stretch"
            )

        st.divider()

        st.subheader("Store-Wise Forecast Demand")

        store_demand = (
            filtered_inventory.groupby("store_id")
            ["forecast_28_day_demand"]
            .sum()
            .reset_index()
        )

        st.bar_chart(
            store_demand,
            x="store_id",
            y="forecast_28_day_demand"
        )

        st.divider()

        st.subheader("Products Requiring Replenishment")

        reorder_table = filtered_inventory[
            filtered_inventory["status"] == "REORDER REQUIRED"
        ][
            [
                "item_id",
                "store_id",
                "reorder_point",
                "net_stock_position",
                "recommended_order_qty"
            ]
        ]

        if not reorder_table.empty:

            st.dataframe(
                reorder_table,
                hide_index=True,
                width="stretch"
            )

        else:

            st.success(
                "No products currently require replenishment."
            )

    # ==========================================
    # PAGE 2: STORE ANALYTICS
    # ==========================================

    elif selected_page == "Store Analytics":

        st.header("🏬 Store-Wise Analytics")

        st.write(
            "Compare demand forecasts and inventory "
            "performance across different stores."
        )

        store_summary = (
            multi_inventory.groupby("store_id")
            .agg(
                total_products=("item_id", "nunique"),
                forecast_demand=(
                    "forecast_28_day_demand", "sum"
                ),
                reorder_count=(
                    "status",
                    lambda x: (x == "REORDER REQUIRED").sum()
                ),
                recommended_order=(
                    "recommended_order_qty", "sum"
                )
            )
            .reset_index()
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Forecast Demand by Store")

            st.bar_chart(
                store_summary,
                x="store_id",
                y="forecast_demand"
            )

        with col2:

            st.subheader("Recommended Order by Store")

            st.bar_chart(
                store_summary,
                x="store_id",
                y="recommended_order"
            )

        st.divider()

        st.subheader("Reorder Requirements by Store")

        st.bar_chart(
            store_summary,
            x="store_id",
            y="reorder_count"
        )

        st.divider()

        st.subheader("Complete Store Performance")

        st.dataframe(
            store_summary,
            hide_index=True,
            width="stretch"
        )

    # ==========================================
    # PAGE 3: INVENTORY ANALYTICS
    # ==========================================

    elif selected_page == "Inventory Analytics":

        st.header("📈 Inventory Analytics")

        st.write(
            "Analyze demand, stock availability "
            "and replenishment recommendations."
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Product-Store Combinations",
            f"{total_combinations:,}"
        )

        col2.metric(
            "Recommended Order Quantity",
            f"{total_recommended_order:,.0f}"
        )

        col3.metric(
            "Reorder Required",
            f"{products_requiring_reorder:,}"
        )

        st.divider()

        col1, col2 = st.columns(2)

        top_products = (
            filtered_inventory.sort_values(
                "forecast_28_day_demand",
                ascending=False
            )
            .head(10)
            [["item_id", "forecast_28_day_demand"]]
            .set_index("item_id")
        )

        reorder_products = (
            filtered_inventory[
                filtered_inventory["recommended_order_qty"] > 0
            ]
            .sort_values(
                "recommended_order_qty",
                ascending=False
            )
            [["item_id", "recommended_order_qty"]]
            .set_index("item_id")
        )

        with col1:

            st.subheader("Top Products by Forecast Demand")

            st.bar_chart(
                top_products,
                horizontal=True
            )

        with col2:

            st.subheader("Recommended Order Quantities")

            st.bar_chart(
                reorder_products,
                horizontal=True
            )

        st.divider()

        st.subheader("Historical vs Forecast Daily Demand")

        demand_comparison = filtered_inventory[
            [
                "item_id",
                "average_historical_demand",
                "average_forecast_demand"
            ]
        ].copy()

        demand_comparison = demand_comparison.set_index("item_id")

        st.bar_chart(demand_comparison)

        st.divider()

        st.subheader("Complete Inventory Recommendations")

        st.dataframe(
            filtered_inventory,
            hide_index=True,
            width="stretch"
        )

    # ==========================================
    # PAGE 4: FORECAST ANALYSIS
    # ==========================================

    elif selected_page == "Forecast Analysis":

        st.header("🔮 Sales Forecast Analysis")

        st.write(
            "Explore the 28-day predicted demand "
            "for each product and store."
        )

        if filtered_forecast.empty:

            st.warning("No forecast records available.")

        else:

            available_products = sorted(
                filtered_forecast["item_id"].unique().tolist()
            )

            selected_product = st.selectbox(
                "Select Product",
                available_products
            )

            available_product_stores = sorted(
                filtered_forecast.loc[
                    filtered_forecast["item_id"] == selected_product,
                    "store_id"
                ].unique().tolist()
            )

            selected_product_store = st.selectbox(
                "Select Product Store",
                available_product_stores
            )

            selected_forecast = filtered_forecast[
                (filtered_forecast["item_id"] == selected_product)
                & (
                    filtered_forecast["store_id"]
                    == selected_product_store
                )
            ].sort_values("day_number")

            product_info = filtered_inventory[
                (filtered_inventory["item_id"] == selected_product)
                & (
                    filtered_inventory["store_id"]
                    == selected_product_store
                )
            ]

            if not selected_forecast.empty:

                forecast_total = selected_forecast[
                    "forecast_sales"
                ].sum()

                forecast_average = selected_forecast[
                    "forecast_sales"
                ].mean()

                col1, col2 = st.columns(2)

                col1.metric(
                    "28-Day Forecast Demand",
                    f"{forecast_total:.2f} units"
                )

                col2.metric(
                    "Average Daily Forecast",
                    f"{forecast_average:.2f} units"
                )

                st.divider()

                st.subheader("28-Day Forecast Trend")

                chart_data = selected_forecast[
                    ["day_number", "forecast_sales"]
                ].set_index("day_number")

                st.line_chart(chart_data)

                st.subheader("Forecast Records")

                st.dataframe(
                    selected_forecast,
                    hide_index=True,
                    width="stretch"
                )

                if not product_info.empty:

                    info = product_info.iloc[0]

                    st.divider()

                    st.subheader("Inventory Context")

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Reorder Point",
                        f"{info['reorder_point']:.2f}"
                    )

                    col2.metric(
                        "Net Stock Position",
                        f"{info['net_stock_position']:.2f}"
                    )

                    col3.metric(
                        "Recommended Order",
                        f"{info['recommended_order_qty']:.0f}"
                    )

    # ==========================================
    # PAGE 5: MODEL PERFORMANCE
    # ==========================================

    elif selected_page == "Model Performance":

        st.header("🤖 Model Performance Evaluation")

        st.write(
            "Evaluate the multi-store Random Forest "
            "sales forecasting model."
        )

        REPORT_FILE = (
            PROJECT_DIR
            / "reports"
            / "multi_store_model_metrics.csv"
        )

        if REPORT_FILE.exists():

            model_metrics = pd.read_csv(REPORT_FILE)

            if {"metric", "value"}.issubset(model_metrics.columns):

                metrics = dict(
                    zip(
                        model_metrics["metric"],
                        model_metrics["value"]
                    )
                )

                col1, col2, col3 = st.columns(3)

                if "MAE" in metrics:
                    col1.metric(
                        "Mean Absolute Error",
                        f"{float(metrics['MAE']):.3f}"
                    )

                if "RMSE" in metrics:
                    col2.metric(
                        "Root Mean Squared Error",
                        f"{float(metrics['RMSE']):.3f}"
                    )

                if "R2 Score" in metrics:
                    col3.metric(
                        "R² Score",
                        f"{float(metrics['R2 Score']):.3f}"
                    )

            st.divider()

            st.subheader("Complete Evaluation Metrics")

            st.dataframe(
                model_metrics,
                hide_index=True,
                width="stretch"
            )

            with st.expander("Understanding Model Metrics"):

                st.write(
                    "**MAE:** Average absolute difference "
                    "between actual and predicted sales. Lower is better."
                )

                st.write(
                    "**RMSE:** Penalizes larger prediction errors "
                    "more heavily. Lower is better."
                )

                st.write(
                    "**R² Score:** Indicates how much variation "
                    "in sales is explained by the model."
                )

        else:

            st.warning(
                "Multi-store model evaluation report not found."
            )


except mysql.connector.Error as error:

    st.error(
        f"MySQL connection failed: {error}"
    )

except Exception as error:

    st.error(
        f"Dashboard error: {error}"
    )

finally:

    if connection is not None and connection.is_connected():

        connection.close()
