import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import seaborn as sns
import datetime
import requests
from stqdm import stqdm
import h5py
import os
import openserver as openserver
import json

analogsModels = {
    'SGT_BASE':'L:/res/santos/presal_pre_projetos/Sagitario/ER/3_Modelo_de_Simulacao/V3A/RUNS/GRID_V3A/SGT_GRID_V3A_Caso20_0906_SPILL_AJGEO_5P4IW_LIFT_R8_UEP120.sr3',
    'SGT_PESS':'L:/res/santos/presal_pre_projetos/Sagitario/ER/3_Modelo_de_Simulacao/V3A/RUNS/GRID_V3A/SGT_GRID_V3A_Caso11_Ajus09set21_INTERMED_AJGEO_malha3_InjWAG_crono_ap.sr3',
    'SGT_OTIM':'L:/res/santos/presal_pre_projetos/Sagitario/ER/3_Modelo_de_Simulacao/V3A/RUNS/GRID_V3A/SGT_GRID_V3A_Caso23_INTERMED_AJGEO_17ago21_v3A_malha1_hphiso_InjA_500_s98ig_iw4iw6iw8_ap.sr3',
    'ORION_OTIM':'L:/res/santos/presal_pre_projetos/SW_Sagitario/ER/3_Modelo_de_Simulacao/RUNS/Versao_fev2022/OTIM_INT_EMI_SW_SGT_VFP17KM_malha6_2032_uep225.sr3',
    'URTIGA_6600':'L:/res/santos/presal_pre_projetos/SW_Sagitario/ER/3_Modelo_de_Simulacao/RUNS/Urtiga/Urtiga_fluido_Carcara_mar2022_refpres_COA6600_vfps6ID_09.sr3',
    'URTIGA_6650':'L:/res/santos/presal_pre_projetos/SW_Sagitario/ER/3_Modelo_de_Simulacao/RUNS/Urtiga/Urtiga_fluido_Carcara_mar2022_refpres_COA6650_6pol_120kbpd_5P_3IA.sr3',
    'URTIGA_6700':'L:/res/santos/presal_pre_projetos/SW_Sagitario/ER/3_Modelo_de_Simulacao/RUNS/Urtiga/Urtiga_fluido_Carcara_mar2022_refpres_COA6700_6pol_120kbpd_2injSUL_7P5IA_vf.sr3',
    'ARAM_V1_BASE':'L:/res/santos/presal_pre_projetos/Aram/ER/Modelo_de_Simulacao/2022_POS_POCO/1525_ARAM_KOTIM_6450_FCARC_SWO_RC2_KMIN_9P6IW.sr3',
    'ARAM_V1_PESS':'L:/res/santos/presal_pre_projetos/Aram/ER/Modelo_de_Simulacao/2022_POS_POCO/1525_ARAM_KOTIM_6450_FCARC_SWO_RC1_KMIN_5P4IW.sr3',
    'ARAM_V2.1_BASE':'L:/res/santos/presal_pre_projetos/Aram/ER/Modelo_de_Simulacao/2022_V2/RUNS_BASE_109EXPEDITO/Cenario_B_SET32_FVMtortuga_vfinal.sr3',
    'ARAM_V2.2_BASE':'L:/res/santos/presal_pre_projetos/Aram/ER/Modelo_de_Simulacao/2022_V2/RUNS_BASE_109/Testes_Malha/CenarioA2_pos109_05dez23B_09P6I_v1c_trigger_PROD-INJv2_BHP440mxc_A2B_BHP_500.sr3',
    'ARAM_PREPOCO_PESS':'L:/res/santos/presal_pre_projetos/Aram/ER/Modelo_de_Simulacao/2020_PIONEIRO/0721_ARAM_GPSM_6375_CMDR_FCARC_5.2IG_RINJ6_POST.sr3',
    'ARAM_PREPOCO_BASE':'L:/res/santos/presal_pre_projetos/Aram/ER/Modelo_de_Simulacao/2020_PIONEIRO/1525_ARAM_GMDR_6375_CPSM_FCARC_10.7IW_PROD1000.sr3',
    'ARAM_PREPOCO_OTIM':'L:/res/santos/presal_pre_projetos/Aram/ER/Modelo_de_Simulacao/2020_PIONEIRO/1444_ARAM_GMDR_6700_CPSM_FSGT_8.5IW_9.7IW_8.6IW_PROD1000.sr3',
    'UIR_ARAUCARIA':'L:/res/santos/presal_pre_projetos/Uirapuru/ER/3_Modelo_de_Simulacao/RUNS/MODELO_BU2E/UIR_EXPORT_3P2IA_SEMCDEPTH_CSP_ARA.sr3',
    'UIR_PINHAO':'L:/res/santos/presal_pre_projetos/Uirapuru/ER/3_Modelo_de_Simulacao/RUNS/MODELO_BU2E/UIR_EXPORT_4P4IW_SEMCDEPTH_CSP_PIN.sr3'
}

help_strings = {
    'sliders': f'(min,max) = ($\mu-3\sigma,\mu+3\sigma$) if Normal',
    'rf': f'Initial guess on the recovery factor, to populate number of wells in experiments',
    'norm': f'Values will be always noramlized',
    'pvt': f'Please attach PVT file for this fluid',
    'krel': f'Please attach SWT tables',
    'krel_consistency': f'If you select this option all ranges will be defined based only on "Swi" to ensure consistency with original selected anaogue',
    'mbal_base_file': 'Select mbal file to start with',
    'def_const': 'Keep unchecked if you wish to keep the constraints in the reference MBAL file',
    'nprod': 'If you keep this option unchecked, well number will be estimated based on the capcities and rates defined above'
}

list_mecanismos = {
    'Oil': ['Depleção', 'Injeção de Água', 'Injeção de Gás'],
    'Gas': ['Depleção'],
}

fluid_input_options = ['Analogue','Correlation','Input File']
groupBy_options = ['Modelo','Res']

