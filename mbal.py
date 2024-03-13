import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import requests

nsamples = 1000

help_strings = {
    'sliders': f'(min,max) = ($\mu-3\sigma,\mu+3\sigma$) if Normal',
    'rf': f'Initial guess on the recovery factor, to populate number of wells in experiments',
    'norm': f'Values will be always noramlized',
    'pvt': f'Please attach PVT file for this fluid',
}

list_mecanismos = {
    'Oil': ['Depleção', 'Injeção de Água', 'Injeção de Gás'],
    'Gas': ['Depleção'],
}

unitsOil = st.sidebar.radio('Oil Units:',['MMm³','MMBBL'], horizontal=True)
unitsGas = st.sidebar.radio('Gas Units:',['MMm³','TCF'], horizontal=True)

st.subheader('_Reservoir Potential evaluation_')

tabRes,tabFluid,tabVFP,tabSampling,tabSchedule,tabMBAL,tabMatBal,tabResults,tabHelp =  st.tabs([
    'Reservoir:mount_fuji:',
    'Fluid:oil_drum:',
    'VFP:chart_with_upwards_trend:',
    'Sampling:game_die:',
    'Schedule:calendar:',
    'MBAL:m:',
    'Spreadsheet:chart_with_downwards_trend:',
    'Results:signal_strength:',
    'Help:question:',
    ])

with tabRes:
    with st.expander('Reservoir Data'):
        st.subheader('Reservoir Data', divider='blue')
        col1, col2 = st.columns(2)
        with col1:
            resType = st.radio('Reservoir type:',['Oil','Gas'], horizontal=True)

            rf = st.number_input('Target RF (%)', 1, 100, 20, help=help_strings['rf'])
            selected_mecanisms = st.multiselect(f'Production Mechanism - {resType}', list_mecanismos[resType])

        with col2:
            voip_dist = st.selectbox('VOIP distribution',options=['Normal','Uniform','Triangular'])
            if resType == 'Oil':
                voip = st.slider('VOIP (MMBBL)', 0, 5000, (1000,3000), help=help_strings['sliders'])
                vgip = (0,0)
            else:
                vgip = st.slider('VGIP (MMm³)', 0, 5000, (1000,2000), help=help_strings['sliders'])
                voip = (0,0)
            voip_mean = np.mean(voip)
            voip_stdev = (voip[1]-voip[0])/6
            vgip_mean = np.mean(vgip)
            vgip_stdev = (vgip[1]-vgip[0])/6

            if resType == 'Oil':
                if voip_dist == 'Normal':                   ploto = sns.kdeplot(np.random.normal(voip_mean,voip_stdev,nsamples), fill=True)
                elif voip_dist == 'Lognormal':              ploto = sns.kdeplot(np.random.normal(np.log(voip_mean+(voip_stdev**2)/2),5,nsamples), fill=True)
                elif voip_dist == 'Triangular':             ploto = sns.kdeplot(np.random.triangular(voip[0], voip_mean, voip[1], nsamples), fill=True)
                else:                                       ploto = sns.kdeplot(np.random.uniform(voip[0],voip[1], nsamples), fill=True)
                ploto.set_xlabel("VOIP")
                st.pyplot(ploto.figure, clear_figure=True)
            else:
                if voip_dist == 'Normal':                   plotg = sns.kdeplot(np.random.normal(vgip_mean,vgip_stdev,nsamples), fill=True)
                elif voip_dist == 'Lognormal':              plotg = sns.kdeplot(np.random.normal(vgip_mean,vgip_stdev,nsamples), fill=True)
                elif voip_dist == 'Triangular':             plotg = sns.kdeplot(np.random.triangular(vgip[0],vgip_mean,vgip[1],nsamples), fill=True)
                else:                                       plotg = sns.kdeplot(np.random.uniform(vgip[0],vgip[1],nsamples), fill=True)
                plotg.set_xlabel("VGIP")
                st.pyplot(plotg.figure, clear_figure=True)

    with st.expander('Production Metrics'):
        st.subheader('Production Metrics', divider='blue')

        col3, col4 = st.columns(2)
        with col3:
            metric_dist = st.selectbox('Metrics parameter distribution',options=['Normal','Uniform','Triangular'])
            np_well = st.slider('Np/well:', 0, 100, (30,60), help=help_strings['sliders'])
            np_well_mean = np.mean(np_well)
            np_well_std = (np_well[1]-np_well[0])/6
            pi = st.slider('Productivity Index (m³/d/kgf/cm²):', 0, 200, (50,100), help=help_strings['sliders'])
            pi_mean = np.mean(pi)
            pi_std = (pi[1]-pi[0])/6

        with col4:
            if metric_dist == 'Normal':
                j = sns.jointplot(y=np.random.normal(np_well_mean, np_well_std, nsamples), x=np.random.normal(pi_mean, pi_std, nsamples), kind='hex', height=4)
            elif metric_dist == 'Lognormal':
                pass;
            elif metric_dist == 'Triangular':
                j = sns.jointplot(y=np.random.triangular(np_well[0],np_well_mean, np_well[1], nsamples), x=np.random.triangular(pi[0],pi_mean,pi[1], nsamples), kind='hex', height=4)
            else:
                j = sns.jointplot(y=np.random.uniform(np_well[0],np_well[1],nsamples), x=np.random.uniform(pi[0],pi[1],nsamples), kind='hex', height=4)
            j.figure.axes[0].set_xlabel('PI')
            j.figure.axes[0].set_ylabel('Np/well')
            j.figure.axes[0].set_xlim((0, 200))
            j.figure.axes[0].set_ylim((0, 100))
            st.pyplot(j.figure, clear_figure=True)

