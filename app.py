import streamlit as st
import streamlit_nested_layout
from typing import NamedTuple 
from typing import List
import numpy as np
import pandas as pd

from funcs import st_plot
from methods import monotype
from methods import treshold
from methods import optimal
from funcs import plotting
from methods import aeneas

class BatteryCell(NamedTuple):  # Class for defining battery cells
    capacity:   float   # Rated capacity (Ah)
    voltage:    float   # Nominal voltage (V)
    dis_rate:   float   # Maximum discharge rate (A/Ah)
    chg_rate:   float   # Maximum charge rate (A/Ah)
    resistance: float   # Internal resistance (Ohm)
    weight:     float   # Cell weight (kg)
    cost_spec:  float   # Specific cost (€/kWh)
    OCV: List[float]        # Open-circuit voltage (V)
    OCV_SOC: List[float]    # State of Charge (0-1)
    aging: List[float]      # fitting parameters for aging model (a, b, c, d)

    @property
    def energy(self):       # Energy Capacity (kWh)
        return self.capacity * self.voltage / 1000
    
    @property
    def cost(self):         # Cost per cell (€)
        return self.energy * self.cost_spec
    
    @property
    def dis_current(self):  # Maximum discharge current (A)
        return self.dis_rate * self.capacity
    
    @property
    def chg_current(self):  # Maximum charge current (A)
        return self.chg_rate * self.capacity

st.set_page_config(
    page_title="AENAES Sizing Tool",
    page_icon=":battery:",
    layout="wide",
)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;r
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

hex_color = ["#66c298", "#fc8d62", "#8da0cb"]

st.markdown(f"<h2 style='text-align: center; color: {hex_color[0]};'>⚡AENEAS SIZING⚡</h2>", unsafe_allow_html=True)
tabs = st.tabs([":one: Inputs", ":two: Results"])
placeholders = [tabs[1].empty()]
for i in placeholders: i.warning("Click the 'Start Calculation' button to generate results", icon="🎯")



hcols = tabs[0].columns([4,5], gap="large")
cols = hcols[0].columns(2, gap="medium")

#cols[0].markdown(f"<div style='background-color: {hex_color[2]}; color: white; padding: 8px; text-align: center; font-weight: bold; border-radius: 10px;'>High Energy Cell</div>", unsafe_allow_html=True)
#cols[1].markdown(f"<div style='background-color: {hex_color[1]}; color: white; padding: 8px; text-align: center; font-weight: bold; border-radius: 10px;'>High Power Cell</div>", unsafe_allow_html=True)
cols[0].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>High Energy Cell</div>", unsafe_allow_html=True)
cols[1].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>High Power Cell</div>", unsafe_allow_html=True)

cols[0].write("")
cols[1].write("")

cols = hcols[0].columns(2, gap="medium")

CELL_TECHS = ["Nickel Magnesium Cobalt (NMC)", "Solid State Battery (SSB)", "Lithium Titanate (LTO)", "Supercapacitor (SC)"]
select_HE = cols[0].selectbox("Battery Cell Technology", CELL_TECHS, index=1)
select_HP = cols[1].selectbox("Battery Cell Technology", CELL_TECHS, index=3)



cell_NMC = BatteryCell(
    capacity    = 50.0,
    voltage     = 3.67,
    dis_rate    = 1.0,
    chg_rate    = 1.0,
    cost_spec   = 150.0,
    resistance  = 1.5 / 1000,
    weight      = 1000*0.885, 
    OCV         = [3.427, 3.508, 3.588, 3.621, 3.647, 3.684, 3.761, 3.829, 3.917, 4.019, 4.135],
    OCV_SOC     = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
    aging       = [694700, -0.1770, 52790, -0.0356],
)

cell_LTO = BatteryCell(
    capacity    = 23.0,
    voltage     = 2.3,
    dis_rate    = 4.0,
    chg_rate    = 4.0,
    cost_spec   = 380.0,
    resistance  = 1.1 / 1000, 
    weight      = 1000*0.55,
    OCV         = [2.067, 2.113, 2.151, 2.183, 2.217, 2.265, 2.326, 2.361, 2.427, 2.516, 2.653],
    OCV_SOC     = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
    aging       = [6881000, -0.1950, 426500, -0.0418],
) 

