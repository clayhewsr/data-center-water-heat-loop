import random
from datetime import datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh


CONTROL_DEFAULTS = {
    "refresh_seconds": 5,
    "compute_load": 70,
    "cooling_demand": 65,
    "heat_reuse_demand": 50,
    "starting_tank_level": 85,
    "pump_mode": "Auto",
    "fault_leak_detected": False,
    "fault_pump_failure": False,
    "fault_high_return_temp": False,
    "fault_sensor_offline": False,
}

SENSOR_AFFECTED_FIELDS = {
    "water_flow_gpm",
    "supply_temp_c",
    "return_temp_c",
    "tank_level_pct",
    "pump_pressure_psi",
    "temperature_rise_c",
}


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


def initialize_state() -> None:
    for key, value in CONTROL_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "history" not in st.session_state:
        st.session_state.history = []

    if "tank_level_state" not in st.session_state:
        st.session_state.tank_level_state = float(st.session_state.starting_tank_level)

    if "thermal_storage_state" not in st.session_state:
        st.session_state.thermal_storage_state = 78.0


def reset_simulation_state() -> None:
    for key, value in CONTROL_DEFAULTS.items():
        st.session_state[key] = value
    st.session_state.history = []
    st.session_state.tank_level_state = float(CONTROL_DEFAULTS["starting_tank_level"])
    st.session_state.thermal_storage_state = 78.0


def clear_faults() -> None:
    st.session_state.fault_leak_detected = False
    st.session_state.fault_pump_failure = False
    st.session_state.fault_high_return_temp = False
    st.session_state.fault_sensor_offline = False


def resolve_pump_mode(selected_mode: str, compute_load_pct: int, cooling_demand_pct: int) -> str:
    if selected_mode != "Auto":
        return selected_mode

    demand_score = (0.6 * cooling_demand_pct) + (0.4 * compute_load_pct)
    if demand_score >= 78:
        return "High"
    if demand_score >= 42:
        return "Normal"
    return "Low"


def build_reading() -> dict:
    """Generate one controlled simulation snapshot for operator training behavior."""
    compute_load_pct = int(st.session_state.compute_load)
    cooling_demand_pct = int(st.session_state.cooling_demand)
    heat_reuse_demand_pct = int(st.session_state.heat_reuse_demand)
    selected_pump_mode = st.session_state.pump_mode

    leak_detected = bool(st.session_state.fault_leak_detected)
    pump_failure = bool(st.session_state.fault_pump_failure)
    high_return_temp = bool(st.session_state.fault_high_return_temp)
    sensor_offline = bool(st.session_state.fault_sensor_offline)

    effective_pump_mode = resolve_pump_mode(selected_pump_mode, compute_load_pct, cooling_demand_pct)

    flow_factor = {"Low": 0.86, "Normal": 1.0, "High": 1.14}[effective_pump_mode]
    pressure_factor = {"Low": 0.88, "Normal": 1.0, "High": 1.16}[effective_pump_mode]

    base_required_flow = 320 + (1.55 * cooling_demand_pct) + (0.35 * compute_load_pct)
    water_flow_gpm = base_required_flow * flow_factor + random.uniform(-8.0, 8.0)

    supply_temp_c = 17.4 + (0.016 * cooling_demand_pct) + random.uniform(-0.4, 0.4)
    return_temp_c = (
        supply_temp_c
        + 4.2
        + (0.067 * compute_load_pct)
        + (0.02 * cooling_demand_pct)
        + random.uniform(-0.6, 0.6)
    )
    if high_return_temp:
        return_temp_c += 3.8

    pump_pressure_psi = (
        33.0
        + (0.21 * cooling_demand_pct)
        + (0.06 * compute_load_pct)
    ) * pressure_factor + random.uniform(-1.4, 1.4)

    recovered_heat_kw = 340 + (6.0 * compute_load_pct) + (1.6 * cooling_demand_pct) + random.uniform(-30.0, 30.0)

    # Tank level starts from the operator-selected baseline and then evolves over time.
    target_tank = float(st.session_state.starting_tank_level)
    current_tank = float(st.session_state.tank_level_state)
    current_tank += (target_tank - current_tank) * 0.08
    tank_delta = 1.25 - (0.022 * cooling_demand_pct) - (0.013 * compute_load_pct)
    if leak_detected:
        tank_delta -= 2.2 + (0.012 * cooling_demand_pct)
    current_tank = clamp(current_tank + tank_delta + random.uniform(-0.3, 0.3), 20.0, 100.0)
    st.session_state.tank_level_state = current_tank

    # Heat-reuse demand draws thermal storage over time.
    storage_state = float(st.session_state.thermal_storage_state)
    storage_charge = max(recovered_heat_kw, 0.0) / 700.0
    storage_draw = (0.045 * heat_reuse_demand_pct) + (0.005 * compute_load_pct)
    storage_state = clamp(storage_state + storage_charge - storage_draw + random.uniform(-0.4, 0.4), 0.0, 100.0)
    st.session_state.thermal_storage_state = storage_state

    if pump_failure:
        water_flow_gpm *= 0.35
        pump_pressure_psi *= 0.42

    water_flow_gpm = int(round(clamp(water_flow_gpm, 80.0, 520.0)))
    supply_temp_c = round(clamp(supply_temp_c, 16.0, 23.0), 1)
    return_temp_c = round(clamp(return_temp_c, 21.0, 38.0), 1)
    pump_pressure_psi = round(clamp(pump_pressure_psi, 8.0, 65.0), 1)
    recovered_heat_kw = int(round(clamp(recovered_heat_kw, 120.0, 1100.0)))
    tank_level_pct = int(round(current_tank))
    thermal_storage_pct = int(round(storage_state))

    temperature_rise_c = round(clamp(return_temp_c - supply_temp_c, 3.0, 16.0), 1)

    return {
        "timestamp": datetime.now(),
        "water_flow_gpm": water_flow_gpm,
        "supply_temp_c": supply_temp_c,
        "return_temp_c": return_temp_c,
        "tank_level_pct": tank_level_pct,
        "pump_pressure_psi": pump_pressure_psi,
        "compute_load_pct": compute_load_pct,
        "cooling_demand_pct": cooling_demand_pct,
        "heat_reuse_demand_pct": heat_reuse_demand_pct,
        "recovered_heat_kw": recovered_heat_kw,
        "thermal_storage_pct": thermal_storage_pct,
        "temperature_rise_c": temperature_rise_c,
        "effective_pump_mode": effective_pump_mode,
        "fault_leak_detected": leak_detected,
        "fault_pump_failure": pump_failure,
        "fault_high_return_temp": high_return_temp,
        "fault_sensor_offline": sensor_offline,
    }