list_fluids = {
    'SEAT': {
        'Temp' : 124,
        'Psat' : 526.0681617,
        'Pres' : 694.0709747,
        'Pressure': [2.087852321,44.28194515,142.7348284,269.3171069,424.0287806,526.0681617,529.5140127,536.5463615,550.892353,565.3789916,579.3030422,600.3297651,635.5618326,670.4422827,694.0709747,705.6040267,775.6462208,845.9697089],
        'Bo': [1.097,1.202,1.317,1.473,1.791,2.279,2.276,2.274442,2.265326,2.25621,2.249373,2.235699,2.217467,2.199235,2.18784,2.185561,2.153655,2.126307],
        'Rs': [0,29.21,73.93,130.75,251.89,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96,423.96],
        'Visc': [2.07,0.8,0.7,0.54,0.4,0.23,0.231,0.234,0.24,0.245,0.251,0.26,0.265,0.272,0.278,0.281,0.29,0.31]
    },
    'ARAM': {
        'Temp' : 121,
        'Psat' : 444.73323,
        'Pres' : 651.03323,
        'Pressure': [1.03323,46.03323,91.03323,141.03323,191.03323,241.03323,291.03323,341.03323,381.03323,421.03323,444.73323,501.03323,551.03323,601.03323,651.03323],
        'Bo': [1.0848,1.2353,1.3024,1.3727,1.4479,1.5318,1.6341,1.7382,1.9064,2.124,2.2069,2.1699,2.1421,2.118300001,2.0981],
        'Rs': [0,35.75,59.84,86.83,115.87,148.06,185.33,223.73,281.06,350.68,378.71,378.71,378.71,378.71,378.71],
        'Visc': [1.632,1.103,0.966,0.841,0.692,0.579,0.487,0.407,0.349,0.295,0.264,0.282,0.297,0.312,0.327]
    }
}

list_analogues = ["ARAM","SEAT"]

def normalize_fluid(analogue,temp,pres,psat,bo,rs,visc,tipo):
    pressure_i1 = [list_fluids[analogue]['Pressure'][0] + (psat - list_fluids[analogue]['Pressure'][0])*(Px - list_fluids[analogue]['Pressure'][0])/(list_fluids[analogue]['Psat']-list_fluids[analogue]['Pressure'][0]) for Px in list_fluids[analogue]['Pressure'] if Px <= list_fluids[analogue]['Psat']]
    pressure_i2 = [psat+ (pres - psat)*(Px - list_fluids[analogue]['Psat'])/(list_fluids[analogue]['Pres']-list_fluids[analogue]['Psat']) for Px in list_fluids[analogue]['Pressure'] if Px > list_fluids[analogue]['Psat']]
    pressure_i = pressure_i1 + pressure_i2


    index_psat = list_fluids[analogue]['Pressure'].index(list_fluids[analogue]['Psat'])
    index_pres = list_fluids[analogue]['Pressure'].index(list_fluids[analogue]['Pres'])
    bo_i0 = list_fluids[analogue]['Bo'][0]*(1 + (temp - list_fluids[analogue]['Temp'])*0.04/35)
    if tipo == "Saturation Pressure":
        fator_Bo = (bo-bo_i0)/(list_fluids[analogue]['Bo'][index_psat]-bo_i0)
        fator_Rs = rs/list_fluids[analogue]['Rs'][index_psat]
        fator_visc = visc/list_fluids[analogue]['Visc'][index_psat]
        visc_s = visc
    else:
        fator_Bo = (bo-bo_i0)*(list_fluids[analogue]['Pres']-list_fluids[analogue]['Psat'])/((list_fluids[analogue]['Bo'][index_pres]-list_fluids[analogue]['Bo'][index_psat])*(pres-psat)+(list_fluids[analogue]['Pres']-list_fluids[analogue]['Psat'])*(list_fluids[analogue]['Bo'][index_psat]-bo_i0))
        fator_Rs = rs/list_fluids[analogue]['Rs'][index_pres]
        visc_s = list_fluids[analogue]['Visc'][index_psat] + visc - list_fluids[analogue]['Visc'][index_pres]
        fator_visc = visc_s/list_fluids[analogue]['Visc'][index_psat]

    bo_i1 = [bo_i0+(Bx-bo_i0)*fator_Bo for Bx in list_fluids[analogue]['Bo'] if list_fluids[analogue]['Bo'].index(Bx) <= index_psat]
    bo_i2 = [bo_i1[-1]+(Bx-list_fluids[analogue]['Bo'][index_psat])*fator_Bo*(pres-psat)/(list_fluids[analogue]['Pres']-list_fluids[analogue]['Psat']) for Bx in list_fluids[analogue]['Bo'] if list_fluids[analogue]['Bo'].index(Bx) > index_psat]
    bo_i = bo_i1 + bo_i2
    rs_i = [Rx*fator_Rs for Rx in list_fluids[analogue]['Rs']]
    visc_i1 = [(Vx-list_fluids[analogue]['Visc'][index_psat])*fator_visc*(pressure_i[list_fluids[analogue]['Visc'].index(Vx)]-psat)/(list_fluids[analogue]['Pressure'][list_fluids[analogue]['Visc'].index(Vx)]-list_fluids[analogue]['Psat']) + visc_s for Vx in list_fluids[analogue]['Visc'] if list_fluids[analogue]['Visc'].index(Vx) < index_psat]
    visc_i2 = [Vx + visc_s - list_fluids[analogue]['Visc'][index_psat] for Vx in list_fluids[analogue]['Visc'] if list_fluids[analogue]['Visc'].index(Vx) >= index_psat ]
    visc_i = visc_i1 + visc_i2
    return(pressure_i,bo_i,rs_i,visc_i)

krel_input_options = ['Analogue','User Defined']

def calc_corey(kro,krw,swi,sor,no,nw):
    sw = np.linspace(swi,1-sor,25)
    swd = [(swx - swi)/((1 - sor) - swi) for swx in sw]
    kro_corey = [kro*((1-swx)**no) for swx in swd]
    krw_corey = [krw*(swx**nw) for swx in swd]

    return(sw,kro_corey,krw_corey)

