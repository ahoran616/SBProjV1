# === 📦 IMPORTS & SETUP ===
import os
import requests
import streamlit as st
from app.config import DEV_MODE
from openai import OpenAI
from app.logic import get_lift_data, get_weather_data

print(f"DEV_MODE is: {DEV_MODE}")  # 

# 🔐 OpenAI API client setup
client = OpenAI(api_key=os.environ["openai_api_key"])

# === 🌄 RESORT DEFINITIONS ===
resorts = {
    "Sugarbush": (44.1938, -72.7771),
    "Stratton": (43.0913, -72.9036),
    "Sunday River": (44.4790, -70.8903)
}

# Liftie slugs mapping
liftie_slugs = {
    "Sugarbush": "sugarbush",
    "Stratton": "stratton",
    "Sunday River": "sunday-river"
}


# === ⟳ UNIT CONVERSIONS ===
def c_to_f(c):
    return round((c * 9 / 5) + 32, 1)


def mm_to_in(mm):
    return round(mm / 25.4, 1)


# === 🎨 STREAMLIT PAGE CONFIGURATION ===
st.set_page_config(page_title="Snowboard Conditions", layout="centered")
st.title("🏂 Snowboard Conditions")
st.caption("Live data from Open-Meteo + Liftie + GPT-4o Ride Recommendation")
if DEV_MODE:
    with st.sidebar:
        st.info("⚙️ DEV MODE ENABLED - USING MOCK DATA INSTEAD OF LIVE DATA")
    
# ☔️ WEATHER & SNOW CONDITIONS (OPEN-METEO) + LIFT STATUS
summary_prompt = "Here is today's snowboard mountain report:\n\n"

for name, (lat, lon) in resorts.items():
    slug = liftie_slugs.get(name)

    # === Weather ===

    data = get_weather_data(name, lat, lon)

    cw = data.get("current_weather", {})
    daily = data.get("daily", {})

    temp_c = cw.get("temperature", 0)
    wind_kph = cw.get("windspeed", 0)
    snowfall_mm = daily.get("snowfall_sum", [0])[0]
    snowdepth_mm = daily.get("snow_depth_max", [0])[0]

    st.subheader(f"{name} Conditions")
    st.metric("🌡️ Temp", f"{c_to_f(temp_c)}°F")
    st.metric("💨 Wind", f"{round(wind_kph * 0.621371, 1)} mph")
    st.metric("❄️ New Snow", f"{mm_to_in(snowfall_mm)} in")
    st.metric("🏔️ Snow Depth", f"{mm_to_in(snowdepth_mm)} in")

    summary_prompt += (f"{name} Weather:\n"
                       f"- Temp: {c_to_f(temp_c)}°F\n"
                       f"- Wind: {round(wind_kph * 0.621371, 1)} mph\n"
                       f"- New Snow: {mm_to_in(snowfall_mm)} in\n"
                       f"- Snow Depth: {mm_to_in(snowdepth_mm)} in\n\n")

    # === Lift Status ===
    try:
        lift_data = get_lift_data(slug, dev_mode=DEV_MODE)
        if not lift_data:
            st.warning(f"⚠️ No lift data available for {name}.")
            continue
    except Exception as e:
        st.warning(f"⚠️ Error loading lift data for {name}: {e}")
        continue

    lift_statuses = lift_data.get("lifts", {}).get("status", {})
    total_lifts = len(lift_statuses)
    open_lifts = sum(1 for status in lift_statuses.values()
                     if status == "open")
    hold_lifts = sum(1 for status in lift_statuses.values()
                     if status == "hold")
    closed_lifts = sum(1 for status in lift_statuses.values()
                       if status == "closed")

    st.subheader(f"🚡 {name} Lift Status")
    st.metric("Lifts Open", f"{open_lifts}/{total_lifts}")

    hold_color = "orange" if hold_lifts > 0 else "white"
    st.markdown(
        f"**On Hold:** <span style='color: {hold_color}; font-size: 24px;'>{hold_lifts}</span>",
        unsafe_allow_html=True)

    st.write("Lift-by-lift breakdown:")
    for lift_name, status in lift_statuses.items():
        if status == "open":
            st.markdown(
                f"<span style='color: green;'>✅ {lift_name}: Open</span>",
                unsafe_allow_html=True)
        elif status == "hold":
            st.markdown(
                f"<span style='color: orange;'>🟡 {lift_name}: On Hold</span>",
                unsafe_allow_html=True)
        elif status == "closed":
            st.markdown(
                f"<span style='color: red;'>⛔ {lift_name}: Closed</span>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<span style='color: gray;'>❓ {lift_name}: Unknown</span>",
                unsafe_allow_html=True)

    summary_prompt += (f"{name} Lift Status:\n"
                       f"- Lifts Open: {open_lifts}/{total_lifts}\n"
                       f"- On Hold: {hold_lifts}\n\n")

# === 🧠 GPT PROMPT FINALIZATION ===
summary_prompt += (
    "Based on this, which mountain is best to ride today and why? "
    "Make the response friendly and informative for a snowboarder. "
    "If there is no snow, say so. Make it inclusive to snowboarders and skiers. "
    "If mountains are closed to skiing and riding for the season, start with this, "
    "and instead recommend other in-season activities that are available at the specific resorts."
)

# === 🤖 GPT RESPONSE DISPLAY ===
if st.button("Get Recommendation"):
    try:
        resp = requests.post(
            "http://localhost:8000/recommend",
            json={"message": summary_prompt}
        )
        if resp.status_code == 200:
            recommendation = resp.json().get("recommendation")
            st.subheader("🤖 Recommendation")
            st.success(recommendation)
        else:
            st.error("Failed to get recommendation from backend.")
    except Exception as e:
        st.error(f"Backend request failed: {e}")
        