def evaluate_statuses(reading: dict) -> dict:
    """Apply clear thresholds for system and subsystem health indicators."""
    statuses = {}

    water_loop = 0
    if reading["water_flow_gpm"] < 390 or reading["tank_level_pct"] < 80:
        water_loop = max(water_loop, 1)
    if reading["water_flow_gpm"] < 370 or reading["tank_level_pct"] < 70:
        water_loop = max(water_loop, 2)
    if reading["fault_leak_detected"]:
        water_loop = max(water_loop, 1)
    statuses["Water Loop"] = severity_to_label(water_loop)

    cooling_loop = 0
    if reading["temperature_rise_c"] > 11.0 or reading["supply_temp_c"] > 20.0:
        cooling_loop = max(cooling_loop, 1)
    if reading["temperature_rise_c"] > 13.0 or reading["supply_temp_c"] > 21.0:
        cooling_loop = max(cooling_loop, 2)
    if reading["fault_high_return_temp"]:
        cooling_loop = max(cooling_loop, 1)
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
    if reading["fault_pump_failure"]:
        pump_system = 2
    statuses["Pump System"] = severity_to_label(pump_system)

    sensor_network = 0
    if reading["fault_sensor_offline"]:
        sensor_network = 2
    else:
        sensor_health_score = random.randint(92, 100)
        if sensor_health_score < 96:
            sensor_network = max(sensor_network, 1)
        if sensor_health_score < 94:
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


def format_metric(reading: dict, key: str, suffix: str) -> str:
    if reading["fault_sensor_offline"] and key in SENSOR_AFFECTED_FIELDS:
        return "Unavailable"
    return f"{reading[key]}{suffix}"


def chart_series_value(row: dict, key: str):
    if row.get("fault_sensor_offline") and key in SENSOR_AFFECTED_FIELDS:
        return None
    return row[key]


def condition_badge(condition: str) -> str:
    if condition == "Normal":
        return "🟢 Normal"
    if condition == "Warning":
        return "🟡 Warning"
    return "🔴 Critical"


