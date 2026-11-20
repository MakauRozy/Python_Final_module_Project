import calendar
import json

import pandas as pd
import streamlit as st

from api import get_solar_estimate, ApiError
from database import (create_table, add_system, get_system, load_monthly, update_capacity, delete_capacity)

ASPECTS = {"South": 0, "South-east": -45, "South-west": 45, "East": -90, "West": 90, "North": 180}
ASPECT_NAMES = {degrees: name for name, degrees in ASPECTS.items()}

st.set_page_config(page_title="Solar Yield Estimator", page_icon="☀️", layout="wide")
create_table()


# Required functions

def calculate(place, peakpower, tilt, aspect, loss, known_location=None):
    """Run the estimate and show any error on the page."""
    try:
        return get_solar_estimate(place, peakpower, tilt, aspect, loss, known_location)
    except ApiError as error:
        st.error(str(error))
        return None


def pick_system(key):
    """Dropdown of saved systems with the newest coming first. Returns the chosen one, or None."""
    saved_systems = get_system()
    if not saved_systems:
        st.info("No systems saved yet. Add one in the first tab.")
        return None
    labels = {
        saved["id"]: f"#{saved['id']} {saved['place']}, {saved['peakpower']:g} kW, "
                     f"{saved['tilt']}° tilt (by {saved['username']})"
        for saved in saved_systems
    }
    chosen_id = st.selectbox("Choose a system", list(labels),
                             format_func=labels.get, key=key)
    return next(saved for saved in saved_systems if saved["id"] == chosen_id)


# Display Page

st.title("How much power will your panels make?")
st.caption("Enter your location description and solar system specifications to estimate your energy output.")

if "message" in st.session_state:
    st.success(st.session_state.pop("message"))


tab_new, tab_view, tab_update, tab_delete = st.tabs(["New system", "View results", "Update", "Delete"])

# adding a new sytem
with tab_new:
    with st.form("new_system"):
        username = st.text_input("Your name")
        place = st.text_input("Location", placeholder="Town or city, country")
        left_col, right_col = st.columns(2)
        peakpower = left_col.number_input("System size (kW)", 0.1, 1000.0, 1.0, step=0.5)
        tilt = right_col.number_input ("Panel tilt (degrees from flat)", 0, 90, 10, step=1)
        aspect_name = left_col.selectbox("Panels face", list(ASPECTS))
        loss = right_col.slider("System losses (%)", 0, 40, 14)
        submitted = st.form_submit_button("Calculate and save", type="primary")

    if submitted:
        if not username.strip() or not place.strip():
            st.warning("Please enter your name and a location.")
        else:
            with st.spinner("Finding the location and fetching solar data..."):
                calculation = calculate(place.strip(), peakpower, tilt, ASPECTS[aspect_name], loss)
            if calculation:
                matched, lat, lon, result = calculation
                add_system(username.strip(), place.strip(), matched, lat, lon,peakpower, tilt, ASPECTS[aspect_name], loss, result)
                st.session_state["message"] = "Saved. See the full results under View results."
                st.rerun()

