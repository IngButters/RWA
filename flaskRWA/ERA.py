from flask import Flask, render_template, request
import os
import pandas as pd
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
import sqlite3

currentdirectory = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

#Parte de pandas df
#--------------------------------Información de precipitación-------------------------------------------
filename = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'

#letra = "P"

#columnas = ['fecha',"21210150",
#"21215160",
#"21210130"]


df_precip_sup = pd.read_csv(filename, nrows=10)#, usecols = columnas)

# Missing data in tetis = -1
df_precip_sup = df_precip_sup.fillna(-1)
df_precip_sup.fecha = pd.to_datetime(df_precip_sup.fecha)
#df_precip_sup = df_precip_sup.head(1)



#--------------------------------Información de temperatura-------------------------------------------
filenameTemp = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
df_temp_sup = pd.read_csv(filenameTemp, nrows=10)#, usecols = columnas)

#letra = "T"

# Missing data temp in tetis = -99
df_temp_sup = df_temp_sup.fillna(-99)
df_temp_sup.fecha = pd.to_datetime(df_temp_sup.fecha)
#df_temp_sup = df_temp_sup.head(5)

#----------------------------------Script Lectura de datos----------------------------------------------
def abrirArchivos(ruta, letra, columnas):
    """ En esta función se abren los archivos con las columnas seleccionadas 
        ruta: es la ruta del archivo
        letra: es la identifiación del tipo de dato -> P=Precipitacion, T=Temperatura
        return df_datos: retorna los datos seleccionados
    """
    if letra == "P":
        df_datos = pd.read_csv(ruta, usecols = columnas)
        df_datos = df_datos.fillna(-1)
        #df_datos.fecha = pd.to_datetime(df_datos.fecha)



    else:
        df_datos = pd.read_csv(ruta, usecols = columnas)
        df_datos = df_datos.fillna(-99)
        #df_datos.fecha = pd.to_datetime(df_datos.fecha, usecols = columnas)

    return df_datos

    






@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')# this redirects to my html file

@app.route('/tetis', methods = ['GET','POST'])
def tetis_page():

    return render_template('tetis.html')


@app.route("/climatologia", methods = ['GET','POST'])
def climatologia_page():
    try:
        cambioClimatico = ['Si','No']
        proyecTemporal = ['Anual', 'Trimestral', 'Ensamble']
        
        estaciones = df_precip_sup.columns.values
        estacionesTemp = df_temp_sup.columns.values

        archivoTetis = ['Evento', 'Cedex']

        precpGet = request.form.getlist('estacion')
        print(precpGet)

        ruta = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
        df_precipSup = abrirArchivos(ruta, "P", precpGet)
        print(df_precipSup.head(10))



        tempGet = request.form.getlist('estacionTemp')
        print(tempGet)

        return render_template('climatologia.html', tables=[df_precip_sup.to_html(classes='data', index=False)], titles=df_precip_sup.columns.values, cambioClimatico=cambioClimatico, proyecTemporal=proyecTemporal, estaciones=estaciones, estacionesTemp=estacionesTemp, archivoTetis=archivoTetis)
            
        #return render_template('climatologia.html', result=result, result2=result2)# this redirects to my html file

    except:
        return render_template('climatologia.html')


if __name__ == '__main__': #checks if our file executes directly and not imported
    app.run(debug=True) #



