import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Streamlit UI
st.title("📊 Order Analysis Dashboard")
st.sidebar.header("🔍 Data Upload & Filters")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV file
    try:
        df = pd.read_csv(uploaded_file)
        
        # Date range filter
        st.sidebar.subheader("Date Range Filter")
        min_date = pd.to_datetime(df['Picked on']).min().date()
        max_date = pd.to_datetime(df['Picked on']).max().date()
        
        start_date = st.sidebar.date_input(
            "Start date",
            min_date,
            min_value=min_date,
            max_value=max_date
        )
        
        end_date = st.sidebar.date_input(
            "End date",
            max_date,
            min_value=min_date,
            max_value=max_date
        )
        
        # Convert dates to datetime for comparison
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Convert date columns to datetime
        date_columns = ["Picked on", "First attempted on", "Delivered on", "Latest Out-For-Delivery on", "Last attempted on"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Filter data based on date range
        df_filtered = df[(df['Picked on'].dt.date >= start_date.date()) & 
                         (df['Picked on'].dt.date <= end_date.date())].copy()
        
        if df_filtered.empty:
            st.warning("No data available for the selected date range.")
        else:
            # Customers with "Next Day" criteria
            next_day_customers = ["The Whole Truth Foods", "ZISHTA TRADITIONS PRIVATE LIMITED", "Assembly Curefit"]

            # Determine Same Day / Next Day Orders
            df_filtered.loc[:, "Next Day"] = (
                df_filtered["Customer"].isin(next_day_customers) | 
                (df_filtered["Picked on"].dt.hour >= 15)
            )
            
            # Count Total Orders
            total_orders = df_filtered["Order Number"].nunique()
            
            # Count Same Day and Next Day Orders
            next_day_orders = df_filtered["Next Day"].sum()
            same_day_orders = total_orders - next_day_orders
            
            # Calculate Percentages
            same_day_pct = (same_day_orders / total_orders) * 100 if total_orders > 0 else 0
            next_day_pct = (next_day_orders / total_orders) * 100 if total_orders > 0 else 0
            
            # Display Metrics
            st.subheader("📋 Order Summary")
            summary_data = pd.DataFrame({
                "Metric": ["Total Orders", "Same Day Orders", "Next Day Orders", 
                           "Same Day %", "Next Day %"],
                "Value": [total_orders, same_day_orders, next_day_orders, 
                          f"{same_day_pct:.2f}%", f"{next_day_pct:.2f}%"]
            })
            st.table(summary_data)
            
            # Delivery Performance Analysis
            st.subheader("🚚 Delivery Performance")
            
            # Same Day Attempted Orders
            same_day_attempted = df_filtered[
                (df_filtered["Next Day"] == False) & 
                (df_filtered["Picked on"].dt.date == df_filtered["First attempted on"].dt.date) & 
                df_filtered["First attempted on"].notna()
            ]["Order Number"].nunique()
            
            # Same Day Delivered Orders
            same_day_delivered = df_filtered[
                (df_filtered["Next Day"] == False) & 
                (df_filtered["Picked on"].dt.date == df_filtered["Delivered on"].dt.date) & 
                df_filtered["Delivered on"].notna()
            ]["Order Number"].nunique()
            
            # Next Day Orders (picked previous day after 3 PM)
            previous_day_start = start_date - pd.Timedelta(days=1)
            next_day_orders_filtered = df[
                (df["Picked on"].dt.date >= previous_day_start.date()) & 
                (df["Picked on"].dt.date <= (end_date - pd.Timedelta(days=1)).date()) & 
                (df["Picked on"].dt.hour >= 15)
            ]
            
            # Count Next Day Orders
            next_day_orders = next_day_orders_filtered["Order Number"].nunique()
            
            # Next Day Attempted Orders
            next_day_attempted = next_day_orders_filtered[
                (next_day_orders_filtered["First attempted on"].dt.date >= start_date.date()) & 
                (next_day_orders_filtered["First attempted on"].dt.date <= end_date.date())
            ]["Order Number"].nunique()
            
            # Next Day Delivered Orders
            next_day_delivered = next_day_orders_filtered[
                (next_day_orders_filtered["Delivered on"].dt.date >= start_date.date()) & 
                (next_day_orders_filtered["Delivered on"].dt.date <= end_date.date())
            ]["Order Number"].nunique()
            
            # Un-attempted Orders
            same_day_unattempted = same_day_orders - same_day_attempted
            next_day_unattempted = next_day_orders - next_day_attempted
            
            # Percentage Calculations
            same_day_attempted_pct = (same_day_attempted / same_day_orders) * 100 if same_day_orders > 0 else 0
            next_day_attempted_pct = (next_day_attempted / next_day_orders) * 100 if next_day_orders > 0 else 0
            
            same_day_delivered_pct = (same_day_delivered / same_day_orders) * 100 if same_day_orders > 0 else 0
            next_day_delivered_pct = (next_day_delivered / next_day_orders) * 100 if next_day_orders > 0 else 0
            
            same_day_unattempted_pct = (same_day_unattempted / same_day_orders) * 100 if same_day_orders > 0 else 0
            next_day_unattempted_pct = (next_day_unattempted / next_day_orders) * 100 if next_day_orders > 0 else 0
            
            # Total Row Calculation
            total_attempted = same_day_attempted + next_day_attempted
            total_delivered = same_day_delivered + next_day_delivered
            total_unattempted = same_day_unattempted + next_day_unattempted
            total_orders_count = same_day_orders + next_day_orders
            
            total_attempted_pct = (total_attempted / total_orders_count) * 100 if total_orders_count > 0 else 0
            total_delivered_pct = (total_delivered / total_orders_count) * 100 if total_orders_count > 0 else 0
            total_unattempted_pct = (total_unattempted / total_orders_count) * 100 if total_orders_count > 0 else 0
            
            # Create Final Table
            delivery_summary = pd.DataFrame({
                "Delivery Frequency": ["Same Day", "Next Day", "Total"],
                "Number of Orders": [same_day_orders, next_day_orders, total_orders_count],
                "Attempted": [same_day_attempted, next_day_attempted, total_attempted],
                "Delivered": [same_day_delivered, next_day_delivered, total_delivered],
                "Un-attempted": [same_day_unattempted, next_day_unattempted, total_unattempted],
                "Attempted %": [f"{same_day_attempted_pct:.1f}%", f"{next_day_attempted_pct:.1f}%", f"{total_attempted_pct:.1f}%"],
                "Delivered %": [f"{same_day_delivered_pct:.1f}%", f"{next_day_delivered_pct:.1f}%", f"{total_delivered_pct:.1f}%"],
                "Un-Attempted %": [f"{same_day_unattempted_pct:.1f}%", f"{next_day_unattempted_pct:.1f}%", f"{total_unattempted_pct:.1f}%"]
            })
            
            st.table(delivery_summary)
            
            # Hub Wise Analysis
            st.subheader("🏢 Hub Wise Performance")
            
            hubs = [
                "Banashankari [ BH Micro warehouse ]",
                "Hebbal [ BH Micro warehouse ]",
                "Mahadevapura [ BH Micro warehouse ]",
                "Koramangala NGV [ BH Micro warehouse ]",
                "Chandra Layout [ BH Micro warehouse ]",
                "Kudlu [ BH Micro warehouse ]"
            ]
            
            if "Delivery Hub" in df_filtered.columns:
                # Same Day Hub Performance
                hub_wise_same_day = []
                
                for hub in hubs:
                    hub_data = df_filtered[(df_filtered["Delivery Hub"] == hub) & (df_filtered["Next Day"] == False)]
                    same_day_orders = hub_data["Order Number"].nunique()
                    
                    same_day_attempted = hub_data[
                        (hub_data["First attempted on"].dt.date == hub_data["Picked on"].dt.date) & 
                        hub_data["First attempted on"].notna()
                    ]["Order Number"].nunique()
                    
                    same_day_delivered = hub_data[
                        (hub_data["Delivered on"].dt.date == hub_data["Picked on"].dt.date) & 
                        hub_data["Delivered on"].notna()
                    ]["Order Number"].nunique()
                    
                    attempted_pct = (same_day_attempted / same_day_orders) * 100 if same_day_orders > 0 else 0
                    delivered_pct = (same_day_delivered / same_day_orders) * 100 if same_day_orders > 0 else 0
                    
                    hub_wise_same_day.append({
                        "Hub Name": hub,
                        "Same Day Orders": same_day_orders,
                        "Attempted": same_day_attempted,
                        "Delivered": same_day_delivered,
                        "Attempted %": f"{attempted_pct:.1f}%",
                        "Delivered %": f"{delivered_pct:.1f}%"
                    })
                
                hub_wise_same_day_df = pd.DataFrame(hub_wise_same_day)
                
                # Next Day Hub Performance
                hub_wise_next_day = []
                
                for hub in hubs:
                    hub_data = next_day_orders_filtered[next_day_orders_filtered["Delivery Hub"] == hub]
                    next_day_orders_count = hub_data["Order Number"].nunique()
                    
                    next_day_attempted = hub_data[
                        (hub_data["First attempted on"].dt.date >= start_date.date()) & 
                        (hub_data["First attempted on"].dt.date <= end_date.date())
                    ]["Order Number"].nunique()
                    
                    next_day_delivered = hub_data[
                        (hub_data["Delivered on"].dt.date >= start_date.date()) & 
                        (hub_data["Delivered on"].dt.date <= end_date.date())
                    ]["Order Number"].nunique()
                    
                    attempted_pct = (next_day_attempted / next_day_orders_count) * 100 if next_day_orders_count > 0 else 0
                    delivered_pct = (next_day_delivered / next_day_orders_count) * 100 if next_day_orders_count > 0 else 0
                    
                    hub_wise_next_day.append({
                        "Hub Name": hub,
                        "Next Day Orders": next_day_orders_count,
                        "Attempted": next_day_attempted,
                        "Delivered": next_day_delivered,
                        "Attempted %": f"{attempted_pct:.1f}%",
                        "Delivered %": f"{delivered_pct:.1f}%"
                    })
                
                hub_wise_next_day_df = pd.DataFrame(hub_wise_next_day)
                
                # Display Hub Performance
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Same Day Performance**")
                    st.dataframe(hub_wise_same_day_df)
                
                with col2:
                    st.markdown("**Next Day Performance**")
                    st.dataframe(hub_wise_next_day_df)
            
            # Customer Wise Analysis
            st.subheader("👥 Customer Wise Performance")
            
            customers = [
                "WESTSIDE UNIT OF TRENT LIMITED",
                "Herbalife Nutrition",
                "krishna ayurved",
                "Supertails",
                "ZISHTA TRADITIONS PRIVATE LIMITED",
                "The Whole Truth Foods",
                "Koskii",
                "Mokobara",
                "TATA CLiQ",
                "Ferns N Petals",
                "Curefit",
                "Assembly",
                "BHAWAR SALES CORPORATION",
                "WITBRAN"
            ]
            
            if "Customer" in df_filtered.columns:
                # Same Day Customer Performance
                customer_wise_same_day = []
                
                for customer in customers:
                    customer_data = df_filtered[(df_filtered["Customer"] == customer) & (df_filtered["Next Day"] == False)]
                    same_day_orders = customer_data["Order Number"].nunique()
                    
                    same_day_attempted = customer_data[
                        (customer_data["First attempted on"].dt.date == customer_data["Picked on"].dt.date) & 
                        customer_data["First attempted on"].notna()
                    ]["Order Number"].nunique()
                    
                    same_day_delivered = customer_data[
                        (customer_data["Delivered on"].dt.date == customer_data["Picked on"].dt.date) & 
                        customer_data["Delivered on"].notna()
                    ]["Order Number"].nunique()
                    
                    attempted_pct = (same_day_attempted / same_day_orders) * 100 if same_day_orders > 0 else 0
                    delivered_pct = (same_day_delivered / same_day_orders) * 100 if same_day_orders > 0 else 0
                    
                    customer_wise_same_day.append({
                        "Customer Name": customer,
                        "Same Day Orders": same_day_orders,
                        "Attempted": same_day_attempted,
                        "Delivered": same_day_delivered,
                        "Attempted %": f"{attempted_pct:.1f}%",
                        "Delivered %": f"{delivered_pct:.1f}%"
                    })
                
                customer_wise_same_day_df = pd.DataFrame(customer_wise_same_day)
                
                # Next Day Customer Performance
                customer_wise_next_day = []
                
                for customer in customers:
                    customer_data = next_day_orders_filtered[next_day_orders_filtered["Customer"] == customer]
                    next_day_orders_count = customer_data["Order Number"].nunique()
                    
                    next_day_attempted = customer_data[
                        (customer_data["First attempted on"].dt.date >= start_date.date()) & 
                        (customer_data["First attempted on"].dt.date <= end_date.date())
                    ]["Order Number"].nunique()
                    
                    next_day_delivered = customer_data[
                        (customer_data["Delivered on"].dt.date >= start_date.date()) & 
                        (customer_data["Delivered on"].dt.date <= end_date.date())
                    ]["Order Number"].nunique()
                    
                    attempted_pct = (next_day_attempted / next_day_orders_count) * 100 if next_day_orders_count > 0 else 0
                    delivered_pct = (next_day_delivered / next_day_orders_count) * 100 if next_day_orders_count > 0 else 0
                    
                    customer_wise_next_day.append({
                        "Customer Name": customer,
                        "Next Day Orders": next_day_orders_count,
                        "Attempted": next_day_attempted,
                        "Delivered": next_day_delivered,
                        "Attempted %": f"{attempted_pct:.1f}%",
                        "Delivered %": f"{delivered_pct:.1f}%"
                    })
                
                customer_wise_next_day_df = pd.DataFrame(customer_wise_next_day)
                
                # Display Customer Performance
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Same Day Performance**")
                    st.dataframe(customer_wise_same_day_df)
                
                with col2:
                    st.markdown("**Next Day Performance**")
                    st.dataframe(customer_wise_next_day_df)
    
    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")
else:
    st.info("Please upload a CSV file to begin analysis.")