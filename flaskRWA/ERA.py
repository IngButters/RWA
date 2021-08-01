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
        #df_datos = df_datos.fillna(-1)
        #df_datos.fecha = pd.to_datetime(df_datos.fecha)

    else:
        df_datos = pd.read_csv(ruta, usecols = columnas)
        #df_datos = df_datos.fillna(-99)
        #df_datos.fecha = pd.to_datetime(df_datos.fecha, usecols = columnas)

    return df_datos


#--------------------------------Generar archivo de evento txt-----------------------------------------
def archivoEvento(df_precip_sup, df_tempSup, df_ubi_info, precpGet, tempGet, nomb_archivo):

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
    Tetis_file = open(nomb_archivo+".txt","w+")
    
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

    
#-------------------------------------------------------Trimestre Precipitacion---------------------------------------------------------------
def trimestre_precip(df_precipSup, rcp_clima):
    df_precipSup['date'] = pd.date_range(start='01/01/1950', periods=len(df_precipSup), freq='D')
    df_precipSup.set_index(['date'], inplace=True)
    df_precipSup_2011_2040 = df_precipSup.copy(deep=True)
    df_precipSup_2041_2070 = df_precipSup.copy(deep=True)
    df_precipSup_2071_2100 = df_precipSup.copy(deep=True)

    if rcp_clima == '2.5':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9327
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0751
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.0936
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.0786

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9577
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 1.1045
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.205
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.0476

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 0.9461
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.089
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.1974
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 1.0336

    elif rcp_clima == '4.5':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9387
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0205
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.1089
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.0943

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9668
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 0.995
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.1834
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.0442

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 1.0003
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.0362
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.1974
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 1.0675

    elif rcp_clima == '6.0':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9389
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0213
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.1054
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.1117

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9814
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 1.0586
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.1846
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.039

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 1.0249
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.0707
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.2297
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 1.033

    elif rcp_clima == '8.5':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9301
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0551
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.1334
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.1503

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9776
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 1.0996
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.2304
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.0842

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 1.0647
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.1436
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.2125
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 0.9771

    df_precipSup_2011_2040.reset_index(inplace=True)
    df_precipSup_2041_2070.reset_index(inplace=True)
    df_precipSup_2071_2100.reset_index(inplace=True)
    
    del df_precipSup_2011_2040['date']
    del df_precipSup_2041_2070['date']
    del df_precipSup_2071_2100['date']

    return (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100)

