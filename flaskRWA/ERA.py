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
cols = pd.read_csv(filename, nrows=1).columns
df_precip_sup = pd.read_csv(filename, nrows=1, usecols=cols[:-1])#, usecols = columnas)

# Missing data in tetis = -1
df_precip_sup = df_precip_sup.fillna(-1)
#df_precip_sup.fecha = pd.to_datetime(df_precip_sup.fecha)
#df_precip_sup = df_precip_sup.head(1)



#--------------------------------Información de temperatura-------------------------------------------
filenameTemp = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
cols = pd.read_csv(filenameTemp, nrows=1).columns
df_temp_sup = pd.read_csv(filenameTemp, nrows=1, usecols=cols[1:])#, usecols = columnas)

#letra = "T"

# Missing data temp in tetis = -99
df_temp_sup = df_temp_sup.fillna(-99)
#df_temp_sup.fecha = pd.to_datetime(df_temp_sup.fecha)
#df_temp_sup = df_temp_sup.head(5)


#-----------------------------------Ubicacion estaciones precipitacion----------------------------------
#Load the columns for selecting the ones we want
#cols = pd.read_csv('C:/Users/Bender/Desktop/Mapas_ERA/RWA/RWA/flaskRWA/static/clima_isoyetas_sup.csv', nrows=1).columns

#df_ubic_precip_sup = pd.read_csv('C:/Users/Bender/Desktop/Mapas_ERA/RWA/RWA/flaskRWA/static/clima_isoyetas_sup.csv', usecols=#['CODIGO','altitud','longitud','latitud'])#, usecols=cols[:-1])

def ubicacion_precip(ruta_ub, filas):
    df_ubic_precip_sup = pd.read_csv(ruta_ub, usecols=['CODIGO','altitud','longitud','latitud'])
    df_ubic_precip_sup.set_index('CODIGO', inplace=True)
    df_ubic_precip_sup = df_ubic_precip_sup.loc[list(map(int, filas[1:]))]

    return df_ubic_precip_sup


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

#--------------------------------Generar archivo de evento txt-----------------------------------------
def archivoEvento(df_precip_sup, df_precip_sup_info, df_precip_sup_info_2, columnas):
    Tetis_file = open("Tetis_file.txt","w+")
    Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
    Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
    Tetis_file.write("F           01-01-1950      00:00\n")
    for i in df_precip_sup_info.index.values:
        Tetis_file.write('P         "'+str(df_precip_sup_info['CODIGO'].iloc[i])    +'" '+str(df_precip_sup_info_2['latitud'].iloc[i])+' '+str(df_precip_sup_info_2['longitud'].iloc[i])+'      '+str(df_precip_sup_info['altitud'].iloc[i])+'\n')
    Tetis_file.write("*dt(dia)\n")
    Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
    with open('Tetis_file.txt', 'a+') as f: df_precip_sup[columnas[1:]].to_string(f, col_space=7)
    Tetis_file.close()
    return Tetis_file

    






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

        #---------------------------------Datos de Precipitacion----------------------------------------------
        ruta = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
        df_precipSup = abrirArchivos(ruta, "P", precpGet)
        print(df_precipSup.head(10))

        #--------------------------------Ubicacion estaciones precipitacion-----------------------------------
        ruta_ub = 'C:/Users/Bender/Desktop/Mapas_ERA/RWA/RWA/flaskRWA/static/clima_isoyetas_sup.csv'
        df_ub_precipSup = ubicacion_precip(ruta_ub, precpGet)
        print(df_ub_precipSup.head())

        #--------------------------------Generar archivo Tetis-----------------------------------------------
        df_ub_precipSup.reset_index(inplace=True)
        df_precip_sup_info_2 = df_ub_precipSup[['latitud','longitud']]
        df_precip_sup_info_2 = df_precip_sup_info_2.round(decimals=2)
        columnas = df_precipSup.columns
        print(archivoEvento(df_precipSup, df_ub_precipSup, df_precip_sup_info_2, columnas))



        tempGet = request.form.getlist('estacionTemp')
        print(tempGet)


        return render_template('climatologia.html', tables=[df_precip_sup.to_html(classes='data', index=False)], titles=df_precip_sup.columns.values, cambioClimatico=cambioClimatico, proyecTemporal=proyecTemporal, estaciones=estaciones, estacionesTemp=estacionesTemp, archivoTetis=archivoTetis)

        #return send_file(video, as_attachment=True)
            
        #return render_template('climatologia.html', result=result, result2=result2)# this redirects to my html file

    except:
        return render_template('climatologia.html')


if __name__ == '__main__': #checks if our file executes directly and not imported
    app.run(debug=True) #