def run_ai_analysis(reading: dict, statuses: dict) -> dict:
    issues = []
    recommended_actions = []
    predicted_outcomes = []
    confidence_notes = []

    root_cause = "No active anomaly pattern detected."
    confidence = 92

    if reading["fault_pump_failure"]:
        issues.append("Pump Failure fault is active.")
        root_cause = "Primary circulation pump failure."
        confidence = 98
        recommended_actions.append("Switch to backup pump and verify circulation recovery.")
        predicted_outcomes.append("Water flow and recovered heat will continue dropping.")

    if reading["fault_leak_detected"]:
        issues.append("Leak Detected fault is active.")
        if root_cause == "No active anomaly pattern detected.":
            root_cause = "Water leak suspected."
            confidence = 97
        recommended_actions.append("Isolate affected loop and inspect piping for leaks.")
        predicted_outcomes.append("Tank level will continue decreasing.")

    if reading["fault_high_return_temp"] or reading["return_temp_c"] > 31.0 or reading["temperature_rise_c"] > 11.0:
        issues.append("Return temperature is above expected range.")
        if root_cause == "No active anomaly pattern detected.":
            root_cause = "Reduced cooling efficiency or fouled heat exchanger."
            confidence = 94
        recommended_actions.append("Inspect heat exchanger and increase cooling capacity.")
        predicted_outcomes.append("Cooling stress will increase and thermal margins will narrow.")

    if reading["fault_sensor_offline"]:
        issues.append("Sensor Offline fault is active.")
        if root_cause == "No active anomaly pattern detected.":
            root_cause = "Sensor communication failure."
            confidence = 100
        recommended_actions.append("Restore sensor connectivity and validate readings.")
        predicted_outcomes.append("Operational decisions will carry elevated uncertainty.")
        confidence_notes.append("Confidence is reduced for calculations that depend on offline sensors.")

    if reading["tank_level_pct"] < 80 and not reading["fault_leak_detected"]:
        issues.append("Tank level is trending low.")
        recommended_actions.append("Increase replenishment or reduce demand load.")
        predicted_outcomes.append("Water-loop stability may degrade if level continues to fall.")

    if reading["water_flow_gpm"] < 390 and not reading["fault_pump_failure"]:
        issues.append("Flow is below preferred operating range.")
        recommended_actions.append("Raise pump mode or reduce cooling demand.")
        predicted_outcomes.append("Heat removal performance may decline.")

    if reading["thermal_storage_pct"] < 45:
        issues.append("Thermal storage reserve is low.")
        recommended_actions.append("Reduce heat-reuse demand or increase recovery input.")
        predicted_outcomes.append("Recovered heat availability will tighten.")

    status_penalty = 0
    for key in ("Water Loop", "Cooling Loop", "Heat Recovery", "Pump System", "Sensor Network"):
        label = statuses.get(key, "GREEN")
        if label == "YELLOW":
            status_penalty += 8
        elif label == "RED":
            status_penalty += 18

    health_score = clamp(100 - status_penalty, 0, 100)
    if reading["fault_pump_failure"]:
        health_score -= 18
    if reading["fault_leak_detected"]:
        health_score -= 10
    if reading["fault_high_return_temp"]:
        health_score -= 10
    if reading["fault_sensor_offline"]:
        health_score -= 12
    health_score = int(clamp(round(health_score), 0, 100))

    if statuses["Overall"] == "RED" or reading["fault_pump_failure"]:
        condition = "Critical"
    elif statuses["Overall"] == "YELLOW" or issues:
        condition = "Warning"
    else:
        condition = "Normal"

    if reading["fault_sensor_offline"] and confidence < 100:
        confidence = max(55, confidence - 22)

    if not issues:
        issues = ["No active issues detected in the current simulation state."]
        recommended_actions = ["Continue monitoring and maintain current settings."]
        predicted_outcomes = ["System is expected to remain stable under current demand."]

    return {
        "health_score": health_score,
        "condition": condition,
        "condition_badge": condition_badge(condition),
        "detected_issues": issues,
        "root_cause": root_cause,
        "confidence": int(clamp(confidence, 0, 100)),
        "recommended_actions": recommended_actions,
        "predicted_outcome": predicted_outcomes,
        "confidence_notes": confidence_notes,
        "analysis_timestamp": datetime.now(),
    }


