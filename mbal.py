import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

help_strings = {
    'sliders': f'(min,max) = ($\mu-3\sigma,\mu+3\sigma$)',
    'rf': f'Initial guess on the recovery factor, to populate number of wells in experiments',
}

list_mecanismos = {
    'Oil': ['Depleção', 'Injeção de Água', 'Injeção de Gás'],
    'Gas': ['Depleção'],
}

unitsOil = st.sidebar.radio('Oil Units:',['MMm³','MMBBL'], horizontal=True)
unitsGas = st.sidebar.radio('Gas Units:',['MMm³','TCF'], horizontal=True)

tabRes, tabFluid, tabVFP, tabSampling, tabMBAL, tabMatBal,  tabResults =  st.tabs(['Reservoir', 'Fluid', 'VFP', 'Sampling', 'MBAL', 'MatBal Spreadsheet', 'Results'])
with tabRes:

    col1, col2 = st.columns(2)
    with col1:
        resType = st.radio('Reservoir type:',['Oil','Gas'], horizontal=True)
        if resType == 'Oil':
            voip = st.slider('VOIP (MMBBL)', 0, 5000, (1000,3000), help=help_strings['sliders'])
            vgip = 0
        else:
            vgip = st.slider('VGIP (MMm³)', 0, 5000, (1000,2000), help=help_strings['sliders'])
            voip = 0
        rf = st.number_input('Target RF (%)', 10, 50, 20, help=help_strings['rf'])
        selected_mecanisms = st.multiselect(f'Production Mechanism - {resType}', list_mecanismos[resType])
    with col2:
        if resType == 'Oil':
            ploto = sns.kdeplot(np.random.normal(np.mean(voip),(voip[1]-voip[0])/6,1000), fill=True)
            ploto.set_xlabel("VOIP")
            st.pyplot(ploto.figure)
        else:
            plotg=sns.kdeplot(np.random.normal(np.mean(vgip),(vgip[1]-vgip[0])/6,1000), fill=True)
            plotg.set_xlabel("VGIP")
            st.pyplot(plotg.figure)


    st.divider()

    col3, col4 = st.columns(2)
    with col3:
        np_well = st.slider('Np/well:', 0, 100, (30,60), help=help_strings['sliders'])
        np_well_mean = np.mean(np_well)
        np_well_std = (np_well[1]-np_well[0])/6
        pi = st.slider('Productivity Index (m³/d/kgf/cm²):', 0, 200, (50,100), help=help_strings['sliders'])
        pi_mean = np.mean(pi)
        pi_std = (pi[1]-pi[0])/6
    with col4:
        j = sns.jointplot(y=np.random.normal(np_well_mean, np_well_std, 1000), x=np.random.normal(pi_mean, pi_std, 1000), kind='hex', height=4)
        j.figure.axes[0].set_xlabel('PI')
        j.figure.axes[0].set_ylabel('Np/well')
        j.figure.axes[0].set_xlim((0, 200))
        j.figure.axes[0].set_ylim((0, 100))
        st.pyplot(j.figure)


with tabSampling:
    st.header("opções de amostragem: montecarlo, hipercubo latino, numero de rodadas MBAL etc....., mostrar um tabelao pandas com os experimentos")
with tabMBAL:
    st.header("Acompanhamento das rodadas e parametrização do openserver")
with tabMatBal:
    st.header("aqui vamos usar a planilha do Gusmão")
with tabResults:
    st.header("calma, estamos fazendo")