#----------------------------------------------------------------Trimestre Temperatura------------------------------------------------
def trimestre_temp(df_tempSup, rcp_clima):
    df_tempSup['date'] = pd.date_range(start='01/01/1950', periods=len(df_tempSup), freq='D')
    df_tempSup.set_index(['date'], inplace=True)
    df_tempSup_2011_2040 = df_tempSup.copy(deep=True)
    df_tempSup_2041_2070 = df_tempSup.copy(deep=True)
    df_tempSup_2071_2100 = df_tempSup.copy(deep=True)

    if rcp_clima == '2.5':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 0.98
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 0.92
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 0.94
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 0.88

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 1.32
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 1.3
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 1.31
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 1.21

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 1.37
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 1.26
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 1.28
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] + 1.22

    elif rcp_clima == '4.5':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 1.15
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 1.02
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 1.05
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 0.99

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 1.88
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 1.82
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 1.81
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 1.70

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 2.22
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 2.04
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 2.11
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] + 1.99

    elif rcp_clima == '6.0':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 1.05
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 0.9
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 0.9
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 0.84

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 1.69
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 1.62
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 1.65
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 1.53

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 2.58
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 2.42
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 2.51
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] +2.32

    elif rcp_clima == '8.5':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 1.2
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 1.07
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 1.11
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 1.04

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 2.47
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 2.32
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 2.38
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 2.17

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 3.94
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 3.67
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 3.86
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] + 3.55

    df_tempSup_2011_2040.reset_index(inplace=True)
    df_tempSup_2041_2070.reset_index(inplace=True)
    df_tempSup_2071_2100.reset_index(inplace=True)
    
    del df_tempSup_2011_2040['date']
    del df_tempSup_2041_2070['date']
    del df_tempSup_2071_2100['date']

    return (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100)












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

        proyecTemporal = ['No aplica','Anual', 'Trimestral', 'Ensamble']
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
        str_rcps_sel = str_rcps_sel.join(rcps_sel)

        
        estaciones = df_precip_sup.columns.values
        estacionesTemp = df_temp_sup.columns.values

        calcEvapot = ['No','Si']
        #Selecciona cambio proyeccion temporal
        calcEvapot_sel = request.form.getlist('calcEvapot_seleccionada')

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
                df_tempSup = df_tempSup.fillna(-1)

                df_precipSup = verif_est_precip
                #--------------------------------Generar archivo Tetis-----------------------------------------------
                archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet, 'soloTemp')

            #Seleccion = Ninguna en temperatura
            elif verif_est_temp == 'None':
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)
                df_precipSup = df_precipSup.fillna(-99)

                df_tempSup = verif_est_temp

                archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet, 'soloPrecip')


            else:
                        
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)
                df_precipSup = df_precipSup.fillna(-99)

                #--------------------------Lectura datos de temperatura---------------------------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                df_tempSup = df_tempSup.fillna(-1)
                #--------------------------------Generar archivo Tetis-----------------------------------------------
                archivoEvento(df_precipSup, df_tempSup,df_ub, precpGet, tempGet, 'precipYtemp')

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


            if proyTemporal_sel == 'Anual':
                #Seleccion = Ninguna en precipitacion
                if str_rcps_sel == '2.5':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_tempSup_2011_2040 = df_tempSup + 0.89
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 1.26
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 1.22
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        df_precipSup_2011_2040 = df_precipSup * 1.0936
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1320
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.0855
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        df_precipSup_2011_2040 = df_precipSup * 1.0936
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1320
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.0855
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                        df_tempSup_2011_2040 = df_tempSup + 0.89
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 1.26
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 1.22
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


                elif str_rcps_sel == '4.5':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_tempSup_2011_2040 = df_tempSup + 1.01
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 1.79
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 2.01
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        df_precipSup_2011_2040 = df_precipSup * 1.1089
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1221
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.1425
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        df_precipSup_2011_2040 = df_precipSup * 1.1089
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1221
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.1425
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                        df_tempSup_2011_2040 = df_tempSup + 1.01
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 1.79
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 2.01
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')

                elif str_rcps_sel == '6.0':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_tempSup_2011_2040 = df_tempSup + 0.88
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 1.58
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 2.32
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        df_precipSup_2011_2040 = df_precipSup * 1.1054
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1311
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.1724
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        df_precipSup_2011_2040 = df_precipSup * 1.1054
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1311
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.1724
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                        df_tempSup_2011_2040 = df_tempSup + 0.88
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 1.58
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 2.32
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


                elif str_rcps_sel == '8.5':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_tempSup_2011_2040 = df_tempSup + 1.06
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 2.23
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 3.68
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        df_precipSup_2011_2040 = df_precipSup * 1.1334
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1856
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.1872
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        df_precipSup_2011_2040 = df_precipSup * 1.1334
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1856
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                        df_precipSup_2071_2100 = df_precipSup * 1.1872
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                        df_tempSup_2011_2040 = df_tempSup + 1.06
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                        df_tempSup_2041_2070 = df_tempSup + 2.23
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                        df_tempSup_2071_2100 = df_tempSup + 3.68
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070, df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')

            elif proyTemporal_sel == 'Trimestral':
                if str_rcps_sel == '2.5':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)


                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------


                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


                elif str_rcps_sel == '4.5':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')

                elif str_rcps_sel == '6.0':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


                elif str_rcps_sel == '8.5':

                    if verif_est_precip == 'None':
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    #Seleccion = Ninguna en temperatura
                    elif verif_est_temp == 'None':
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        df_tempSup = verif_est_temp

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                    else:
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, str_rcps_sel)

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                        (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, str_rcps_sel)

                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


            if proyTemporal_sel == 'Ensamble':


                if verif_est_precip == 'None':
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                    df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                    df_tempSup_2011_2040 = df_tempSup + 1.09
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                    df_tempSup_2041_2070 = df_tempSup + 1.98
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                    df_tempSup_2071_2100 = df_tempSup + 2.75
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   

                    df_precipSup = verif_est_precip
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                    archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                    archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                #Seleccion = Ninguna en temperatura
                elif verif_est_temp == 'None':
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                    df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                    df_tempSup = verif_est_temp

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   


                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                    archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                    archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




                else:
                            
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                    df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                    df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                    #--------------------------------Generar archivo Tetis-----------------------------------------------

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                    df_tempSup_2011_2040 = df_tempSup + 1.09
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                    df_tempSup_2041_2070 = df_tempSup + 1.98
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                    df_tempSup_2071_2100 = df_tempSup + 2.75
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   


                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                    archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                    archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


                        

                        

            else:
                pass


        



            




        return render_template('climatologia.html', tables=[df_precip_sup.to_html(classes='data', index=False)], titles=df_precip_sup.columns.values, cambioClimatico=cambioClimatico, proyecTemporal=proyecTemporal, rcps=rcps, estaciones=estaciones, estacionesTemp=estacionesTemp, calcEvapot=calcEvapot, archivoTetis=archivoTetis)

        #return send_file(video, as_attachment=True)
            
        #return render_template('climatologia.html', result=result, result2=result2)# this redirects to my html file

    #except:
    #    return render_template('climatologia.html')


if __name__ == '__main__': #checks if our file executes directly and not imported
    app.run(debug=True) #