@st.cache_data(max_entries=1)
def mbal_calc(samples,path):
    date_end = d.split("/")
    date_end[-1] = str(int(date_end[-1]) + delta_prod)
    date_end = '/'.join(date_end)
    myobj = {
        "volumes": samples['Vol'].tolist(),
        "path": path,
        "date_start":d,
        "date_end":date_end,
        "fpso_qo":0,
        "fpso_qg":0,
        "prod_qo":0,
        "prod_qg":0,
        "prod_bhp":0,
        "nprod":0,
        "krel_no": [],
        "krel_nw": [],
        "krel_kro": [],
        "krel_krw": [],
        "krel_swi": [],
        "krel_sor": []

    }
    if "KREL" in samples.columns:
        myobj = {
            "volumes": samples['Vol'].tolist(),
            "path": path,
            "date_start":d,
            "date_end":date_end,
            "fpso_qo":0,
            "fpso_qg":0,
            "prod_qo":0,
            "prod_qg":0,
            "prod_bhp":0,
            "nprod":0,
            "krel_no": samples['KREL_no'].tolist(),
            "krel_nw": samples['KREL_nw'].tolist(),
            "krel_kro": samples['KREL_kro'].tolist(),
            "krel_krw": samples['KREL_krw'].tolist(),
            "krel_swi": samples['KREL_swi'].tolist(),
            "krel_sor": samples['KREL_sor'].tolist()
    }
        
    if def_cons:
        myobj["fpso_qo"]=fpso_qo
        myobj["fpso_qg"]=fpso_qg*(10**6)
        myobj["prod_qo"]=prod_qo
        myobj["prod_qg"]=prod_qg*(10**6)
        myobj["prod_bhp"]=prod_bhp
        if def_cons_k > 0.5:
            myobj["nprod"]=prod_number
        elif resType == 'Oil':
            nwprod = round(fpso_qo/prod_qo+0.5,0)
            myobj["nprod"]=nwprod
        else:
            nwprod = round(fpso_qg/prod_qg+0.5,0)
            myobj["nprod"]=nwprod

    print(myobj["nprod"])
    x = requests.put("http://10.14.141.21:8600/mbal",json = myobj)

    return(x)

list_analogues_krel = ["SEAT","ACFC","Monai"]

list_krels = {
    'SEAT': {
        'kro' : 0.815,
        'krw' : 0.461,
        'swi' : 0.27,
        'sor': 0.365,
        'no': 4.717,
        'nw': 1.836
    },
    'ACFC': {
        'kro' : 0.84,
        'krw' : 0.47,
        'swi' : 0.19,
        'sor': 0.405,
        'no': 2.,
        'nw': 2.
    },
    'Monai': {
        'kro' : 1.0,
        'krw' : 0.4,
        'swi' : 0.245,
        'sor': 0.05,
        'no': 2.,
        'nw': 3.
    }
}

def define_samples(nruns):
    pi_dist = np.random.normal(pi_mean, pi_std, nruns)
    np_well_dist = np.random.normal(np_well_mean, np_well_std, nruns)

    if voip_dist == 'Normal':                  vol = np.random.normal(voip_mean,voip_stdev,nruns)
    elif voip_dist == 'Lognormal':             vol = np.e**(np.random.normal(np.log(voip_mean),(np.log(voip[1])-np.log(voip[0]))/6,nruns))
    elif voip_dist == 'Triangular':            vol = np.random.triangular(voip[0], voip_mean, voip[1], nruns)
    else:                                      vol = np.random.uniform(voip[0],voip[1], nruns)

    fluid_dist = np.random.choice(fluids, size=nruns, p=fluid_prob)

    samples = pd.DataFrame(
        {
            'Vol':vol,
            #'RF':rf*np.ones(nruns),
            #'Np_Well':np_well_dist,
            #'Pi':pi_dist,
            'Fluid':fluid_dist
        },
        index=[i+1 for i in range(nruns)]
    )


    if nkrels == 0:
        pass
    elif nkrels == 1:
        krel_dist = [1]*nruns
        if kr_unc == 0:
            krel_kro = [krel_mbal[0][0]]*nruns
            krel_krw = [krel_mbal[0][1]]*nruns
            krel_swi = [krel_mbal[0][2]]*nruns
            krel_sor = [krel_mbal[0][3]]*nruns
            krel_no = [krel_mbal[0][4]]*nruns
            krel_nw = [krel_mbal[0][5]]*nruns
        elif len(krel_mbal[0]) > 3:
            krel_no = np.random.normal((krel_mbal[0][4][1]+krel_mbal[0][4][0])/2,(krel_mbal[0][4][1]-krel_mbal[0][4][0])/6,nruns)
            krel_nw = np.random.normal((krel_mbal[0][5][1]+krel_mbal[0][5][0])/2,(krel_mbal[0][5][1]-krel_mbal[0][5][0])/6,nruns)
            krel_kro = np.random.normal((krel_mbal[0][0][1]+krel_mbal[0][0][0])/2,(krel_mbal[0][0][1]-krel_mbal[0][0][0])/6,nruns)
            krel_krw = np.random.normal((krel_mbal[0][1][1]+krel_mbal[0][1][0])/2,(krel_mbal[0][1][1]-krel_mbal[0][1][0])/6,nruns)
            krel_swi = np.random.normal((krel_mbal[0][2][1]+krel_mbal[0][2][0])/2,(krel_mbal[0][2][1]-krel_mbal[0][2][0])/6,nruns)
            krel_sor = np.random.normal((krel_mbal[0][3][1]+krel_mbal[0][3][0])/2,(krel_mbal[0][3][1]-krel_mbal[0][3][0])/6,nruns)
        else:
            krel_swi = np.random.normal((krel_mbal[0][1]+krel_mbal[0][0])/2,(krel_mbal[0][1]-krel_mbal[0][0])/6,nruns)
            krel_sor = [(1 - krel_swi[i])/2 for i in range(len(krel_swi))]
            krel_krw = [min(1,krw_an*swi_an/krel_swi[i]) for i in range(len(krel_swi))]
            krel_kro = [min(1,kro_an*swi_an/krel_swi[i]) for i in range(len(krel_swi))]
            krel_no = [max(1,no_an*krel_swi[i]/swi_an) for i in range(len(krel_swi))]
            krel_nw = [max(1,nw_an*swi_an/krel_swi[i]) for i in range(len(krel_swi))]
        
        samples = samples.assign(KREL=krel_dist,
                                 KREL_no=krel_no,
                                 KREL_nw=krel_nw,
                                 KREL_kro=krel_kro,
                                 KREL_krw=krel_krw,
                                 KREL_swi=krel_swi,
                                 KREL_sor=krel_sor)        

    else:
        krel_dist = np.random.choice(nkrels, size=nruns, p=krel_prob)
        krel_kro = [krel_mbal[krel_dist[i]][0] for i in range(len(krel_dist))]
        krel_krw = [krel_mbal[krel_dist[i]][1] for i in range(len(krel_dist))]
        krel_swi = [krel_mbal[krel_dist[i]][2] for i in range(len(krel_dist))]
        krel_sor = [krel_mbal[krel_dist[i]][3] for i in range(len(krel_dist))]
        krel_no = [krel_mbal[krel_dist[i]][4] for i in range(len(krel_dist))]
        krel_nw = [krel_mbal[krel_dist[i]][5] for i in range(len(krel_dist))]

        samples = samples.assign(KREL=krel_dist,
                                 KREL_no=krel_no,
                                 KREL_nw=krel_nw,
                                 KREL_kro=krel_kro,
                                 KREL_krw=krel_krw,
                                 KREL_swi=krel_swi,
                                 KREL_sor=krel_sor)

    #samples['Np'] = samples['Vol'] * rf/100
    #samples['Wells'] = samples['Np']/samples['Np_Well']
    samples = samples.round(3)
    return(samples)