with tabFluid:
    col1, col2 = st.columns(2)
    with col1:
        nfluids = st.number_input('How many Fluids?',1,5,3)
        fluids = [f+1 for f in range(nfluids)]
        st.divider()
        fluid_prob = [st.number_input(f"Probability/weight of fluid {i+1}", 1,100,1, help=help_strings['norm']) for i in range(nfluids)]
        st.divider()
        fluid_files = [st.file_uploader(f"PVT file (fluid {i+1})", help=help_strings['pvt']) for i in range(nfluids)]
        fluid_prob = fluid_prob/np.sum(fluid_prob)

    with col2:
        plotf = sns.barplot(x=fluids, y=fluid_prob, hue=fluids, palette='tab10')
        plotf.set_xlabel('Fluid')
        plotf.set_ylabel('Probability')
        st.pyplot(plotf.figure, clear_figure=True)

with tabSampling:
    st.subheader('MBAL Runs', divider='blue')
    nruns = st.number_input('MBAL runs:', 10, None, 100, step=100)
    pi_dist = np.random.normal(pi_mean, pi_std, nruns)
    np_well_dist = np.random.normal(np_well_mean, np_well_std, nruns)
    fluid_dist = np.random.choice(fluids, size=nruns, p=fluid_prob)
    if resType=='Oil':
        vol = np.random.normal(np.mean(voip),(voip[1]-voip[0])/6,nruns)
    else:
        vol = np.random.normal(np.mean(vgip),(voip[1]-voip[0])/6,nruns)

    samples = pd.DataFrame(
        {
            'Vol':vol,
            'RF':rf*np.ones(nruns),
            'Np_Well':np_well_dist,
            'Pi':pi_dist,
            'Fluid':fluid_dist,
        },
        index=[i+1 for i in range(nruns)]
    )

    samples['Np'] = samples['Vol'] * rf/100
    samples['Wells'] = samples['Np']/samples['Np_Well']
    samples = samples.round(0)

    st.subheader('Experiments', divider='blue')
    st.write(samples)
    st.subheader('Stats', divider='blue')
    st.write(samples.describe().loc[['mean', '50%', 'std', 'min', 'max', 'count']].round(0))

with tabSchedule:
    d = st.date_input("Fisrt Oil", datetime.date(2034, 1, 1))
    interval = st.number_input('Interval between wells (days):', 0, None, None, step=30, help='teste help', placeholder='One new well every 90 days')

with tabMBAL:
    pass;
    # url = 'http://es00010252:2301/api/production/SatelliteOilLinearIPRWell/calculate'

    # for wct in ['0','10','20', '50', '95']:
    #     st.write('WCT=',wct)
    #     myobj = {
    #         "fluid_gor": ["300"],
    #         "fluid_api": ["22"],
    #         "gas_sg": ["0.7"],
    #         "gas_co2": ["0"],
    #         "gas_h2s": ["0"],
    #         "gas_n2": ["0"],
    #         "fluid_wct": [wct],
    #         "reservoir_pressure": ["350"],
    #         "reservoir_temperature": ["55"],
    #         "reservoir_depth": ["6000"],
    #         "well_pi": ["12"],
    #         "water_depth": ["1400"],
    #         "riser_length": ["2000"],
    #         "flowline_length": ["2000"],
    #         "riser_diameter": ["6"],
    #         "flowline_diameter": ["6"],
    #         "pipe_type": ["FLX"],
    #         "production_column_diameter": ["4.5"],
    #         "arrival_pressure": ["90"]
    #     }
    #     x = requests.post(url, json = myobj)
    #     st.write(x.text)


with tabMatBal:
    st.header("aqui vamos usar a planilha do Gusmão")

with tabResults:
    st.header("calma, estamos fazendo")

st.caption('Powered by DND :sunglasses:')