# Viewing results
with tab_view:
    system = pick_system("view_pick")
    if system:
        monthly_rows = load_monthly([system["id"]])

        st.subheader(system["place"])
        st.caption(f"Matched location: {system['matched']}, {system['latitude']:.3f}, {system['longitude']:.3f}). "
                   f"Saved by {system['username']}.")

        st.markdown("**Inputs**")
        size_col, tilt_col, facing_col, loss_col = st.columns(4)
        size_col.metric("System size", f"{system['peakpower']:g} kW")
        tilt_col.metric("Tilt", f"{system['tilt']}°")
        facing_col.metric("Panels face",
                          ASPECT_NAMES.get(system["aspect"], f"{system['aspect']:g}°"))
        loss_col.metric("Losses", f"{system['loss']}%")

        if not monthly_rows:
            st.warning("No monthly results are saved for this system.")
        else:
            monthly_table = pd.DataFrame(monthly_rows)
            monthly_table["Month"] = monthly_table["month"].apply(
                lambda month_number: calendar.month_abbr[month_number])
            best_month = monthly_table.loc[monthly_table["energy_kwh"].idxmax()]
            weakest_month = monthly_table.loc[monthly_table["energy_kwh"].idxmin()]

            st.markdown("**Results**")
            year_col, day_col, best_col, weakest_col = st.columns(4)
            year_col.metric("Energy per year", f"{system['yearly_kwh']:,.0f} kWh")
            day_col.metric("Average per day", f"{system['yearly_kwh'] / 365:.1f} kWh")
            best_col.metric("Best month",
                            f"{best_month['Month']} ({best_month['energy_kwh']:,.0f} kWh)")
            weakest_col.metric("Weakest month",
                               f"{weakest_month['Month']} ({weakest_month['energy_kwh']:,.0f} kWh)")

            st.markdown("**Month by month**")
            display_table = monthly_table[["Month", "energy_kwh", "irradiation"]].rename(
                columns={"energy_kwh": "Energy (kWh)", "irradiation": "Sunlight (kWh/m²)"})
            st.dataframe(display_table.round(1), hide_index=True)

            # ---- downloads ----
            as_json = json.dumps({"system": system, "monthly": monthly_rows}, indent=2)
            flat_rows = [{**system, **row} for row in monthly_rows]
            as_csv = pd.DataFrame(flat_rows).drop(columns=["run_id"]).to_csv(index=False)

            json_col, csv_col, _ = st.columns([1, 1, 4])
            json_col.download_button("Download JSON", as_json,
                                     file_name=f"system_{system['id']}.json",
                                     mime="application/json")
            csv_col.download_button("Download CSV", as_csv,
                                    file_name=f"system_{system['id']}.csv",
                                    mime="text/csv")

# Updating entries
with tab_update:
    system = pick_system("update_pick")
    if system:
        system_id = system["id"]
        aspect_degrees = list(ASPECTS.values())
        st.caption(f"System #{system_id}, saved by {system['username']}. "
                   "The ID and name can't be changed.")

        with st.form(f"update_form_{system_id}"):
            new_place = st.text_input("Location", value=system["place"],
                                      key=f"place_{system_id}")
            left_col, right_col = st.columns(2)
            new_peakpower = left_col.number_input(
                "System size (kW)", 0.1, 1000.0, float(system["peakpower"]),
                step=0.5, key=f"power_{system_id}")
            new_tilt = right_col.slider(
                "Panel tilt (degrees from flat)", 0, 90, int(system["tilt"]),
                key=f"tilt_{system_id}")
            new_aspect_name = left_col.selectbox(
                "Panels face", list(ASPECTS),
                index=aspect_degrees.index(system["aspect"])
                if system["aspect"] in aspect_degrees else 0,
                key=f"aspect_{system_id}")
            new_loss = right_col.slider("System losses (%)", 0, 40, int(system["loss"]),
                                        key=f"loss_{system_id}")
            update_clicked = st.form_submit_button("Recalculate and update", type="primary")

        if update_clicked:
            if not new_place.strip():
                st.warning("Please enter a location.")
            else:
                # same place as before? reuse the saved coordinates
                known_location = None
                if new_place.strip() == system["place"]:
                    known_location = (system["matched"], system["latitude"],
                                      system["longitude"])
                with st.spinner("Recalculating..."):
                    calculation = calculate(new_place.strip(), new_peakpower, new_tilt,
                                            ASPECTS[new_aspect_name], new_loss,
                                            known_location)
                if calculation:
                    matched, lat, lon, result = calculation
                    update_capacity(system_id, new_place.strip(), matched, lat, lon,
                                    new_peakpower, new_tilt, ASPECTS[new_aspect_name],
                                    new_loss, result)
                    st.session_state["message"] = f"System #{system_id} updated with fresh results."
                    st.rerun()

#Deleting entries
with tab_delete:
    system = pick_system("delete_pick")
    if system:
        st.write(f"**{system['place']}**: {system['peakpower']:g} kW, "
                 f"{system['tilt']}° tilt, {system['yearly_kwh']:,.0f} kWh per year.")
        confirmed = st.checkbox("Yes, delete this system and its results permanently",
                                key=f"confirm_{system['id']}")
        if st.button("Delete", disabled=not confirmed):
            delete_capacity(system["id"])
            st.session_state["message"] = f"System #{system['id']} deleted."
            st.rerun()