cell_SSB = BatteryCell(
    capacity    = 106.0,
    voltage     = 3.55,
    dis_rate    = 0.33,
    chg_rate    = 0.33,
    cost_spec   = 150.0*100,
    resistance  = 1.2 / 1000,
    weight      = 1000*1.083, 
    OCV         = [2.5, 3.025, 3.55, 3.9, 4.25],
    OCV_SOC     = [0, 0.25, 0.5, 0.75, 1],
    aging       = [6881000, -0.1950, 426500, -0.0418],
)

cell_SC = BatteryCell(
    capacity    = 0.75,
    voltage     = 1.95,
    dis_rate    = 173.3,
    chg_rate    = 173.3,
    cost_spec   = 54700.0,
    resistance  = 0.2 / 1000,
    weight      = 1000*0.542, 
    OCV         = [1.5, 1.75, 1.95, 2, 2.4],
    OCV_SOC     = [0, 0.33, 0.56, 0.61, 1],
    aging       = [6881000, -0.1950, 426500, -0.0418],
)

cell_HE = cell_NMC if select_HE == CELL_TECHS[0] else cell_SSB
cell_HP = cell_LTO if select_HP == CELL_TECHS[2] else cell_SC


scols = cols[0].columns(2)
cell_HE = BatteryCell(
    capacity    = scols[0].number_input("Rated Capacity _(Ah)_", value=cell_HE.capacity, min_value=0.0, step=10.0),
    voltage     = scols[1].number_input("Cell Voltage _(V)_", value=cell_HE.voltage, min_value=0.0, step=0.1, disabled=True),
    dis_rate    = scols[0].number_input("Discharge C-rate _(A/Ah)_", value=cell_HE.dis_rate, min_value=0.0, step=0.25),
    chg_rate    = scols[1].number_input("Charge C-rate _(A/Ah)_", value=cell_HE.chg_rate, min_value=0.0, step=0.25, disabled=True),
    resistance  = scols[0].number_input("Internal Resistance _(mΩ)_", value=cell_HE.resistance*1000.0, min_value=0.0, step=0.1)/1000,
    weight      = scols[1].number_input("Cell Weight _(g)_", value=cell_HE.weight, min_value=0.0, step=0.1),
    cost_spec   = cell_HE.cost_spec,
    OCV         = cell_HE.OCV,
    OCV_SOC     = cell_HE.OCV_SOC,
    aging       = cell_HE.aging,
)


scols = cols[1].columns(2)
cell_HP = BatteryCell(
    capacity    = scols[0].number_input("Rated Capacity _(Ah)_", value=cell_HP.capacity, min_value=0.0, step=10.0),
    voltage     = scols[1].number_input("Cell Voltage _(V)_", value=cell_HP.voltage, min_value=0.0, step=0.1, disabled=True),
    dis_rate    = scols[0].number_input("Discharge C-rate _(A/Ah)_", value=cell_HP.dis_rate, min_value=0.0, step=0.25),
    chg_rate    = scols[1].number_input("Charge C-rate _(A/Ah)_", value=cell_HP.chg_rate, min_value=0.0, step=0.25, disabled=True),
    resistance  = scols[0].number_input("Internal Resistance _(mΩ)_", value=cell_HP.resistance*1000, min_value=0.0, step=0.1)/1000,
    weight      = scols[1].number_input("Cell Weight _(g)_", value=cell_HP.weight, min_value=0.0, step=0.1),
    cost_spec   = cell_HP.cost_spec,
    OCV         = cell_HP.OCV,
    OCV_SOC     = cell_HP.OCV_SOC,
    aging       = cell_HP.aging,
)


hcols[0].divider()
cols = hcols[0].columns([2, 1], gap="medium")
V_bus = cols[0].number_input("Nominal Battery Voltage _(V)_", value=33*cell_HP.voltage, min_value=0.0, step=100.0)
bool_aging = cols[1].checkbox("Enable Cell Degradation", value=False, disabled=True)
bool_charge = cols[1].checkbox("Allow Intercharging", value=True, disabled=True)

run = tabs[0].button("Start Calculation...", type="primary", use_container_width=True)

load_files = [hcols[1].file_uploader("Upload a load profile", type=["csv"], key=137)]
cycles = 0 #[hcols[1].number_input("Load cycles during lifetime", min_value=0, value=3650 if bool_aging else 0, key=120, disabled=not bool_aging)]



if load_files[0] is not None:
    loads = [pd.read_csv(load_files[0])]
