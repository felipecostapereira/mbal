from flask import Flask, request
import openserver as openserver
import os
import pandas as pd
import numpy as np
import pythoncom
import json

app = Flask(__name__)

propriedades = [
    {
    'volumes': [1800,2300,2000],
    'path': "monai_p50_blackoil_streamlit.mbi",
    'date_start': "01/01/2028",
    'date_end': "01/01/2058",
    'fpso_qo':0,
    'fpso_qg':0,
    'prod_qo':0,
    'prod_qg':0,
    'prod_bhp':0,
    'nprod':0,
    'krel_no': [],
    'krel_nw': [],
    'krel_kro': [],
    'krel_krw': [],
    'krel_swi': [],
    'krel_sor': [],
    }
]

@app.route('/mbal',methods=['PUT'])
def run_mbal():
    CurvasFrg = []
    Curvas = []
    CurvasGp = []
    propriedades[0].update(request.get_json())
    vol = propriedades[0]["volumes"]
    path = propriedades[0]["path"]
    date_start = propriedades[0]["date_start"]
    date_end = propriedades[0]["date_end"]
    if len(propriedades[0]["krel_no"]) > 0:
        krel_no = propriedades[0]["krel_no"]
        krel_nw = propriedades[0]["krel_nw"]
        krel_kro = propriedades[0]["krel_kro"]
        krel_krw = propriedades[0]["krel_krw"]
        krel_swi = propriedades[0]["krel_swi"]
        krel_sor = propriedades[0]["krel_sor"]

    # if int(propriedades[0]['fpso_qo']) > 0:
    #     fpso_qo = propriedades[0]["fpso_qo"]
    #     fpso_qg = propriedades[0]["fpso_qg"]
    #     prod_qo = propriedades[0]["prod_qo"]
    #     prod_qg = propriedades[0]["prod_qg"]
    #     prod_bhp = propriedades[0]["prod_bhp"]
    #     nprod = propriedades[0]["nprod"]

    pythoncom.CoInitialize()
    petex = openserver.OpenServer()
    with petex:
        petex.DoCmd('MBAL.START')
        petex.DoCmd(f'MBAL.OPENFILE("{os.path.join(os.getcwd(),path)}")')
        for i in range(len(vol)):
            petex.DoSet("MBAL.MB[0].TANK[0].OGIP",f"{vol[i]}")
            petex.DoSet("MBAL.MB[0].TANK[0].PRODSTART",f"{date_start}")
            petex.DoSet("MBAL.MB[0].PREDINP.DRILL[0].STARTTIME",f"{date_start}")
            petex.DoSet("MBAL.MB[0].PREDINP.CALCDRILL[0].STARTTIME",f"{date_start}")
            petex.DoSet("MBAL.MB[0].PREDINP.USEREND",f"{date_end}")
            if len(propriedades[0]['krel_no']) > 0:
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.EXPON.Krg",f"{krel_no[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.EXPON.Krw",f"{krel_nw[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.ENDPOINT.Krg",f"{krel_kro[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.ENDPOINT.Krw",f"{krel_krw[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.RESSAT.Krg",f"{krel_sor[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.RESSAT.Krw",f"{krel_swi[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].CONWATER",f"{krel_swi[i]}")
            if isinstance(propriedades[0]['fpso_qo'], list):
                #petex.DoSet("",f"{fpso_qo}")
                petex.DoSet("MBAL.MB[0].CONSTRAINTS[0].TARGETGASRATE",f"{propriedades[0]['fpso_qg'][i]}")
                #petex.DoSet("",f"{prod_qo}")
                petex.DoSet("MBAL.MB[0].PREDWELL[0].CONSTRAINTS.MAXRATE",f"{propriedades[0]['prod_qg']}")
                petex.DoSet("MBAL.MB[0].PREDWELL[0].CONSTFBHP",f"{propriedades[0]['prod_bhp']}")
                petex.DoSet("MBAL.MB[0].PREDINP.DRILL[0].NUMWELLS",f"{propriedades[0]['nprod'][i]}")
            elif int(propriedades[0]['fpso_qo']) > 0:
                #petex.DoSet("",f"{fpso_qo}")
                petex.DoSet("MBAL.MB[0].CONSTRAINTS[0].TARGETGASRATE",f"{propriedades[0]['fpso_qg']}")
                #petex.DoSet("",f"{prod_qo}")
                petex.DoSet("MBAL.MB[0].PREDWELL[0].CONSTRAINTS.MAXRATE",f"{propriedades[0]['prod_qg']}")
                petex.DoSet("MBAL.MB[0].PREDWELL[0].CONSTFBHP",f"{propriedades[0]['prod_bhp']}")
                petex.DoSet("MBAL.MB[0].PREDINP.DRILL[0].NUMWELLS",f"{propriedades[0]['nprod']}")
            petex.DoCmd('MBAL.MB.RunPrediction')
            CurvasFrg.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER").tolist())
            Curvas.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRATE").tolist())
            CurvasGp.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER").tolist())

        petex.DoCmd('MBAL.SHUTDOWN')
    dic = {
        "CurvasFrg": CurvasFrg,
        "Curvas": Curvas
    }
    return dic

@app.route('/mbal_get',methods=['GET'])
def get_mbal():
    CurvasFrg = []
    Curvas = []
    CurvasGp = []
    vol = propriedades[0]["volumes"]
    path = propriedades[0]["path"]
    date_start = propriedades[0]["date_start"]
    date_end = propriedades[0]["date_end"]
    if len(propriedades[0]["krel_no"]) > 0:
        krel_no = propriedades[0]["krel_no"]
        krel_nw = propriedades[0]["krel_nw"]
        krel_kro = propriedades[0]["krel_kro"]
        krel_krw = propriedades[0]["krel_krw"]
        krel_swi = propriedades[0]["krel_swi"]
        krel_sor = propriedades[0]["krel_sor"]

    if int(propriedades[0]['fpso_qo']) > 0:
        fpso_qo = propriedades[0]["fpso_qo"]
        fpso_qg = propriedades[0]["fpso_qg"]
        prod_qo = propriedades[0]["prod_qo"]
        prod_qg = propriedades[0]["prod_qg"]
        prod_bhp = propriedades[0]["prod_bhp"]
        nprod = propriedades[0]["nprod"]

    pythoncom.CoInitialize()
    petex = openserver.OpenServer()
    with petex:
        petex.DoCmd('MBAL.START')
        petex.DoCmd(f'MBAL.OPENFILE("{os.path.join(os.getcwd(),path)}")')
        for i in range(len(vol)):
            petex.DoSet("MBAL.MB[0].TANK[0].OGIP",f"{vol[i]}")
            petex.DoSet("MBAL.MB[0].TANK[0].PRODSTART",f"{date_start}")
            petex.DoSet("MBAL.MB[0].PREDINP.DRILL[0].STARTTIME",f"{date_start}")
            petex.DoSet("MBAL.MB[0].PREDINP.CALCDRILL[0].STARTTIME",f"{date_start}")
            petex.DoSet("MBAL.MB[0].PREDINP.USEREND",f"{date_end}")
            if len(propriedades[0]['krel_no']) > 0:
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.EXPON.Krg",f"{krel_no[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.EXPON.Krw",f"{krel_nw[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.ENDPOINT.Krg",f"{krel_kro[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.ENDPOINT.Krw",f"{krel_krw[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.RESSAT.Krg",f"{krel_sor[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].RELPERM.RESSAT.Krw",f"{krel_swi[i]}")
                petex.DoSet("MBAL.MB[0].TANK[0].CONWATER",f"{krel_swi[i]}")
            if int(propriedades[0]['fpso_qo']) > 0:
                #petex.DoSet("",f"{fpso_qo}")
                petex.DoSet("MBAL.MB[0].CONSTRAINTS[0].MAXGASRATE",f"{fpso_qg}")
                #petex.DoSet("",f"{prod_qo}")
                petex.DoSet("MBAL.MB[0].PREDWELL[$].CONSTRAINTS.MAXRATE",f"{prod_qg}")
                petex.DoSet("MBAL.MB[0].PREDWELL[$].CONSTFBHP",f"{prod_bhp}")
                petex.DoSet("MBAL.MB[0].PREDINP.DRILL[0].NUMWELLS",f"{nprod}")
            petex.DoCmd('MBAL.MB.RunPrediction')
            #Curvas.append(json.dumps(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER")))
            CurvasFrg.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER").tolist())
            Curvas.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRATE").tolist())
            CurvasGp.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER").tolist())
        petex.DoCmd('MBAL.SHUTDOWN')
    dic = {
        "CurvasFrg": CurvasFrg,
        "Curvas": Curvas
    }
    return dic

app.run(port=8600,host='0.0.0.0',debug=False)
