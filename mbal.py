import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# plt.style.use('cyberpunk')
# plt.style.use('dark_background')
# sns.color_palette('coolwarm_r')


list_mecanismos = {
    'Oil': ['Depleção', 'Injeção de Água', 'Injeção de Gás'],
    'Gas': ['Depleção'],
}

resType = st.sidebar.radio('Reservoir type:',['Oil','Gas'], horizontal=True)
tabRes, tabSampling, tabMBAL, tabMatBal,  tabResults =  st.tabs(['Reservoir', 'Sampling', 'MBAL', 'MatBal Spreadsheet' 'Results'])
with tabRes:
    col1, col2 = st.columns(2)
    with col1:
        selected_mecanisms = st.multiselect(
            f'Mecanismo de Recuperação - {resType}', list_mecanismos[resType]
        )
    with col2:
        if resType == 'Oil':
            voip = st.slider('VOIP (MMBBL)', 0, 5000, 2000)
            vgip = 0
        else:
            vgip = st.slider('VGIP (MMm³)', 0, 5000, 100)
            voip = 0

    col3, col4 = st.columns(2)
    with col3:
        st.write('Np / poço')
        np_well_mean, np_well_std = st.slider('Média(MMBBL/poço)', 0, 200, 10), st.slider('Desvio Padrão(MMBBL/poço)', 0, 50, 5) # mean and standard deviation
    with col4:
        st.write('IP (m³/d/kgf/cm²)')
        pi_mean, pi_std = st.slider('Média', 0, 200, 10), st.slider('Desvio Padrão', 0, 50, 5) # mean and standard deviation
        fig2, ax2 = plt.subplots()
        ax2.set_ylabel('Np/poço')
        ax2.set_xlabel('IP')
        j = sns.jointplot(y=np.random.normal(np_well_mean, np_well_std, 1000), x=np.random.normal(pi_mean, pi_std, 1000),kind='hex')
        j.figure.axes[0].set_ylabel('Np/poço')
        j.figure.axes[1].set_ylabel('IP')
    st.pyplot(j.figure)


with tabSampling:
    st.header("opções de amostragem: montecarlo, hipercubo latino, numero de rodadas MBAL etc....., mostrar um tabelao pandas com os experimentos")
with tabMBAL:
    st.header("Acompanhamento das rodadas e parametrização do openserver")
with tabMatBal:
    st.header("aqui vamos usar a planilha do Gusmão")
with tabResults:
    st.header("calma, estamos fazendo")
