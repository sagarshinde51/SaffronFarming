import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Saffron Farm Monitoring",
    page_icon="🌱",
    layout="wide"
)

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password1234"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Saffron Farm Portal Login")
    with st.form("login_form"):
        username = st.text_input("Username", value=DEFAULT_USERNAME)
        password = st.text_input("Password", value=DEFAULT_PASSWORD, type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    st.stop()

DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

def fetch_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        query = "SELECT * FROM SaffronFarm ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        conn.close()

        numeric_cols = ["Temp", "Humidity", "Moisture1", "Moisture2", "Gas"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "DateTime" in df.columns:
            df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")

        return df
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return pd.DataFrame()

col_title, col_actions = st.columns([5, 2])
with col_title:
    st.title("🌱 Saffron Farm Environmental Monitor")

with col_actions:
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    with btn_col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

df = fetch_data()

if df.empty:
    st.warning("No records found in database or failed to connect.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 Latest Data", "📈 Past Data (Graphs)", "📋 All Data (Table)"])

with tab1:
    latest = df.iloc[0]
    
    if "DateTime" in latest and pd.notnull(latest["DateTime"]):
        st.caption(f"Last updated: **{latest['DateTime']}**")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(label="Air Temp", value=f"{latest['Temp']} °C")
    m2.metric(label="Humidity", value=f"{latest['Humidity']} %")
    m3.metric(label="Soil Moisture 1", value=f"{latest['Moisture1']} %")
    m4.metric(label="Soil Moisture 2", value=f"{latest['Moisture2']} %")
    m5.metric(label="Air Gas Raw", value=f"{latest['Gas']}")

    st.markdown("---")
    st.subheader("Threshold Status Check")
    s1, s2, s3 = st.columns(3)
    
    with s1:
        if 10 <= latest['Temp'] <= 20:
            st.success("Temperature is in optimal range (10°C - 20°C)")
        else:
            st.warning(f"Temperature alert: {latest['Temp']}°C")

    with s2:
        if 40 <= latest['Humidity'] <= 65:
            st.success("Humidity is in optimal range (40% - 65%)")
        else:
            st.warning(f"Humidity alert: {latest['Humidity']}%")

    with s3:
        avg_moisture = (latest['Moisture1'] + latest['Moisture2']) / 2
        if 20 <= avg_moisture <= 40:
            st.success("Soil moisture is in optimal range (20% - 40%)")
        else:
            st.warning(f"Average moisture: {avg_moisture:.1f}%")

with tab2:
    st.subheader("Environmental Trends Over Time")
    
    df_sorted = df.sort_values(by="id", ascending=True)
    x_axis = "DateTime" if "DateTime" in df_sorted.columns and df_sorted["DateTime"].notnull().any() else "id"

    fig_climate = px.line(
        df_sorted, 
        x=x_axis, 
        y=["Temp", "Humidity"], 
        markers=True,
        title="Air Temperature (°C) & Relative Humidity (%)",
        labels={"value": "Level", "variable": "Sensor", x_axis: "Timestamp"}
    )
    st.plotly_chart(fig_climate, use_container_width=True)

    fig_moisture = px.line(
        df_sorted, 
        x=x_axis, 
        y=["Moisture1", "Moisture2"], 
        markers=True,
        title="Soil Moisture Profiles (%)",
        labels={"value": "Moisture (%)", "variable": "Sensor", x_axis: "Timestamp"}
    )
    st.plotly_chart(fig_moisture, use_container_width=True)

    fig_gas = px.line(
        df_sorted, 
        x=x_axis, 
        y="Gas", 
        markers=True,
        title="Air Quality / Gas Sensor Level",
        labels={"Gas": "Analog Gas Value", x_axis: "Timestamp"}
    )
    st.plotly_chart(fig_gas, use_container_width=True)

with tab3:
    st.subheader("Historical Farm Records")
    
    col_search, col_dl = st.columns([4, 1])
    with col_search:
        st.write(f"Total Logged Records: **{len(df)}**")
    with col_dl:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="saffron_farm_data.csv",
            mime="text/csv"
        )

    st.dataframe(df, use_container_width=True, hide_index=True)
