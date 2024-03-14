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

list_fluids = {
    'SEAT': {
        'Temp' : 124,
        'Psat' : 526.0681617,
        'Pres' : 694.0709747,
        'Pressure': [2.087852321,44.28194515,142.7348284,269.3171069,424.0287806,526.0681617,529.5140127,536.5463615,550.892353,565.3789916,579.3030422,600.3297651,635.5618326,670.4422827,694.0709747,705.6040267,775.6462208,845.9697089],
        'Bo': [1.097,1.202,1.317,1.473,1.791,2.279,2.276,2.274442,2.265326,2.25621,2.249373,2.235699,2.217467,2.199235,2.18784,2.185561,2.153655,2.126307],
        'Rs': [0,29.21,73.93,130.75,251.89,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96]
    },
    'ARAM': {
        'Temp' : 121,
        'Psat' : 700,
        'Pres' : 900,
        'Pressure': [5,700,900],
        'Bo': [1.1,1.8,1.6],
        'Rs': [300,500,500]
    }
}

def normalize_fluid(analogue,temp,pres,psat,bo,tipo):
    pressure_i1 = [list_fluids[analogue]['Pressure'][0] + (psat - list_fluids[analogue]['Pressure'][0])*(Px - list_fluids[analogue]['Pressure'][0])/(list_fluids[analogue]['Psat']-list_fluids[analogue]['Pressure'][0]) for Px in list_fluids[analogue]['Pressure'] if Px <= list_fluids[analogue]['Psat']]
    pressure_i2 = [psat+ (pres - psat)*(Px - list_fluids[analogue]['Psat'])/(list_fluids[analogue]['Pres']-list_fluids[analogue]['Psat']) for Px in list_fluids[analogue]['Pressure'] if Px > list_fluids[analogue]['Psat']]
    pressure_i = pressure_i1 + pressure_i2
 
    bo_i0 = list_fluids[analogue]['Bo'][0]*(1 + (temp - list_fluids[analogue]['Temp'])*0.04/35)
    if tipo == "Saturation Pressure":
        fator_Bo = (bo-bo_i0)/(list_fluids[analogue]['Bo'][list_fluids[analogue]['Pressure'].index(list_fluids[analogue]['Psat'])]-bo_i0)
    else:
        fator_Bo = (bo-bo_i0)/(list_fluids[analogue]['Bo'][list_fluids[analogue]['Pressure'].index(list_fluids[analogue]['Pres'])]-bo_i0)
    
    bo_i = [bo_i0+(Bx-bo_i0)*fator_Bo for Bx in list_fluids[analogue]['Bo']]
    return(pressure_i,bo_i)

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
            voip_dist = st.selectbox('VOIP distribution',options=['Normal','Uniform','Triangular','Lognormal'])
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
                elif voip_dist == 'Lognormal':              ploto = sns.kdeplot(np.e**(np.random.normal(np.log(voip_mean),(np.log(voip[1])-np.log(voip[0]))/6,nsamples)), fill=True)
                elif voip_dist == 'Triangular':             ploto = sns.kdeplot(np.random.triangular(voip[0], voip_mean, voip[1], nsamples), fill=True)
                else:                                       ploto = sns.kdeplot(np.random.uniform(voip[0],voip[1], nsamples), fill=True)
                ploto.set_xlabel("VOIP")
                st.pyplot(ploto.figure, clear_figure=True)
            else:
                if voip_dist == 'Normal':                   plotg = sns.kdeplot(np.random.normal(vgip_mean,vgip_stdev,nsamples), fill=True)
                elif voip_dist == 'Lognormal':              plotg = sns.kdeplot(np.e**(np.random.normal(np.log(vgip_mean),(np.log(vgip[1])-np.log(vgip[0]))/6,nsamples)), fill=True)
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
    list_analogues = ["SEAT","ARAM"]
    with col1:
        nfluids = st.number_input('How many Fluids?',1,3,1)
        fluids = [f+1 for f in range(nfluids)]
        st.divider()
        fluid_prob = [st.number_input(f"Probability/weight of fluid {i+1}", 1,100,1, help=help_strings['norm']) for i in range(nfluids)]
        st.divider()
        
        fluid_prob = fluid_prob/np.sum(fluid_prob)

    with col2:
        plotf = sns.barplot(x=fluids, y=fluid_prob, hue=fluids, palette='tab10')
        plotf.set_xlabel('Fluid')
        plotf.set_ylabel('Probability')
        st.pyplot(plotf.figure, clear_figure=True)

    st.divider()  

    col3,col4 = st.columns(2)
    with col3:
        fluid_input = st.radio(f'Fluid 1 selection:',['Analogue','Input File'], horizontal=True)
        if fluid_input == "Input File":
            fluid_files = st.file_uploader(f"PVT file (fluid 1)", help=help_strings['pvt'])
        else:
            selected_analogue1 = st.selectbox(f'Select Analogue Fluid 1', list_analogues, key = 1)
            Temp_ref = st.number_input('Temp (ºC)',15,200,80, key = 2)
            Pres_ref = st.number_input('Pres (kgf/cm²)',200,1000,500, key = 3)
            Psat_ref = st.number_input('Psat (kgf/cm²)',150,800,350, key = 4)
            pres_type = st.radio('Reference Pressure for Analogue Properties:',['Saturation Pressure','Reservoir Pressure'], horizontal=True, key = 9)
            Bo_ref = st.number_input('Bo (m³/m³)',1.,3.,1.7,step=1.,format="%.2f", key = 5)
            Rs_ref = st.number_input('Rs (m³/m³)',50,8000,350, key = 6)

            pressures,bos = normalize_fluid(selected_analogue1,Temp_ref,Pres_ref,Psat_ref,Bo_ref,pres_type)
    with col4:
        fig, axs = plt.subplots(ncols=1,nrows=1) 
        i = 0
        if fluid_input == "Input File":
            pass
        else:             
            axs.plot(list_fluids[selected_analogue1]['Pressure'],list_fluids[selected_analogue1]['Bo'],'b-',label='Original')
            axs.plot(pressures,bos,'r-',label='Analogue Fluid')
            st.pyplot(fig.figure, clear_figure=True)

    st.divider() 

    if nfluids > 1:
        col5,col6 = st.columns(2)
        with col5:
            fluid_input = st.radio(f'Fluid 2 selection:',['Analogue','Input File'], horizontal=True)
            if fluid_input == "Input File":
                fluid_files = st.file_uploader(f"PVT file (fluid 2)", help=help_strings['pvt'])
            else:
                selected_analogue2 = st.selectbox(f'Select Analogue Fluid 2', list_analogues, key = 10)
                Temp_ref = st.number_input('Temp (ºC)',15,200,80, key = 11)
                Pres_ref = st.number_input('Pres (kgf/cm²)',200,1000,500, key = 12)
                Psat_ref = st.number_input('Psat (kgf/cm²)',150,800,350, key = 13)
                pres_type = st.radio('Reference Pressure for Analogue Properties:',['Saturation Pressure','Reservoir Pressure'], horizontal=True, key = 19)
                Bo_ref = st.number_input('Bo (m³/m³)',1.,3.,1.7,step=1.,format="%.2f", key = 14)
                Rs_ref = st.number_input('Rs (m³/m³)',50,8000,350, key = 15)

                pressures,bos = normalize_fluid(selected_analogue2,Temp_ref,Pres_ref,Psat_ref,Bo_ref,pres_type)
        with col6:
            fig, axs = plt.subplots(ncols=1,nrows=1) 
            i = 0
            if fluid_input == "Input File":
                pass
            else:             
                axs.plot(list_fluids[selected_analogue2]['Pressure'],list_fluids[selected_analogue2]['Bo'],'b-',label='Original')
                axs.plot(pressures,bos,'r-',label='Analogue Fluid')
                st.pyplot(fig.figure, clear_figure=True)

        st.divider() 

    if nfluids > 2:
        col7,col8 = st.columns(2)
        with col7:
            fluid_input = st.radio(f'Fluid 3 selection:',['Analogue','Input File'], horizontal=True)
            if fluid_input == "Input File":
                fluid_files = st.file_uploader(f"PVT file (fluid 3)", help=help_strings['pvt'])
            else:
                selected_analogue3 = st.selectbox(f'Select Analogue Fluid 3', list_analogues, key = 20)
                Temp_ref = st.number_input('Temp (ºC)',15,200,80, key = 21)
                Pres_ref = st.number_input('Pres (kgf/cm²)',200,1000,500, key = 22)
                Psat_ref = st.number_input('Psat (kgf/cm²)',150,800,350, key = 23)
                pres_type = st.radio('Reference Pressure for Analogue Properties:',['Saturation Pressure','Reservoir Pressure'], horizontal=True, key = 29)
                Bo_ref = st.number_input('Bo (m³/m³)',1.,3.,1.7,step=1.,format="%.2f", key = 24)
                Rs_ref = st.number_input('Rs (m³/m³)',50,8000,350, key = 25)

                pressures,bos = normalize_fluid(selected_analogue3,Temp_ref,Pres_ref,Psat_ref,Bo_ref,pres_type)
        with col8:
            fig, axs = plt.subplots(ncols=1,nrows=1) 
            i = 0
            if fluid_input == "Input File":
                pass
            else:             
                axs.plot(list_fluids[selected_analogue3]['Pressure'],list_fluids[selected_analogue3]['Bo'],'b-',label='Original')
                axs.plot(pressures,bos,'r-',label='Analogue Fluid')
                st.pyplot(fig.figure, clear_figure=True)

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