@st.cache_data
def getModels(selectedModels):
    dfWell = pd.DataFrame()
    dfSector = pd.DataFrame()
    df3D = pd.DataFrame()
    for key in stqdm(selectedModels):
        f = h5py.File(analogsModels.get(key), 'r')

        # tempos
        mtt = f['/General/MasterTimeTable'] # (0, 0.  , 20280101.  ), (1, 0.1 , 20280101.1 ),
        sDates = [i[2] for i in mtt]
        times = f['TimeSeries/SECTORS/Timesteps'] # [0,1,2,3,4...]

        # datasets
        wVars = f['TimeSeries/WELLS/Variables']
        wOrigins = f['TimeSeries/WELLS/Origins']
        wData = f['TimeSeries/WELLS/Data']
        gVars = f['TimeSeries/GROUPS/Variables']
        gOrigins = f['TimeSeries/GROUPS/Origins']
        gData = f['TimeSeries/GROUPS/Data']
        sVars = f['TimeSeries/SECTORS/Variables']
        sOrigins = f['TimeSeries/SECTORS/Origins']
        sData = f['TimeSeries/SECTORS/Data']

        # indexes
        w_Np_i = np.where(wVars[()] == b'OILVOLSC')[0][0]
        w_Wp_i = np.where(wVars[()] == b'WATVOLSC')[0][0]
        s_N_i = np.where(sVars[()] == b'OILSECSU')[0][0]
        s_FR_i = np.where(sVars[()] == b'OILSECRECO')[0][0]
        g_Np_i = np.where(gVars[()] == b'OILVOLSC')[0][0]
        g_Wp_i = np.where(gVars[()] == b'WATVOLSC')[0][0]
        g_Field_i = np.where((gOrigins[:] == b'FIELD-PRO') | (gOrigins[:] == b'Field-PRO'))[0][0]
        s_Field_i = np.where((sOrigins[:] == b'FIELD') | (sOrigins[:] == b'Field'))[0][0]

        # Well
        for iw,well in enumerate(wOrigins):
            dfWell = pd.concat(
                [dfWell, pd.DataFrame({
                        'Res': [key.split('_')[0]],
                        'Modelo': [key],
                        'Poço': [well.decode()],
                        'Np': int(6.29/1e6*wData[-1:, w_Np_i, iw]),
                        'Np+Wp': int(6.29/1e6*(wData[-1:, w_Wp_i, iw]+wData[-1:, w_Np_i, iw]))})
                ])

        # Sector Field
        dfSector = pd.concat([dfSector,pd.DataFrame({
            'Res': key.split('_')[0],
            'Modelo': key,
            'N': int(6.29/1e6*sData[0, s_N_i, s_Field_i]),
            'FR': sData[-1:, s_FR_i, s_Field_i]
            })
        ])

        # por = f['SpatialProperties/000000/POR']
        # k = 1000*np.array(f['SpatialProperties/000000/PERMI'])
        # sw = f['SpatialProperties/000000/SW']

        # df3D = pd.concat(
        #     [df3D, pd.DataFrame({
        #         'Res': key.split('_')[0],
        #         'Modelo': key,
        #         'POR': por,
        #         'K': np.log(k),
        #         'SW': sw
        #     })]
        # )
        f.close()

    return dfWell, dfSector #, df3D

unitsOil = st.sidebar.radio('Oil Units:',['MMm³','MMBBL'], horizontal=True)
unitsGas = st.sidebar.radio('Gas Units:',['MMm³','TCF'], horizontal=True)

st.subheader('_Reservoir Potential Evaluation_')

tabRes,tabFluid,tabRockFluid,tabVFP,tabSchedule,tabSampling,tabMBAL,tabResults,tabAnalog,tabHelp =  st.tabs([
    'Reservoir:mount_fuji:',
    'Fluid:oil_drum:',
    'Rock-Fluid:earth_americas:',
    'VFP:chart_with_upwards_trend:',
    'Schedule:calendar:',
    'Sampling:game_die:',
    'MBAL:m:',
    'Results:signal_strength:',
    'Analogs:dart:',
    'Help:question:',
    ])

