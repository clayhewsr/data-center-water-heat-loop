import random
from datetime import datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a numeric value into a safe range for simulation outputs."""
    return max(min_value, min(max_value, value))


def severity_to_label(severity: int) -> str:
    if severity <= 0:
        return "GREEN"
    if severity == 1:
        return "YELLOW"
    return "RED"


def status_block(label: str) -> str:
    colors = {
        "GREEN": "#1b7f3a",
        "YELLOW": "#a97800",
        "RED": "#b42318",
    }
    color = colors.get(label, "#344054")
    return (
        f"<span style='padding:0.25rem 0.55rem;border-radius:0.4rem;"
        f"background:{color};color:white;font-weight:600;'>{label}</span>"
    )


def build_reading() -> dict:
    """Generate one simulated operations snapshot based on project demo ranges."""
    water_flow_gpm = random.randint(380, 450)
    supply_temp_c = round(random.uniform(17.5, 20.5), 1)
    return_temp_c = round(random.uniform(25.0, 31.5), 1)
    tank_level_pct = random.randint(70, 100)
    pump_pressure_psi = round(random.uniform(35.0, 62.0), 1)
    compute_load_pct = random.randint(35, 98)
    recovered_heat_kw = random.randint(450, 950)
    thermal_storage_pct = random.randint(40, 100)

    # Keep the delta physically reasonable for this prototype.
    temperature_rise_c = round(clamp(return_temp_c - supply_temp_c, 3.0, 14.0), 1)

    return {
        "timestamp": datetime.now(),
        "water_flow_gpm": water_flow_gpm,
        "supply_temp_c": supply_temp_c,
        "return_temp_c": return_temp_c,
        "tank_level_pct": tank_level_pct,
        "pump_pressure_psi": pump_pressure_psi,
        "compute_load_pct": compute_load_pct,
        "recovered_heat_kw": recovered_heat_kw,
        "thermal_storage_pct": thermal_storage_pct,
        "temperature_rise_c": temperature_rise_c,
    }


def evaluate_statuses(reading: dict) -> dict:
    """Apply clear thresholds for system and subsystem health indicators."""
    statuses = {}

    water_loop = 0
    if reading["water_flow_gpm"] < 390 or reading["tank_level_pct"] < 80:
        water_loop = max(water_loop, 1)
    if reading["water_flow_gpm"] < 370 or reading["tank_level_pct"] < 70:
        water_loop = max(water_loop, 2)
    statuses["Water Loop"] = severity_to_label(water_loop)

    cooling_loop = 0
    if reading["temperature_rise_c"] > 11.0 or reading["supply_temp_c"] > 20.0:
        cooling_loop = max(cooling_loop, 1)
    if reading["temperature_rise_c"] > 13.0 or reading["supply_temp_c"] > 21.0:
        cooling_loop = max(cooling_loop, 2)
    statuses["Cooling Loop"] = severity_to_label(cooling_loop)

    heat_recovery = 0
    if reading["recovered_heat_kw"] < 600 or reading["thermal_storage_pct"] < 55:
        heat_recovery = max(heat_recovery, 1)
    if reading["recovered_heat_kw"] < 500 or reading["thermal_storage_pct"] < 45:
        heat_recovery = max(heat_recovery, 2)
    statuses["Heat Recovery"] = severity_to_label(heat_recovery)

    pump_system = 0
    if reading["pump_pressure_psi"] < 40 or reading["pump_pressure_psi"] > 58:
        pump_system = max(pump_system, 1)
    if reading["pump_pressure_psi"] < 36 or reading["pump_pressure_psi"] > 61:
        pump_system = max(pump_system, 2)
    statuses["Pump System"] = severity_to_label(pump_system)

    sensor_network = 0
    sensor_health_score = random.randint(90, 100)
    if sensor_health_score < 95:
        sensor_network = max(sensor_network, 1)
    if sensor_health_score < 92:
        sensor_network = max(sensor_network, 2)
    statuses["Sensor Network"] = severity_to_label(sensor_network)

    overall_severity = 0
    for value in statuses.values():
        if value == "YELLOW":
            overall_severity = max(overall_severity, 1)
        elif value == "RED":
            overall_severity = max(overall_severity, 2)
    statuses["Overall"] = severity_to_label(overall_severity)

    return statuses


def append_history(reading: dict) -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append(reading)
    # Keep recent points for compact, responsive charts.
    st.session_state.history = st.session_state.history[-60:]


def main() -> None:
    st.set_page_config(
        page_title="Data Center Water & Heat Loop Operations Dashboard",
        page_icon="💧",
        layout="wide",
    )

    st.title("Data Center Water & Heat Loop Operations Dashboard")
    st.caption("Simulated operational prototype for monitoring water, cooling, and heat recovery behavior.")

    with st.sidebar:
        st.header("Dashboard Controls")
        refresh_seconds = st.slider("Refresh Interval (seconds)", min_value=2, max_value=30, value=5)
        st.markdown("**Simulation Mode:** Prototype / Simulated")
        st.markdown("**Project Version:** v0.2.0")

    # Timed reruns avoid manual loops and keep the UI responsive.
    st_autorefresh(interval=refresh_seconds * 1000, key="dashboard_refresh")

    try:
        reading = build_reading()
        append_history(reading)
        statuses = evaluate_statuses(reading)
    except Exception as exc:
        st.error(f"Dashboard data update failed: {exc}")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Water Flow Rate", f"{reading['water_flow_gpm']} GPM")
    c2.metric("Supply-Water Temperature", f"{reading['supply_temp_c']} °C")
    c3.metric("Return-Water Temperature", f"{reading['return_temp_c']} °C")
    c4.metric("Temperature Rise", f"{reading['temperature_rise_c']} °C")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Tank Level", f"{reading['tank_level_pct']}%")
    c6.metric("Pump Pressure", f"{reading['pump_pressure_psi']} PSI")
    c7.metric("Compute Load", f"{reading['compute_load_pct']}%")
    c8.metric("Recovered Heat", f"{reading['recovered_heat_kw']} kW")

    st.metric("Thermal Storage", f"{reading['thermal_storage_pct']}%")

    st.subheader("Overall System Status")
    st.markdown(status_block(statuses["Overall"]), unsafe_allow_html=True)

    st.subheader("Subsystem Status")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.markdown(f"**Water Loop**<br>{status_block(statuses['Water Loop'])}", unsafe_allow_html=True)
    s2.markdown(f"**Cooling Loop**<br>{status_block(statuses['Cooling Loop'])}", unsafe_allow_html=True)
    s3.markdown(f"**Heat Recovery**<br>{status_block(statuses['Heat Recovery'])}", unsafe_allow_html=True)
    s4.markdown(f"**Pump System**<br>{status_block(statuses['Pump System'])}", unsafe_allow_html=True)
    s5.markdown(f"**Sensor Network**<br>{status_block(statuses['Sensor Network'])}", unsafe_allow_html=True)

    if len(st.session_state.history) > 1:
        st.subheader("Historical Trends")

        temperature_chart = {
            "Supply Temperature (°C)": [row["supply_temp_c"] for row in st.session_state.history],
            "Return Temperature (°C)": [row["return_temp_c"] for row in st.session_state.history],
            "Temperature Rise (°C)": [row["temperature_rise_c"] for row in st.session_state.history],
        }

        performance_chart = {
            "Water Flow (GPM)": [row["water_flow_gpm"] for row in st.session_state.history],
            "Recovered Heat (kW)": [row["recovered_heat_kw"] for row in st.session_state.history],
            "Compute Load (%)": [row["compute_load_pct"] for row in st.session_state.history],
        }

        st.line_chart(temperature_chart)
        st.line_chart(performance_chart)
    else:
        st.info("Historical charts will appear after additional refresh cycles.")

    st.caption(f"Last update: {reading['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()