def main() -> None:
    st.set_page_config(
        page_title="Data Center Water & Heat Loop Operations Dashboard",
        page_icon="💧",
        layout="wide",
    )

    st.title("Data Center Water & Heat Loop Operations Dashboard")
    st.caption("Simulated operational prototype for monitoring water, cooling, and heat recovery behavior.")
    st.warning(
        "Simulation Notice: This is a simulated operator-training prototype and does not control real equipment."
    )

    initialize_state()

    with st.sidebar:
        st.header("Dashboard Controls")
        refresh_seconds = st.slider(
            "Refresh Interval (seconds)",
            min_value=2,
            max_value=30,
            key="refresh_seconds",
        )

        st.divider()
        st.header("Simulation Controls")
        st.slider("Compute Load (%)", min_value=0, max_value=100, key="compute_load")
        st.slider("Cooling Demand (%)", min_value=0, max_value=100, key="cooling_demand")
        st.slider("Heat-Reuse Demand (%)", min_value=0, max_value=100, key="heat_reuse_demand")
        st.slider("Starting Tank Level (%)", min_value=20, max_value=100, key="starting_tank_level")
        st.selectbox("Pump Mode", options=["Auto", "Low", "Normal", "High"], key="pump_mode")

        st.button("Reset Simulation", use_container_width=True, on_click=reset_simulation_state)

        st.subheader("Fault Injection")
        st.checkbox("Leak Detected", key="fault_leak_detected")
        st.checkbox("Pump Failure", key="fault_pump_failure")
        st.checkbox("High Return Temperature", key="fault_high_return_temp")
        st.checkbox("Sensor Offline", key="fault_sensor_offline")

        st.button("Clear Faults", use_container_width=True, on_click=clear_faults)

        st.divider()
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
    c1.metric("Water Flow Rate", format_metric(reading, "water_flow_gpm", " GPM"))
    c2.metric("Supply-Water Temperature", format_metric(reading, "supply_temp_c", " °C"))
    c3.metric("Return-Water Temperature", format_metric(reading, "return_temp_c", " °C"))
    c4.metric("Temperature Rise", format_metric(reading, "temperature_rise_c", " °C"))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Tank Level", format_metric(reading, "tank_level_pct", "%"))
    c6.metric("Pump Pressure", format_metric(reading, "pump_pressure_psi", " PSI"))
    c7.metric("Compute Load", f"{reading['compute_load_pct']}%")
    c8.metric("Recovered Heat", f"{reading['recovered_heat_kw']} kW")

    st.metric("Thermal Storage", f"{reading['thermal_storage_pct']}%")
    st.caption(f"Effective Pump Mode: {reading['effective_pump_mode']}")

    if reading["fault_sensor_offline"]:
        st.error(
            "Sensor Network Fault: live sensor fields are marked as Unavailable "
            "for flow, supply/return temperature, tank level, pressure, and temperature rise."
        )

    st.subheader("Overall System Status")
    st.markdown(status_block(statuses["Overall"]), unsafe_allow_html=True)

    analysis = run_ai_analysis(reading, statuses)

    st.subheader("AI Analysis")
    with st.container(border=True):
        a1, a2, a3 = st.columns(3)
        a1.metric("Overall Health Score", f"{analysis['health_score']}")
        a2.metric("System Condition", analysis["condition_badge"])
        a3.metric("Confidence", f"{analysis['confidence']}%")

        st.markdown(f"**Probable Root Cause:** {analysis['root_cause']}")

        st.markdown("**Detected Issues**")
        for issue in analysis["detected_issues"]:
            st.write(f"- {issue}")

        st.markdown("**Recommended Actions**")
        for action in analysis["recommended_actions"]:
            st.write(f"- {action}")

        st.markdown("**Predicted Outcome if no action is taken**")
        for outcome in analysis["predicted_outcome"]:
            st.write(f"- {outcome}")

        if analysis["confidence_notes"]:
            for note in analysis["confidence_notes"]:
                st.caption(note)

        st.caption(
            "AI analysis last updated: "
            f"{analysis['analysis_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

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
            "Supply Temperature (°C)": [chart_series_value(row, "supply_temp_c") for row in st.session_state.history],
            "Return Temperature (°C)": [chart_series_value(row, "return_temp_c") for row in st.session_state.history],
            "Temperature Rise (°C)": [chart_series_value(row, "temperature_rise_c") for row in st.session_state.history],
        }

        performance_chart = {
            "Water Flow (GPM)": [chart_series_value(row, "water_flow_gpm") for row in st.session_state.history],
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