with tabRes:
    st.subheader('Reservoir Data', divider='blue')
    with st.expander('Volumes, Mechanisms, Recoveries'):
        col1, col2 = st.columns(2)
        with col1:
            resType = st.radio('Reservoir type:',['Oil','Gas'], horizontal=True)

            rf = st.number_input('Target RF (%)', 1, 100, 20, help=help_strings['rf'])
            selected_mecanisms = st.multiselect(f'Production Mechanism - {resType}', list_mecanismos[resType])

        with col2:
            voip_dist = st.selectbox('VOIP distribution',options=['Normal','Uniform','Triangular','Lognormal'])
            if resType == 'Oil':
                if unitsOil == 'MMBBL':                     voip = st.slider('VOIP (MMBBL)', 0, 5000, (1000,3000), help=help_strings['sliders'])
                else:                                       voip = st.slider('VOIP (MMm³)', 0, 800, (160,480), help=help_strings['sliders'])
            else:
                if unitsGas == 'TCF':                       voip = st.slider('VGIP (tcf)', 0., 8., (1.,3.), help=help_strings['sliders'])
                else:                                       voip = st.slider('VGIP (MMm³)', 0, 5000, (1000,3000), help=help_strings['sliders'])
            voip_mean = np.mean(voip)
            voip_stdev = (voip[1]-voip[0])/6

            if resType == 'Oil':
                if voip_dist == 'Normal':                   ploto = sns.kdeplot(np.random.normal(voip_mean,voip_stdev,1000), fill=True)
                elif voip_dist == 'Lognormal':              ploto = sns.kdeplot(np.e**(np.random.normal(np.log(voip_mean),(np.log(voip[1])-np.log(voip[0]))/6,1000)), fill=True)
                elif voip_dist == 'Triangular':             ploto = sns.kdeplot(np.random.triangular(voip[0], voip_mean, voip[1], 1000), fill=True)
                else:                                       ploto = sns.kdeplot(np.random.uniform(voip[0],voip[1], 1000), fill=True)
                ploto.set_xlabel("VOIP")
                st.pyplot(ploto.figure, clear_figure=True)
            else:
                if voip_dist == 'Normal':                   plotg = sns.kdeplot(np.random.normal(voip_mean,voip_stdev,1000), fill=True)
                elif voip_dist == 'Lognormal':              plotg = sns.kdeplot(np.e**(np.random.normal(np.log(voip_mean),(np.log(voip[1])-np.log(voip[0]))/6,1000)), fill=True)
                elif voip_dist == 'Triangular':             plotg = sns.kdeplot(np.random.triangular(voip[0],voip_mean,voip[1],1000), fill=True)
                else:                                       plotg = sns.kdeplot(np.random.uniform(voip[0],voip[1],1000), fill=True)
                plotg.set_xlabel("VGIP")
                st.pyplot(plotg.figure, clear_figure=True)


    st.subheader('Production Metrics', divider='blue')
    with st.expander('Production Metrics'):

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
                j = sns.jointplot(y=np.random.normal(np_well_mean, np_well_std, 1000), x=np.random.normal(pi_mean, pi_std, 1000), kind='hex', height=4)
            elif metric_dist == 'Lognormal':
                pass;
            elif metric_dist == 'Triangular':
                j = sns.jointplot(y=np.random.triangular(np_well[0],np_well_mean, np_well[1], 1000), x=np.random.triangular(pi[0],pi_mean,pi[1], 1000), kind='hex', height=4)
            else:
                j = sns.jointplot(y=np.random.uniform(np_well[0],np_well[1],1000), x=np.random.uniform(pi[0],pi[1],1000), kind='hex', height=4)
            j.figure.axes[0].set_xlabel('PI')
            j.figure.axes[0].set_ylabel('Np/well')
            j.figure.axes[0].set_xlim((0, 200))
            j.figure.axes[0].set_ylim((0, 100))
            st.pyplot(j.figure, clear_figure=True)

with tabFluid:
    st.subheader('Fluid Scenarios', divider='blue')
    col1, col2 = st.columns(2)

    with col1:
        nfluids = st.number_input('How many Fluids?',1,3,1)
        fluids = [f+1 for f in range(nfluids)]
        fluid_prob = [st.number_input(f"Probability/weight of fluid {i+1}", 1,100,1, help=help_strings['norm']) for i in range(nfluids)]
        fluid_prob = fluid_prob/np.sum(fluid_prob)

    with col2:
        plotf = sns.barplot(x=fluids, y=fluid_prob, hue=fluids, palette='tab10')
        plotf.set_xlabel('Fluid')
        plotf.set_ylabel('Probability')
        st.pyplot(plotf.figure, clear_figure=True)

    st.subheader('Fluid Parameters', divider='blue')
    for f in fluids:
        with st.expander(f'Fluid {f}: (Probability = {100*fluid_prob[f-1]:.0f}%)'):
            col3,col4 = st.columns(2)
            with col3:
                fluid_input = st.radio(f'Fluid {f} Input Type:',fluid_input_options, key=f'fluid{f}', horizontal=True)
                if fluid_input == "Input File":
                    fluid_files = st.file_uploader(f"PVT file (fluid 1)", help=help_strings['pvt'])
                else:
                    selected_analogue1 = st.selectbox(f'Select Analogue Fluid 1', list_analogues, key = f'analog{f}')
                    Temp_ref = st.number_input('Temp (ºC)',15,200,80, key = f'temp_ref{f}')
                    Pres_ref = st.number_input('Pres (kgf/cm²)',200,1000,500, key = f'pres_ref{f}')
                    Psat_ref = st.number_input('Psat (kgf/cm²)',150,800,350, key = f'psat_ref{f}')
                    pres_type = st.radio('Reference Pressure for Analogue Properties:',['Saturation Pressure','Reservoir Pressure'], horizontal=True, key = f'pres_type{f}')
                    Bo_ref = st.number_input('Bo (m³/m³)',1.,3.,1.7,step=1.,format="%.2f", key = f'bo_ref{f}')
                    Rs_ref = st.number_input('Rs (m³/m³)',50,8000,350, key = f'rs_ref{f}')
                    Visc_ref = st.number_input('Viscosidade (cp)',0.0001,5.,0.35, key = f'visc_ref{f}')

                    pressures,bos,rsss,viscs = normalize_fluid(selected_analogue1,Temp_ref,Pres_ref,Psat_ref,Bo_ref,Rs_ref,Visc_ref,pres_type)
            with col4:
                fig, axs = plt.subplots(ncols=1,nrows=3,figsize=[5,15])

                if fluid_input == "Analogue":
                    axs[0].plot(list_fluids[selected_analogue1]['Pressure'],list_fluids[selected_analogue1]['Bo'],'b-',label=selected_analogue1)
                    axs[0].plot(pressures,bos,'r-',label=f'Fluid {f}')
                    axs[0].set_xlabel('Pressure')
                    axs[0].set_ylabel('Bo (m³/m³)')
                    axs[0].legend()

                    axs[1].plot(list_fluids[selected_analogue1]['Pressure'],list_fluids[selected_analogue1]['Rs'],'b-',label=selected_analogue1)
                    axs[1].plot(pressures,rsss,'r-',label=f'Fluid {f}')
                    axs[1].set_xlabel('Pressure')
                    axs[1].set_ylabel('Rs (m³/m³)')
                    axs[1].legend()

                    axs[2].plot(list_fluids[selected_analogue1]['Pressure'],list_fluids[selected_analogue1]['Visc'],'b-',label=selected_analogue1)
                    axs[2].plot(pressures,viscs,'r-',label=f'Fluid {f}')
                    axs[2].set_xlabel('Pressure')
                    axs[2].set_ylabel('Visc (cp)')
                    axs[2].legend()

                    st.pyplot(fig.figure, clear_figure=True)
                else:
                    pass

