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
    'path': "monai_p50_blackoil_streamlit.mbi"
    }
]

@app.route('/mbal',methods=['PUT'])
def run_mbal():
    Curvas = []
    propriedades[0].update(request.get_json())
    vol = propriedades[0]["volumes"]
    path = propriedades[0]["path"]
    pythoncom.CoInitialize()
    petex = openserver.OpenServer()
    with petex:
        petex.DoCmd('MBAL.START')
        petex.DoCmd(f'MBAL.OPENFILE("{os.path.join(os.getcwd(),path)}")')
        for i in range(len(vol)):
            petex.DoSet("MBAL.MB[0].TANK[0].OGIP",f"{vol[i]}")
            petex.DoCmd('MBAL.MB.RunPrediction')
            Curvas.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER").tolist())

        petex.DoCmd('MBAL.SHUTDOWN')
    dic = {
        "Curvas": Curvas
    }
    return dic

@app.route('/mbal_get',methods=['GET'])
def get_mbal():
    Curvas = []
    vol = propriedades[0]["volumes"]
    path = propriedades[0]["path"]
    pythoncom.CoInitialize()
    petex = openserver.OpenServer()
    with petex:
        petex.DoCmd('MBAL.START')
        petex.DoCmd(f'MBAL.OPENFILE("{os.path.join(os.getcwd(),path)}")')
        for i in range(len(vol)):
            petex.DoSet("MBAL.MB[0].TANK[0].OGIP",f"{vol[i]}")
            petex.DoCmd('MBAL.MB.RunPrediction')
            #Curvas.append(json.dumps(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER")))
            Curvas.append(petex.DoGet("MBAL.MB[0].TRES[{Prediction}][{Prediction}][$].GASRECOVER").tolist())

        petex.DoCmd('MBAL.SHUTDOWN')
    dic = {
        "Curvas": Curvas
    }
    return dic

app.run(port=8600,host='0.0.0.0',debug=True)
