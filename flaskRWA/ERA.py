from flask import Flask, render_template, request
import os
import pandas as pd
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
import sqlite3

currentdirectory = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

#Leer todos los datos
#--------------------------------Información de precipitación-------------------------------------------
filename = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
cols = pd.read_csv(filename, nrows=1).columns
df_precip_sup = pd.read_csv(filename, nrows=1, usecols=cols[:-1])#, usecols = columnas)

# Missing data in tetis = -1
df_precip_sup = df_precip_sup.fillna(-1)
df_precip_sup = df_precip_sup.round(decimals=2)



#--------------------------------Información de temperatura-------------------------------------------
filenameTemp = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
cols = pd.read_csv(filenameTemp, nrows=1).columns
df_temp_sup = pd.read_csv(filenameTemp, nrows=1, usecols=cols[1:])#, usecols = columnas)

# Missing data temp in tetis = -99
df_temp_sup = df_temp_sup.fillna(-99)
df_temp_sup = df_temp_sup.round(decimals=2)



#-----------------------------------Ubicacion estaciones precipitacion----------------------------------
def ubicacion_estaciones(ruta_ub):
    df_ubic_precip_sup = pd.read_csv(ruta_ub, usecols=['CODIGO','altitud','longitud','latitud'])
    #df_ubic_precip_sup.set_index('CODIGO', inplace=True)
    df_ubic_precip_sup = df_ubic_precip_sup.round(decimals=2)
    #df_ubic_precip_sup = df_ubic_precip_sup.loc[list(map(int, filas[1:]))]

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
def archivoEvento(df_precip_sup, df_tempSup, df_ubi_info, precpGet, tempGet):

    #Inciar condicion de precipitacion
    if isinstance(df_precip_sup, pd.DataFrame):
        df_precip_sup_cond = df_precip_sup.loc[0].values[0]
    else:
        df_precip_sup_cond = df_precip_sup

        #Inciar condicion de precipitacion
    if isinstance(df_tempSup, pd.DataFrame):
        df_temp_sup_cond = df_tempSup.loc[0].values[0]
    else:
        df_temp_sup_cond = df_tempSup


    #---------ENCABEZADO-----------------------------------------------
    Tetis_file = open("Tetis_file.txt","w+")
    
    #Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
    #Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
    #Tetis_file.write("F           01-01-1950      00:00\n")

    #if df_precip_sup == 'None' or df_precip_sup is None:
    #if df_precip_sup is None or df_precip_sup == 'None':   
    #if df_precip_sup.loc[0].values[0] == -999 or df_precip_sup == 'None':  
    if df_precip_sup_cond == 'None':
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

            #Temperatura
        for j in tempGet:
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])   +'\n')

        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = df_tempSup
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))


    #elif df_tempSup == 'None':
    elif df_temp_sup_cond == 'None':
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])   +'\n')  

                #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = df_precip_sup
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))


    else:
        #--------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])   +'\n')  
        #Temperatura
        for j in tempGet:
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])   +'\n')
        
        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_precip_sup, df_tempSup], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

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
    #try:
        cambioClimatico = ['No','Si']
        #Selecciona cambio climatico
        cambioClimaticoSiNo = request.form.getlist('cambClima')
        # initialize an empty string
        str1 = " " 
        # convert string  
        cambioClimaticoSiNo = str1.join(cambioClimaticoSiNo)
        
        #print(cambioClimaticoSiNo)
        #print(cambioClimaticoSiNo[0])

        proyecTemporal = ['No Aplica','Anual', 'Trimestral', 'Ensamble']
        #Selecciona cambio proyeccion temporal
        proyTemporal_sel = request.form.getlist('proyTemp')

        str_proy_temp = " " 
        # convert string  
        proyTemporal_sel = str_proy_temp.join(proyTemporal_sel)
        #print(proyTemporal_sel)

        rcps = ['No aplica','2.5','4.5', '6.0', '8.5']
        #Selecciona cambio proyeccion temporal
        rcps_sel = request.form.getlist('rcp')

        str_rcps_sel = " " 
        # convert string  
        proyTemporal_sel = str_proy_temp.join(proyTemporal_sel)

        
        estaciones = df_precip_sup.columns.values
        estacionesTemp = df_temp_sup.columns.values

        archivoTetis = ['Evento', 'Cedex']

        #--------------------------------Ubicacion estaciones-----------------------------------
        ruta_ub = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Ubicacion_puntos.csv'
        df_ub = ubicacion_estaciones(ruta_ub)
        #print(df_ub_precipSup.head())


        if cambioClimaticoSiNo == 'No':
            #Estaciones seleccionadas de precipitacion
            precpGet = request.form.getlist('estacion')
            # initialize an empty string
            str_Prec = " " 
            # convert string  
            verif_est_precip = str_Prec.join(precpGet)
            #print(verif_est_precip)

            #Estaciones seleccionadas de temperatura
            tempGet = request.form.getlist('estacionTemp')
            # initialize an empty string
            str_Temp = " " 
            # convert string  
            verif_est_temp = str_Temp.join(tempGet)
            #print(verif_est_temp)

            #Seleccion = Ninguna en precipitacion
            if verif_est_precip == 'None':
                #--------------------------Lectura datos de temperatura---------------------------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                df_precipSup = verif_est_precip
                #--------------------------------Generar archivo Tetis-----------------------------------------------
                archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)

            #Seleccion = Ninguna en temperatura
            elif verif_est_temp == 'None':
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                df_tempSup = verif_est_temp

                archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)


            else:
                        
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                #--------------------------Lectura datos de temperatura---------------------------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                #--------------------------------Generar archivo Tetis-----------------------------------------------
                archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)

        else:
            #Estaciones seleccionadas de precipitacion
            precpGet = request.form.getlist('estacion')
            # initialize an empty string
            str_Prec = " " 
            # convert string  
            verif_est_precip = str_Prec.join(precpGet)
            #print(verif_est_precip)

            #Estaciones seleccionadas de temperatura
            tempGet = request.form.getlist('estacionTemp')
            # initialize an empty string
            str_Temp = " " 
            # convert string  
            verif_est_temp = str_Temp.join(tempGet)
            #print(verif_est_temp)

            if proyTemporal_sel == 'No Aplica':


                #Seleccion = Ninguna en precipitacion
                if verif_est_precip == 'None':
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                    df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                    df_precipSup = verif_est_precip
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)

                #Seleccion = Ninguna en temperatura
                elif verif_est_temp == 'None':
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                    df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                    df_tempSup = verif_est_temp

                    archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)


                else:
                            
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                    df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                    df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)


            elif proyTemporal_sel == 'Anual':
                #Seleccion = Ninguna en precipitacion
                if verif_est_precip == 'None':
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                    df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                    df_precipSup = verif_est_precip
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)

                #Seleccion = Ninguna en temperatura
                elif verif_est_temp == 'None':
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                    df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                    df_tempSup = verif_est_temp

                    archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)


                else:
                            
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                    df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                    df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet)

            else:
                pass

        



            




        return render_template('climatologia.html', tables=[df_precip_sup.to_html(classes='data', index=False)], titles=df_precip_sup.columns.values, cambioClimatico=cambioClimatico, proyecTemporal=proyecTemporal, rcps=rcps, estaciones=estaciones, estacionesTemp=estacionesTemp, archivoTetis=archivoTetis)

        #return send_file(video, as_attachment=True)
            
        #return render_template('climatologia.html', result=result, result2=result2)# this redirects to my html file

    #except:
    #    return render_template('climatologia.html')


if __name__ == '__main__': #checks if our file executes directly and not imported
    app.run(debug=True) #