with tabRockFluid:
    st.subheader('Relative Permeability Set Definition', divider='blue')

    col3,col4 = st.columns(2)

    with col3:
        nkrels = st.number_input('How many Krel sets?',0,3,1,help='Choose "1" if you wish to input a continuous distribution based on the curve parameters')
        krels = [f+1 for f in range(nkrels)]
        krel_prob = [st.number_input(f"Probability/weight of Krel {i+1}", 1,100,1, help=help_strings['norm']) for i in range(nkrels)]
        krel_prob = krel_prob/np.sum(krel_prob)

    if nkrels != 0:
        with col4:
            fig, plotk =  plt.subplots(ncols=1,nrows=1,figsize=[5,5])
            plotk = sns.barplot(x=krels, y=krel_prob, hue=krels, palette='tab10')
            plotk.set_xlabel('Krel')
            plotk.set_ylabel('Probability')
            st.pyplot(plotk.figure, clear_figure=True)
        

        st.subheader('Relative Permeability Curves', divider='blue')
        krel_mbal = []
        for kr in krels:
            with st.expander(f'Krel {kr}: (Probability = {100*krel_prob[kr-1]:.0f}%)'):

                col1,col2 = st.columns(2)

                with col1:
                    
                    if nkrels == 1:
                        uncertainty_krel = st.checkbox("Do you wish to perform uncertainty assessment on the krel set?",key=f'unc_{kr}')

                        if uncertainty_krel:
                            krel_selection = st.radio('Select Input Type',krel_input_options, horizontal=True,key=f'unc1_{kr}')
                            kr_unc = 1
                        else:
                            krel_selection = st.radio('Select Input Type',krel_input_options+['Input File'], horizontal=True,key=f'unc0_{kr}')
                            kr_unc = 0
                    else:
                        krel_selection = st.radio('Select Input Type',krel_input_options+['Input File'], horizontal=True,key=f'dic_{kr}')
                        kr_unc = 0

                    if krel_selection == "Input File":
                        krel_files = st.file_uploader(f"KREL file", help=help_strings['krel'],key=f'krel_{kr}')

                    elif krel_selection == "User Defined":
                        if kr_unc == 0:
                            kro_user = st.number_input('kro',0.,1.,0.8,key=f'nin_{kr}')
                            krw_user = st.number_input('krw',0.,1.,0.5,key=f'nin1_{kr}')
                            swi_user = st.number_input('swi',0.,1.,0.3,key=f'nin2_{kr}')
                            sor_user = st.number_input('sor',0.,1.,0.3,key=f'nin3_{kr}')
                            no_user = st.number_input('no',0.,10.,4.,key=f'nin4_{kr}')
                            nw_user = st.number_input('nw',0.,10.,1.5,key=f'nin5_{kr}')

                            krel_mbal.append([kro_user,krw_user,swi_user,sor_user,no_user,nw_user])

                        else:
                            krel_properties_dist = st.selectbox('Parameters distribution',options=['Normal','Uniform','Triangular','Lognormal'],key='krel_param')
                            kro_range = st.slider('kro', 0., 1., (0.6,0.9), help=help_strings['sliders'])
                            krw_range = st.slider('krw', 0., 1., (0.4,0.6), help=help_strings['sliders'])
                            swi_range = st.slider('swi', 0., 1., (0.2,0.3), help=help_strings['sliders'])
                            sor_range = st.slider('sor', 0., 1., (0.2,0.3), help=help_strings['sliders'])
                            no_range = st.slider('no', 0., 10., (3.,5.), help=help_strings['sliders'])
                            nw_range = st.slider('nw', 0., 10., (1.5,2.5), help=help_strings['sliders'])

                            kro_user = np.mean(kro_range)
                            krw_user = np.mean(krw_range)
                            swi_user = np.mean(swi_range)
                            sor_user = np.mean(sor_range)
                            no_user = np.mean(no_range)
                            nw_user = np.mean(nw_range)

                            krel_mbal.append([[kro_range[0],kro_range[1]],[krw_range[0],krw_range[1]],[swi_range[0],swi_range[1]],[sor_range[0],sor_range[1]],[no_range[0],no_range[1]],[nw_range[0],nw_range[1]]])

                        sw,kro,krw = calc_corey(kro_user,krw_user,swi_user,sor_user,no_user,nw_user)

                    else:
                        selected_analogue_krel = st.selectbox(f'Select Analogue Krel', list_analogues_krel,key=f'{kr}')
                        kro_an = list_krels[selected_analogue_krel]['kro']
                        krw_an = list_krels[selected_analogue_krel]['krw']
                        swi_an = list_krels[selected_analogue_krel]['swi']
                        sor_an = list_krels[selected_analogue_krel]['sor']
                        no_an = list_krels[selected_analogue_krel]['no']
                        nw_an = list_krels[selected_analogue_krel]['nw']

                        st.text(f'kro = {kro_an}')
                        st.text(f'krw = {krw_an}')
                        st.text(f'swi = {swi_an}')
                        st.text(f'sor = {sor_an}')
                        st.text(f'no = {no_an}')
                        st.text(f'nw = {nw_an}')

                        sw,kro,krw = calc_corey(kro_an,krw_an,swi_an,sor_an,no_an,nw_an)

                with col2:
                    if krel_selection == "Input File":
                        pass
                    else:
                        fig, axs = plt.subplots(ncols=1,nrows=1,figsize=[5,5])
                        axs.plot(sw,kro,'b-')
                        axs.plot(sw,krw,'b-')
                        axs.set_xlim(0,1)
                        axs.set_ylim(0,1)
                        if krel_selection == "Analogue":
                            axs.set_title(f'Analogue {selected_analogue_krel}')
                        else:
                            if kr_unc == 0:
                                axs.set_title(f'Defined Krel {kr}')
                            else:
                                axs.set_title(f'Average Krel {kr}')

                        st.pyplot(fig.figure, clear_figure=True)

                if krel_selection == "Analogue":
                    st.divider()
                    col5,col6 = st.columns(2)
                    with col5:
                        if kr_unc == 0:
                            edit_krel = st.checkbox('Edit Analogue Krel?',key=f'edit_{kr}')
                            if edit_krel:
                                consistency_check = st.checkbox('Consistency Check?',help=help_strings['krel_consistency'],key=f'check_{kr}')
                                if consistency_check:
                                    swi_user = st.number_input('swi',0.,1.,swi_an,key=f'uinput_{kr}')

                                    sor_user = (1 - swi_user)/2
                                    krw_user = min(1,krw_an*swi_an/swi_user)
                                    kro_user = min(1,kro_an*swi_an/swi_user)
                                    no_user = no_an*swi_user/swi_an
                                    nw_user = nw_an*swi_an/swi_user

                                else:
                                    kro_user = st.number_input('kro',0.,1.,kro_an,key=f'uin1_{kr}')
                                    krw_user = st.number_input('krw',0.,1.,krw_an,key=f'uin2_{kr}')
                                    swi_user = st.number_input('swi',0.,1.,swi_an,key=f'uin3_{kr}')
                                    sor_user = st.number_input('sor',0.,1.,sor_an,key=f'uin4_{kr}')
                                    no_user = st.number_input('no',0.,10.,no_an,key=f'uin5_{kr}')
                                    nw_user = st.number_input('nw',0.,10.,nw_an,key=f'uin6_{kr}')

                                sw_e,kro_e,krw_e = calc_corey(kro_user,krw_user,swi_user,sor_user,no_user,nw_user)
                                krel_mbal.append([kro_user,krw_user,swi_user,sor_user,no_user,nw_user])
                            else:
                                krel_mbal.append([kro_an,krw_an,swi_an,sor_an,no_an,nw_an])

                        else:
                            st.header('Denife Ranges for Parameters',divider='blue')
                            consistency_check = st.checkbox('Consistency Check?',help=help_strings['krel_consistency'],key=f'check_{kr}')
                            if consistency_check:
                                krel_properties_dist = st.selectbox('Parameters distribution',options=['Normal','Uniform','Triangular','Lognormal'],key='krel_param')
                                swi_range = st.slider('swi', 0., 1., (0.2,0.3), help=help_strings['sliders'])
                                swi_user = np.mean(swi_range)
                                sor_user = (1 - swi_user)/2
                                krw_user = min(1,krw_an*swi_an/swi_user)
                                kro_user = min(1,kro_an*swi_an/swi_user)
                                no_user = max(1,no_an*swi_user/swi_an)
                                nw_user = max(1,nw_an*swi_an/swi_user)

                                krel_mbal.append([swi_range[0],swi_range[1]])
                            else:
                                krel_properties_dist = st.selectbox('Parameters distribution',options=['Normal','Uniform','Triangular','Lognormal'],key='krel_param')
                                kro_range = st.slider('kro', 0., 1., (0.6,0.9), help=help_strings['sliders'])
                                krw_range = st.slider('krw', 0., 1., (0.4,0.6), help=help_strings['sliders'])
                                swi_range = st.slider('swi', 0., 1., (0.2,0.3), help=help_strings['sliders'])
                                sor_range = st.slider('sor', 0., 1., (0.2,0.3), help=help_strings['sliders'])
                                no_range = st.slider('no', 0., 10., (3.,5.), help=help_strings['sliders'])
                                nw_range = st.slider('nw', 0., 10., (1.5,2.5), help=help_strings['sliders'])

                                kro_user = np.mean(kro_range)
                                krw_user = np.mean(krw_range)
                                swi_user = np.mean(swi_range)
                                sor_user = np.mean(sor_range)
                                no_user = np.mean(no_range)
                                nw_user = np.mean(nw_range)

                                krel_mbal.append([[kro_range[0],kro_range[1]],[krw_range[0],krw_range[1]],[swi_range[0],swi_range[1]],[sor_range[0],sor_range[1]],[no_range[0],no_range[1]],[nw_range[0],nw_range[1]]])


                            sw_e,kro_e,krw_e = calc_corey(kro_user,krw_user,swi_user,sor_user,no_user,nw_user)

                        with col6:
                            if kr_unc == 1 or (kr_unc == 0 and edit_krel):
                                fig, axs = plt.subplots(ncols=1,nrows=1,figsize=[5,5])
                                axs.plot(sw,kro,'b-',label = f'Analogue {selected_analogue_krel}')
                                axs.plot(sw,krw,'b-')

                                axs.plot(sw_e,kro_e,'r-',label = 'Edited Krel')
                                axs.plot(sw_e,krw_e,'r-')

                                axs.set_xlim(0,1)
                                axs.set_ylim(0,1)

                                axs.legend()

                                st.pyplot(fig.figure, clear_figure=True)
        
        st.write(krel_mbal)

