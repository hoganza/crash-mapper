import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import io

st.set_page_config(layout="wide")
st.title("🚗 Crash Map Generator")

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type="xlsx")

# Color helper
def get_color(severity):
    if severity == "PDO":
        return "green"
    elif severity == "INJ":
        return "orange"
    elif severity == "FAT":
        return "red"
    return "gray"

if uploaded_file:
    # Read file
    df = pd.read_excel(uploaded_file)
    df = df.dropna(subset=["Latitude", "Longitude", "Date", "Severity"])
    df["Date"] = pd.to_datetime(df["Date"])
    df["Veh1 Dir"] = df["Veh1 Dir"].astype(str).str.strip().str.upper()
    df["Weight"] = df["Severity"].map({"FAT": 3, "INJ": 2, "PDO": 1})

    # Direction logic
    north_dirs = {"N", "NE", "NW"}
    south_dirs = {"S", "SE", "SW"}
    df["Is_Northbound"] = df["Veh1 Dir"].isin(north_dirs)
    df["Is_Southbound"] = df["Veh1 Dir"].isin(south_dirs)

    # Base location
    center = [df["Latitude"].mean(), df["Longitude"].mean()]

    # Create all maps
    def make_severity_map(data):
        m = folium.Map(location=center, zoom_start=11)
        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=6,
                color=get_color(row["Severity"]),
                fill=True,
                fill_opacity=0.8,
                popup=f"{row['Date'].date()} | {row['Severity']} | Dir: {row['Veh1 Dir']}"
            ).add_to(m)
        return m

    def make_heatmap(data):
        m = folium.Map(location=center, zoom_start=11)
        heat_data = [[row["Latitude"], row["Longitude"], row["Weight"]] for _, row in data.iterrows()]
        HeatMap(heat_data, radius=10, blur=15).add_to(m)
        return m

    # Create and show maps
    st.subheader("🔴 Severity Map (color-coded)")
    st_folium(make_severity_map(df), width=700, height=500)

    st.subheader("🔥 Full Heatmap")
    st_folium(make_heatmap(df), width=700, height=500)

    st.subheader("⬆️ Northbound Map (Markers)")
    north_df = df[df["Is_Northbound"]].dropna(subset=["Latitude", "Longitude"])
    if not north_df.empty:
        st_folium(make_severity_map(north_df), width=700, height=500)
        st.subheader("🔥 Northbound Heatmap")
        st_folium(make_heatmap(north_df), width=700, height=500)
    else:
        st.info("No Northbound crashes found.")

    st.subheader("⬇️ Southbound Map (Markers)")
    south_df = df[df["Is_Southbound"]].dropna(subset=["Latitude", "Longitude"])
    if not south_df.empty:
        st_folium(make_severity_map(south_df), width=700, height=500)
        st.subheader("🔥 Southbound Heatmap")
        st_folium(make_heatmap(south_df), width=700, height=500)
    else:
        st.info("No Southbound crashes found.")