else:
    loads = [pd.read_csv("loads/aeneas_1_div29.csv")] #_div60

limit = hcols[1].slider("Power Treshold _(kW)_", 0.0, max(loads[0]["P"])/1e3, max(loads[0]["P"])/2e3, help="If the power demand is below this line, only the HE cells wil be used.")*1000 #W
fig = st_plot.plot_load_profiles_aeneas(loads, 350, limit)
hcols[1].altair_chart(fig, use_container_width=True)

if run:
    for i in placeholders: i.empty()
    with st.spinner("Calculation in progress..."):
        st.toast("Calculating monotype HE solution...", icon="⌛")
        dict_mono_HE = monotype.monotype2(loads=loads, cell=cell_HE, V_bus=V_bus, cycles=cycles if bool_aging else [0]*len(loads))
        st.toast(f"[{dict_mono_HE['time']/1000:,.2f}s] Monotype HE solution found!", icon="✅")

        st.toast("Calculating monotype HP solution...", icon="⌛")
        dict_mono_HP = monotype.monotype2(loads=loads, cell=cell_HP, V_bus=V_bus, cycles=cycles if bool_aging else [0]*len(loads))
        st.toast(f"[{dict_mono_HP['time']/1000:,.2f}s] Monotype HP solution found!", icon="✅")

        st.toast("Calculating AENEAS solution...", icon="⌛")
        dict_aeneas = aeneas.aeneas_opti(loads=loads, cell_HE=cell_HE, cell_HP=cell_HP, V_bus=V_bus, cycles=cycles if bool_aging else [0]*len(loads), limit=limit, dict_initial=None)
        st.toast(f"[{dict_aeneas['time']/1000:,.2f}s] AENEAS solution found!", icon="✅")

        st.toast("Calculating AENEAS 2 solution...", icon="⌛")
        dict_aeneas_energy = aeneas.aeneas_opti_energy(loads=loads, cell_HE=cell_HE, cell_HP=cell_HP, V_bus=V_bus, cycles=cycles if bool_aging else [0]*len(loads), limit=limit, dict_initial=dict_aeneas)
        st.toast(f"[{dict_aeneas['time']/1000:,.2f}s] AENEAS 2 solution found!", icon="✅")

        st.toast("Calculating AENEAS 2 solution...", icon="⌛")
        dict_aeneas_HP = aeneas.aeneas_opti_HP(loads=loads, cell_HE=cell_HE, cell_HP=cell_HP, V_bus=V_bus, cycles=cycles if bool_aging else [0]*len(loads), limit=limit, dict_initial=dict_aeneas)
        st.toast(f"[{dict_aeneas['time']/1000:,.2f}s] AENEAS 2 solution found!", icon="✅")

        # st.toast("Calculating rule-based hybrid solution...", icon="⌛")
        # dict_tresh_0 = treshold.treshold(loads=loads, cell_HE=cell_HE, cell_HP=cell_HP, V_bus=V_bus, cycles=cycles if bool_aging else [0]*len(loads))
        # if (dict_tresh_0['N_HE'] != 0 and dict_tresh_0['N_HP'] != 0):
        #     dict_tresh = treshold.treshold_opti(loads=loads, cell_HE=cell_HE, cell_HP=cell_HP, V_bus=V_bus, cycles=cycles if bool_aging else [0]*len(loads), dict_initial=dict_tresh_0)
        #     st.toast(f"[{dict_tresh['time']/1000:,.2f}s] Rule-based hybrid solution found!", icon="✅")

        #     st.toast("Calculating optimal hybrid solution...", icon="⌛")
        #     dict_opti = optimal.optimal_aging(loads, cell_HE, cell_HP, V_bus, cycles=cycles if bool_aging else [0]*len(loads), bool_intercharge=False, dict_initial=dict_tresh)
        #     st.toast(f"[{dict_opti['time']/1000:,.2f}s] Optimal hybrid solution found!", icon="✅")

        #     if bool_charge:
        #         st.toast("Calculating optimal hybrid solution with intercharging...", icon="⌛")
        #         dict_opti2 = optimal.optimal_aging(loads, cell_HE, cell_HP, V_bus, cycles=cycles if bool_aging else [0]*len(loads), bool_intercharge=True, dict_initial=dict_tresh)
        #         st.toast(f"[{dict_opti2['time']/1000:,.2f}s] Optimal hybrid solution with intercharging found!", icon="✅")
        # else:
        #     dict_tresh = dict_mono_HE if dict_mono_HE["cost"] < dict_mono_HP["cost"] else dict_mono_HP
        #     dict_opti = dict_mono_HE if dict_mono_HE["cost"] < dict_mono_HP["cost"] else dict_mono_HP
        #     if bool_charge:
        #         dict_opti2 = dict_mono_HE if dict_mono_HE["cost"] < dict_mono_HP["cost"] else dict_mono_HP
            

        #time_tot = dict_mono_HE['time'] + dict_mono_HP['time'] + dict_tresh['time'] + dict_opti['time'] + dict_opti2['time'] if bool_charge else dict_mono_HE['time'] + dict_mono_HP['time'] + dict_tresh['time'] + dict_opti['time']
        #st.toast(f"All results found in **{time_tot/1000:.2f}s**!", icon="✅")


        cols = tabs[1].columns(5, gap="large")
        cols[0].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Monotype HE</div>", unsafe_allow_html=True)
        cols[0].write("")
        df = pd.DataFrame({
            'Configuration': ["High Energy", "High Power"],
            'Values': [f"{int(dict_mono_HE['M_HE'])} series, {int(dict_mono_HE['N_HE'])} parallel",
                       f"{int(dict_mono_HE['M_HP'])} series, {int(dict_mono_HE['N_HP'])} parallel"]
                       }).set_index('Configuration')
        cols[0].dataframe(df, use_container_width=True)
        cols[0].altair_chart(st_plot.plot_powers(dict_mono_HE), use_container_width=True)
        cols[0].download_button(label="Download power data as csv", data=st_plot.get_power_csv(dict_mono_HE), file_name="opti_battery_loads.csv", mime="text/csv", use_container_width=True)
        cols[0].altair_chart(st_plot.plot_SOC(dict_mono_HE), use_container_width=True)
        cols[0].altair_chart(st_plot.plot_V(dict_mono_HE), use_container_width=True)
        cols[0].altair_chart(st_plot.plot_I(dict_mono_HE), use_container_width=True)
        cols[0].altair_chart(st_plot.plot_joule(dict_mono_HE), use_container_width=True)
        cols[0].altair_chart(st_plot.plot_I_SC(dict_mono_HE), use_container_width=True)
        cols[0].download_button(label="Download power data as csv", data=st_plot.get_SC_current_csv(dict_mono_HE), file_name="opti_battery_cap_current.csv", mime="text/csv", use_container_width=True)
        
        cols[1].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Monotype HP</div>", unsafe_allow_html=True)
        cols[1].write("")
        df = pd.DataFrame({
            'Configuration': ["High Energy", "High Power"],
            'Values': [f"{int(dict_mono_HP['M_HE'])} series, {int(dict_mono_HP['N_HE'])} parallel",
                       f"{int(dict_mono_HP['M_HP'])} series, {int(dict_mono_HP['N_HP'])} parallel"]
                       }).set_index('Configuration')
        cols[1].dataframe(df, use_container_width=True)
        cols[1].altair_chart(st_plot.plot_powers(dict_mono_HP), use_container_width=True)
        cols[1].download_button(label="Download power data as csv", data=st_plot.get_power_csv(dict_mono_HP), file_name="opti_supercaps_loads.csv", mime="text/csv", use_container_width=True)
        cols[1].altair_chart(st_plot.plot_SOC(dict_mono_HP), use_container_width=True)
        cols[1].altair_chart(st_plot.plot_V(dict_mono_HP), use_container_width=True)
        cols[1].altair_chart(st_plot.plot_I(dict_mono_HP), use_container_width=True)
        cols[1].altair_chart(st_plot.plot_joule(dict_mono_HP), use_container_width=True)
        cols[1].altair_chart(st_plot.plot_I_SC(dict_mono_HP), use_container_width=True)
        cols[1].download_button(label="Download power data as csv", data=st_plot.get_SC_current_csv(dict_mono_HP), file_name="opti_supercaps_cap_current.csv", mime="text/csv", use_container_width=True)
        

        cols[2].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>No intercharging</div>", unsafe_allow_html=True)
        cols[2].write("")
        df = pd.DataFrame({
            'Configuration': ["High Energy", "High Power"],
            'Values': [f"{int(dict_aeneas['M_HE'])} series, {int(dict_aeneas['N_HE'])} parallel",
                       f"{int(dict_aeneas['M_HP'])} series, {int(dict_aeneas['N_HP'])} parallel"]
                       }).set_index('Configuration')
        cols[2].dataframe(df, use_container_width=True)
        cols[2].altair_chart(st_plot.plot_powers(dict_aeneas), use_container_width=True)
        cols[2].download_button(label="Download power data as csv", data=st_plot.get_power_csv(dict_aeneas), file_name="opti_positive_loads.csv", mime="text/csv", use_container_width=True)
        cols[2].altair_chart(st_plot.plot_SOC(dict_aeneas), use_container_width=True)
        cols[2].altair_chart(st_plot.plot_V(dict_aeneas), use_container_width=True)
        cols[2].altair_chart(st_plot.plot_I(dict_aeneas), use_container_width=True)
        cols[2].altair_chart(st_plot.plot_joule(dict_aeneas), use_container_width=True)
        cols[2].altair_chart(st_plot.plot_I_SC(dict_aeneas), use_container_width=True)
        cols[2].download_button(label="Download power data as csv", data=st_plot.get_SC_current_csv(dict_aeneas), file_name="opti_positive_cap_current.csv", mime="text/csv", use_container_width=True)


        cols[3].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Minimize Total Energy</div>", unsafe_allow_html=True)
        cols[3].write("")
        df = pd.DataFrame({
            'Configuration': ["High Energy", "High Power"],
            'Values': [f"{int(dict_aeneas_energy['M_HE'])} series, {int(dict_aeneas_energy['N_HE'])} parallel",
                       f"{int(dict_aeneas_energy['M_HP'])} series, {int(dict_aeneas_energy['N_HP'])} parallel"]
                       }).set_index('Configuration')
        cols[3].dataframe(df, use_container_width=True)
        cols[3].altair_chart(st_plot.plot_powers(dict_aeneas_energy), use_container_width=True)
        cols[3].download_button(label="Download power data as csv", data=st_plot.get_power_csv(dict_aeneas_energy), file_name="opti_energy_loads.csv", mime="text/csv", use_container_width=True)
        cols[3].altair_chart(st_plot.plot_SOC(dict_aeneas_energy), use_container_width=True)
        cols[3].altair_chart(st_plot.plot_V(dict_aeneas_energy), use_container_width=True)
        cols[3].altair_chart(st_plot.plot_I(dict_aeneas_energy), use_container_width=True)
        cols[3].altair_chart(st_plot.plot_joule(dict_aeneas_energy), use_container_width=True)
        cols[3].altair_chart(st_plot.plot_I_SC(dict_aeneas_energy), use_container_width=True)
        cols[3].download_button(label="Download power data as csv", data=st_plot.get_SC_current_csv(dict_aeneas_energy), file_name="opti_energy_cap_current.csv", mime="text/csv", use_container_width=True)


        cols[4].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Minimize Total C-Rate</div>", unsafe_allow_html=True)
        cols[4].write("")
        df = pd.DataFrame({
            'Configuration': ["High Energy", "High Power"],
            'Values': [f"{int(dict_aeneas_HP['M_HE'])} series, {int(dict_aeneas_HP['N_HE'])} parallel",
                       f"{int(dict_aeneas_HP['M_HP'])} series, {int(dict_aeneas_HP['N_HP'])} parallel"]
                       }).set_index('Configuration')
        
        cols[4].dataframe(df, use_container_width=True)
        cols[4].altair_chart(st_plot.plot_powers(dict_aeneas_HP), use_container_width=True)
        cols[4].download_button(label="Download power data as csv", data=st_plot.get_power_csv(dict_aeneas_HP), file_name="opti_power_loads.csv", mime="text/csv", use_container_width=True)
        cols[4].altair_chart(st_plot.plot_SOC(dict_aeneas_HP), use_container_width=True)
        cols[4].altair_chart(st_plot.plot_V(dict_aeneas_HP), use_container_width=True)
        cols[4].altair_chart(st_plot.plot_I(dict_aeneas_HP), use_container_width=True)
        cols[4].altair_chart(st_plot.plot_joule(dict_aeneas_HP), use_container_width=True)
        cols[4].altair_chart(st_plot.plot_I_SC(dict_aeneas_HP), use_container_width=True)
        cols[4].download_button(label="Download capacitor current as csv", data=st_plot.get_SC_current_csv(dict_aeneas_HP), file_name="opti_power_cap_current.csv", mime="text/csv", use_container_width=True)



        quit()

        cols = tabs[1].columns(4 if bool_charge else 3, gap="medium")
        dict = dict_mono_HE if dict_mono_HE["cost"] < dict_mono_HP["cost"] else dict_mono_HP
        cols[0].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Monotype</div>", unsafe_allow_html=True)
        cols[0].warning(f"Configuration HE: {int(dict['M_HE'])} series, {int(dict['N_HE'])} parallel")
        cols[0].warning(f"Configuration HP: {int(dict['M_HP'])} series, {int(dict['N_HP'])} parallel")
        cols[0].warning(f"Total cost: € {dict['cost']:,.2f}")
        cols[0].write("")
        cols[0].altair_chart(st_plot.plot_powers(dict_mono_HE if dict_mono_HE["cost"] < dict_mono_HP["cost"] else dict_mono_HP), use_container_width=True)
        cols[0].altair_chart(st_plot.plot_SOC(dict_mono_HE if dict_mono_HE["cost"] < dict_mono_HP["cost"] else dict_mono_HP), use_container_width=True)

        cols[1].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Rule-Based Hybrid</div>", unsafe_allow_html=True)
        cols[1].warning(f"Configuration HE: {int(dict_tresh['M_HE'])} series, {int(dict_tresh['N_HE'])} parallel")
        cols[1].warning(f"Configuration HP: {int(dict_tresh['M_HP'])} series, {int(dict_tresh['N_HP'])} parallel")
        cols[1].warning(f"Total cost: € {dict_tresh['cost']:,.2f}")
        cols[1].write("")
        cols[1].altair_chart(st_plot.plot_powers(dict_tresh), use_container_width=True)
        cols[1].altair_chart(st_plot.plot_SOC(dict_tresh), use_container_width=True)

        cols[2].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Optimal Hybrid</div>", unsafe_allow_html=True)
        cols[2].warning(f"Configuration HE: {int(dict_opti['M_HE'])} series, {int(dict_opti['N_HE'])} parallel")
        cols[2].warning(f"Configuration HP: {int(dict_opti['M_HP'])} series, {int(dict_opti['N_HP'])} parallel")
        cols[2].warning(f"Total cost: € {dict_opti['cost']:,.2f}")
        cols[2].write("")
        cols[2].altair_chart(st_plot.plot_powers(dict_opti), use_container_width=True)
        cols[2].altair_chart(st_plot.plot_SOC(dict_opti), use_container_width=True)
        

        if bool_charge:
            cols[3].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Optimal Hybrid w/ Intercharging</div>", unsafe_allow_html=True)
            cols[2].warning(f"Configuration HE: {int(dict_opti2['M_HE'])} series, {int(dict_opti2['N_HE'])} parallel")
            cols[2].warning(f"Configuration HP: {int(dict_opti2['M_HP'])} series, {int(dict_opti2['N_HP'])} parallel")
            cols[2].warning(f"Total cost: € {dict_opti2['cost']:,.2f}")
            cols[3].write("")
            cols[3].altair_chart(st_plot.plot_powers(dict_opti2), use_container_width=True)
            cols[3].altair_chart(st_plot.plot_SOC(dict_opti2), use_container_width=True)

        

        cols = tabs[2].columns(4 if bool_charge else 3, gap="medium")

        cols[0].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Monotype</div>", unsafe_allow_html=True)
        cols[0].write("")
        cols[0].metric("Total Cost", value=f"€ {min(dict_mono_HE['cost'], dict_mono_HP['cost']):,.2f}")

        cols[1].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Rule-Based Hybrid</div>", unsafe_allow_html=True)
        cols[1].write("")
        cols[1].metric("Total Cost", value=f"€ {dict_tresh['cost']:,.2f}")

        cols[2].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Optimal Hybrid</div>", unsafe_allow_html=True)
        cols[2].write("")
        cols[2].metric("Total Cost", value=f"€ {dict_opti['cost']:,.2f}")

        if bool_charge:
            cols[3].markdown(f"<div style='border: 4px solid {hex_color[0]}; padding: 8px; text-align: center; font-weight: bold; color: {hex_color[0]}; border-radius: 10px;'>Optimal Hybrid w/ Intercharging</div>", unsafe_allow_html=True)
            cols[3].write("")
            cols[3].metric("Total Cost", value=f"€ {dict_opti2['cost']:,.2f}")