with tabSchedule:
    st.subheader("Schedule", divider='blue')
    #d = st.date_input("Fisrt Oil", datetime.date(2034, 1, 1))
    d = st.text_input("Fisrt Oil", "01/01/2028")
    delta_prod = st.number_input("Production Time (years)",1,50,30)
    interval = st.number_input('Interval between wells (days):', 0, None, None, step=30, help='teste help', placeholder='One new well every 90 days')

    st.subheader("Constraints", divider='blue')
    def_cons = st.checkbox("Define Constraints?",help=help_strings['def_const'])
    if def_cons:
        with st.expander("FPSO Constraints"):
            fpso_qo = st.number_input("Oil Capacity (kbpd)",40,675,150)
            fpso_qg = st.number_input("Gas Capacity (MMm³/d)",3.,36.,12.)
        with st.expander("Producer Well Constraints"):
            prod_qo = st.number_input("Max Oil Rate (kbpd)",10,80,40)
            prod_qg = st.number_input("Max Gas Rate (MMm³/d)",0.2,6.,4.)
            prod_bhp = st.number_input("Min BHP (kgf/cm²)",2,1000,300)
            prod_definition = st.checkbox("Define Number of Producers?", help=help_strings['nprod'])
            if prod_definition:
                def_cons_k = 1
                prod_number = st.number_input("Number of Producer Wells",1,20,1)
            else:
                def_cons_k = 0
                prod_number = 0
        with st.expander("Water Injector Well Constraints"):
            pass
        with st.expander("Gas Injector Well Constraints"):
            pass

with tabSampling:

    st.subheader('MBAL Runs', divider='blue')
    nruns = st.number_input('MBAL runs:', 3, None, 10, step=100)

    create_samples = st.button("Generate Sampling")

    samples = define_samples(nruns)

    st.subheader('Experiments', divider='blue')
    st.write(samples)
    st.subheader('Stats', divider='blue')
    st.write(samples.describe().loc[['mean', '50%', 'std', 'min', 'max', 'count']].round(0))

with tabMBAL:


    path = "monai_p50_blackoil_streamlit.mbi"
    run_simulator = st.button("Run MBAL")
    if run_simulator:

        result_mbal_prev = mbal_calc(samples,path)
        result_mbal = result_mbal_prev.json()#["Curvas"]

        Frg = [result_mbal["CurvasFrg"][i][-1] for i in range(len(samples['Vol']))]
        Gp = [Frg[i]*samples['Vol'][i+1]/100 for i in range(len(samples['Vol']))]

        results_table = samples.assign(Frg=Frg,
                                       Gp=Gp)

        st.write(results_table)

with tabAnalog:
    selectedModels = st.multiselect('Analog Models:',analogsModels.keys())
    # groupBy_option = st.radio('Group Vars By:', groupBy_options, horizontal=True)

    # st.write(list(analogsModels.keys()))

    if len(selectedModels):
        dfWell,dfSector = getModels(selectedModels)
        dfWell = dfWell[dfWell['Np'] > 0]
        dfSector['Np'] = dfSector['N'] * dfSector['FR'] / 100

        dfx = dfWell.groupby('Modelo')['Np'].agg(['sum','mean','count'])
        dfx.rename(columns={'sum':'Np','mean':'Np/Poço','count':'Poços'}, inplace=True)
        dfx = dfx.round(0)
        dfx

        # plot = sns.kdeplot(dfWell,x='Modelo')
        # st.pyplot(plot.figure, clear_figure=True)

with tabResults:
    if run_simulator:
        
        pct_frg = np.sort(Gp)
        p10 = Gp.index(pct_frg[int(math.ceil(nruns*0.9))])
        p50 = Gp.index(pct_frg[int(math.ceil(nruns*0.5))])
        p90 = Gp.index(pct_frg[int(math.ceil(nruns*0.1))])
        anos = np.linspace(0,delta_prod+2,delta_prod+2)

        st.write(f'P10 {delta_prod} years = {round(Gp[p10],0)}')
        st.write(f'P50 {delta_prod} years = {round(Gp[p50],0)}')
        st.write(f'P90 {delta_prod} years = {round(Gp[p90],0)}')

        fig_res, axs = plt.subplots(ncols=1,nrows=2,figsize=[5,5])
        for i in range(len(samples['Vol'])):
            result_mbal["Curvas"][i].insert(0,0)
            result_mbal["CurvasFrg"][i].insert(0,0)
            if i == p50 or i == p10 or i == p90:
                pass
            else:                
                axs[0].plot(anos,result_mbal["Curvas"][i],'0.9',label="_nolegend_")
                axs[1].plot(anos,result_mbal["CurvasFrg"][i],'0.9',label="_nolegend_")

        axs[0].plot(anos,result_mbal["Curvas"][p10],'#00FFFF',label="P10")
        axs[0].plot(anos,result_mbal["Curvas"][p50],'r-',label="P50")
        axs[0].plot(anos,result_mbal["Curvas"][p90],'#00FFFF',label="P90")
        axs[0].set_xlabel("Year")
        axs[0].set_ylabel("Qg")

        axs[1].plot(anos,result_mbal["CurvasFrg"][p10],'#00FFFF',label="P10")
        axs[1].plot(anos,result_mbal["CurvasFrg"][p50],'r-',label="P50")
        axs[1].plot(anos,result_mbal["CurvasFrg"][p90],'#00FFFF',label="P90")
        axs[1].set_xlabel("Year")
        axs[1].set_ylabel("FRg")
        #axs[0].legend()


            #axs[1].hist(results_table['Frg'])
            #axs[1].set_xlabel("Frg")

        st.pyplot(fig_res.figure, clear_figure=True)

st.caption('Powered by DND :sunglasses:')
