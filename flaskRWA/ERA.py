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
#df_precip_sup = df_precip_sup.fillna(-1)
df_precip_sup = df_precip_sup.round(decimals=2)



#--------------------------------Información de temperatura-------------------------------------------
filenameTemp = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
cols = pd.read_csv(filenameTemp, nrows=1).columns
df_temp_sup = pd.read_csv(filenameTemp, nrows=1, usecols=cols[1:])#, usecols = columnas)

# Missing data temp in tetis = -99
#df_temp_sup = df_temp_sup.fillna(-99)
df_temp_sup = df_temp_sup.round(decimals=2)

#Estaciones para evapotranspiracion
ruta_evapot = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/estaciones_sup_evapot.csv'
cols_evapot = pd.read_csv(ruta_evapot, nrows=1).columns
df_evapot_sup = pd.read_csv(ruta_evapot, usecols=cols_evapot[0:1])

## Tabla radiacion
ruta_rad = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/radiacion.csv'
df_radiacion = pd.read_csv(ruta_rad)
df_radiacion.rename(columns={'Latitud': 'latitud'}, inplace=True)


#-----------------------------------Ubicacion estaciones precipitacion----------------------------------
def ubicacion_estaciones(ruta_ub):
    """     
    Returns the dataframe of the location of stations

            Parameters:
                    ruta_ub (String): A string with the location of the file

            Returns:
                    df_ubic (Dataframe): Dataframe with the information of the location of the stations
     """

    df_ubic = pd.read_csv(ruta_ub, usecols=['CODIGO','altitud','longitud','latitud'])
    #df_ubic = df_ubic_precdf_ubicip_sup.round(decimals=2)

    return df_ubic

def abrirArchivos(ruta, letra, columnas):
    """ 
    Returns the dataframe of the data opened

            Parameters:
                    ruta (String): A string with the location of the file
                    letra (String): A string with the identification of the data type -> P=Precipitation, T=Temperature

            Returns:
                    df_datos (Dataframe): Dataframe with the information of precipitation or temperature 

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
def archivoEvento(df_precip_sup, df_tempSup, df_evapot, df_ubi_info, precpGet, tempGet, evapotGet, nomb_archivo):
    """     
    Returns the column file format for Tetis software.

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    df_tempSup (Dataframe): A pandas dataframe with temperature data
                    df_evapot (Dataframe): A pandas dataframe with the evapotranspiration data
                    df_ubi_info (Dataframe): A pandas dataframe with the location of the stations
                    precpGet (list): List of the precipitation stations selected
                    tempGet (list): List of the temperature stations selected
                    evapotGet (list): List of the evapotranspiration stations selected
                    nomb_archivo (string): String of the file name


            Returns:
                    Tetis_file (txt file): File in the column format for Tetis software
     """

    #Check if the user selected precipitation data
    if isinstance(df_precip_sup, pd.DataFrame):
        df_precip_sup_cond = df_precip_sup.loc[0].values[0]
    else:
        df_precip_sup_cond = df_precip_sup

    #Check if the user selected temperature data
    if isinstance(df_tempSup, pd.DataFrame):
        df_temp_sup_cond = df_tempSup.loc[0].values[0]
    else:
        df_temp_sup_cond = df_tempSup

    #Check if the user selected evapotranspiration data
    if isinstance(df_evapot, pd.DataFrame):
        df_evapot_cond = df_evapot.loc[0].values[0]
    else:
        df_evapot_cond = df_evapot

    


    #---------HEADER OF THE FILE-----------------------------------------------
    Tetis_file = open(nomb_archivo+".txt","w+")
    
    #Only temperature
    if (df_precip_sup_cond == 'None' and df_evapot_cond == 'None'):
                
        
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


    #Only precipitation
    elif (df_temp_sup_cond == 'None' and df_evapot_cond == 'None'):
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

    #Temperature and evapotranspiration
    elif (df_precip_sup_cond == 'None' and isinstance(df_tempSup, pd.DataFrame) and isinstance(df_evapot, pd.DataFrame)):
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #Temperatura1
        for j in tempGet:
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])   +'\n')

        for k in evapotGet:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')


        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_tempSup,df_evapot], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Precipitation and evapotranspiration
    elif (df_temp_sup_cond == 'None' and isinstance(df_precip_sup, pd.DataFrame) and isinstance(df_evapot, pd.DataFrame)):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])   +'\n')  

        for k in evapotGet:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')



                #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_precip_sup,df_evapot], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Only evapotranspiration
    elif (df_temp_sup_cond == 'None' and df_precip_sup_cond == 'None'):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Evapotranspiration
        for k in evapotGet:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')



                #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = df_evapot
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Total---------------
    elif df_evapot_cond == 'None':
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
        #Evapotranspiration
        for k in evapotGet:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')




        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_precip_sup, df_tempSup,df_evapot], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/1950  hasta:  31/12/2021\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    Tetis_file.close()
    return Tetis_file

#-------------------------------------------------------Archivo CEDEX------------------------------------------------------------------------
def archivoCEDEX(df_precip_sup, df_tempSup, df_evapot, df_ubi_info, precpGet, tempGet, evapotGet, nomb_archivo):

    """     
    Returns the CEDEX file format for Tetis software.

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    df_tempSup (Dataframe): A pandas dataframe with temperature data
                    df_evapot (Dataframe): A pandas dataframe with the evapotranspiration data
                    df_ubi_info (Dataframe): A pandas dataframe with the location of the stations
                    precpGet (list): List of the precipitation stations selected
                    tempGet (list): List of the temperature stations selected
                    evapotGet (list): List of the evapotranspiration stations selected
                    nomb_archivo (string): String of the file name


            Returns:
                    Tetis_file (txt file): File in the CEDEX format for Tetis software
     """

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

    #Check if the user selected evapotranspiration data
    if isinstance(df_evapot, pd.DataFrame):
        df_evapot_cond = df_evapot.loc[0].values[0]
    else:
        df_evapot_cond = df_evapot

    
    #---------HEADER-----------------------------------------------
    Tetis_file = open(nomb_archivo+".txt","w+")
    
    #Only temperature
    if (df_precip_sup_cond == 'None' and df_evapot_cond == 'None'):
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")


        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  



    #Only precipitation
    elif (df_temp_sup_cond == 'None' and df_evapot_cond == 'None'):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  


    #Temperature and evapotranspiration
    elif (df_precip_sup_cond == 'None' and isinstance(df_tempSup, pd.DataFrame) and isinstance(df_evapot, pd.DataFrame)):
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")


        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  

        for k in evapotGet:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')

    #Precipitation and evapotranspiration
    elif (df_temp_sup_cond == 'None' and isinstance(df_evapot, pd.DataFrame) and isinstance(df_precip_sup, pd.DataFrame)):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  

        for k in evapotGet:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')

    #Only evapotranspiration
    elif (df_temp_sup_cond == 'None' and df_precip_sup_cond == 'None'):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Evapotranspiration
        for k in evapotGet:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')


    #Precipitation and temperature
    elif df_evapot_cond == 'None':
        #--------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        #Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  

        #Temperatura
        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  

    #Todos
    else:
        #--------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        #Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  

        #Temperatura
        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  

        #Evapotranspiration
        for k in evapotGet:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')


    Tetis_file.close()
    return Tetis_file

#------------------Trimestre Precipitacion---------------------------------
def trimestre_precip(df_precipSup, rcp_clima):
    """     
    Returns the the dataframe of the precipitation with climate change scenarios

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    rcp_clima (String): A string that for the climate change scenario selected

            Returns:
                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) (Dataframe, Dataframe, Dataframe): Dataframe with climate change scenario for timelapse of 2011-2040, 2041-2070, 2071-2100
     """

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

#---------------------Trimestre Temperatura------------------------------------------------
def trimestre_temp(df_tempSup, rcp_clima):
    """     
    Returns the the dataframe of the temperature with climate change scenarios

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    rcp_clima (String): A string that for the climate change scenario selected

            Returns:
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) (Dataframe, Dataframe, Dataframe): Dataframe with climate change scenario for timelapse of 2011-2040, 2041-2070, 2071-2100
    """
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

def calcEvapotranspiracion(df_tempSup, df_ub, df_radiacion,tempGet):
    """     
    Returns the dataframe of the evapotranspiration calculated with Turc Modified

            Parameters:
                    df_tempSup (Dataframe): A pandas dataframe with temperature data
                    df_ub (Dataframe): A pandas dataframe with the location of the stations
                    df_radiacion (Dataframe): A pandas dataframe with the location of the stations
                    tempGet (list): List of the temperature stations selected

            Returns:
                    df_tempSup (Dataframe): Dataframe of the evapotranspiration calculated
    """

    df_new = pd.DataFrame()
    HR = [82.065943, 82.91073, 85.125509, 85.536313, 85.341042, 83.060406, 80.410283, 78.7061, 79.407464, 83.32468, 85.336647, 84.15651]
    meses = ['Ene',	'Feb',	'Mar',	'Abr',	'May',	'Jun',	'Jul',	'Ago',	'Sep',	'Oct',	'Nov',	'Dic']
    K = [0.4, 0.37, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]

    df_tempSup['date'] = pd.date_range(start='01/01/1950', periods=len(df_tempSup), freq='D')
    df_tempSup.set_index('date', inplace=True)

    for i in df_tempSup.columns:
        df_new = df_new.append(df_ub.loc[df_ub.index == i])

    df_radiacion = pd.concat([df_radiacion,df_new[['latitud']]],ignore_index = False).sort_values(['latitud'], ascending=True)
    df_radiacion = df_radiacion.interpolate()

    df_evapot = pd.merge(df_new, df_radiacion, left_index=True, right_index=True)

    
    for n, j, i, in zip(range(1,13), K, HR):
        df_tempSup[df_tempSup.index.month.isin([n])] = (j * ((df_tempSup[df_tempSup.index.month.isin([n])])/((df_tempSup[df_tempSup.index.month.isin([n])])+15))) * (1+((50-i)/70))

    for m in meses:
        df_evapot[[str(m)]] = (df_evapot[[str(m)]]+50)

    for l in tempGet:
        for n, m in zip(range(1,13),meses):
            
            df_tempSup[l][df_tempSup.index.month.isin([n])] = (df_tempSup[l][df_tempSup.index.month.isin([n])] * df_evapot.loc[df_evapot.index == l, m].values[0].squeeze())

    df_tempSup = df_tempSup.fillna(-1)
    df_tempSup.reset_index(inplace=True)
    del df_tempSup['date']
    return df_tempSup


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
        
        print(cambioClimaticoSiNo)
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
        estacionesEvapot = df_evapot_sup['CODIGO'].to_numpy()



        archivoTetis = ['Columna', 'Cedex']
        #Selecciona si el archivo a generar es cedex o evento
        archivoTetis_sele = request.form.getlist('archivoTetis_sel')
        str_archivoTetis_sele = " " 
        # convert string  
        archivoTetis_sele = str_archivoTetis_sele.join(archivoTetis_sele)
        

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

            #Estaciones seleccionadas de temperatura
            evapotGet = request.form.getlist('calcEvapot_seleccionada')
            # initialize an empty string
            str_Evapot = " " 
            # convert string  
            verif_est_evapot = str_Evapot.join(evapotGet)
            #print(verif_est_evapot)

            #Seleccion = Ninguna en precipitacion y evapotranspiracion
            if (verif_est_precip == 'None' and verif_est_evapot == 'None'):
                #--------------------------Lectura datos de temperatura---------------------------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                df_tempSup = df_tempSup.fillna(-99)

                #----------------Evapotranspiracion--------------------
                #df_datos_evapot = abrirArchivos(rutaT, "T", evapotGet)
                #df_ub2 = df_ub.set_index('CODIGO')
                #df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, evapotGet)
                


                df_precipSup = verif_est_precip

                df_evapot = verif_est_evapot
                #--------------------------------Generar archivo Tetis-----------------------------------------------
                if archivoTetis_sele == 'Columna':
                    archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'soloTempColumna')

                else:
                    archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'soloTempCEDEX')

            #Seleccion = Ninguna en temperatura y evapotranspiracion
            elif (verif_est_temp == 'None' and verif_est_evapot == 'None'):
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)
                df_precipSup = df_precipSup.fillna(-1)

                df_tempSup = verif_est_temp

                df_evapot = verif_est_evapot

                #--------------------------------Generar archivo Tetis-----------------------------------------------
                if archivoTetis_sele == 'Columna':
                    archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'soloPrecipColumna')

                else:
                    archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'soloPrecipCEDEX')

            #Seleccion = Ninguna en evapotranspiracion
            elif verif_est_evapot == 'None':
                        
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)
                df_precipSup = df_precipSup.fillna(-1)

                #--------------------------Lectura datos de temperatura---------------------------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                df_tempSup = df_tempSup.fillna(-99)

                df_evapot = verif_est_evapot



                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                if archivoTetis_sele == 'Columna':
                    archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'precipYtempColumna')

                else:
                    archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'precipYtempCEDEX')

            #Ninguna en precipitacion y temperatura
            elif (verif_est_temp == 'None' and verif_est_precip == 'None'):

                #----------------Evapotranspiracion--------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_datos_evapot = abrirArchivos(rutaT, "T", evapotGet)
                df_ub2 = df_ub.set_index('CODIGO')
                df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, evapotGet)
 

                df_tempSup = verif_est_temp

                df_precipSup = verif_est_precip

                print(df_evapot)


                #--------------------------------Generar archivo Tetis-----------------------------------------------
                if archivoTetis_sele == 'Columna':
                    archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'soloEvapotColumna')

                else:
                    archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'soloEvapotCEDEX')

            #Ninguna en precipitacion
            elif (verif_est_precip == 'None'):
                #--------------------------Lectura datos de temperatura---------------------------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                df_tempSup = df_tempSup.fillna(-99)

                #----------------Evapotranspiracion--------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_datos_evapot = abrirArchivos(rutaT, "T", evapotGet)
                df_ub2 = df_ub.set_index('CODIGO')
                df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, evapotGet)
 


                df_precipSup = verif_est_precip

                #--------------------------------Generar archivo Tetis-----------------------------------------------
                if archivoTetis_sele == 'Columna':
                    archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'TempeEvapotColumna')

                else:
                    archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'TempeEvapotCEDEX')

            #Seleccion = Ninguna en temperatura
            elif (verif_est_temp == 'None'):
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)
                df_precipSup = df_precipSup.fillna(-1)

                #----------------Evapotranspiracion--------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_datos_evapot = abrirArchivos(rutaT, "T", evapotGet)
                df_ub2 = df_ub.set_index('CODIGO')
                df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, evapotGet)
 

                df_tempSup = verif_est_temp

                #--------------------------------Generar archivo Tetis-----------------------------------------------
                if archivoTetis_sele == 'Columna':
                    archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'PrecipEvapotColumna')

                else:
                    archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'PrecipEvapotCEDEX')


            else:
                        
                #--------------------------Lectura datos de precipitación-------------------------------------
                rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                df_precipSup = abrirArchivos(rutaP, "P", precpGet)
                df_precipSup = df_precipSup.fillna(-1)

                #--------------------------Lectura datos de temperatura---------------------------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                df_tempSup = df_tempSup.fillna(-99)

                #----------------Evapotranspiracion--------------------
                rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                df_datos_evapot = abrirArchivos(rutaT, "T", evapotGet)
                df_ub2 = df_ub.set_index('CODIGO')
                df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, evapotGet)
 

                #--------------------------------Generar archivo Tetis-----------------------------------------------
                if archivoTetis_sele == 'Columna':
                    archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'PrecipTempEvapotColumna')

                else:
                    archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'PrecipTempEvapotCEDEX')

        elif cambioClimaticoSiNo == 'Si':
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

            #Estaciones seleccionadas de temperatura
            evapotGet = request.form.getlist('calcEvapot_seleccionada')
            # initialize an empty string
            str_Evapot = " " 
            # convert string  
            verif_est_evapot = str_Evapot.join(evapotGet)


            if proyTemporal_sel == 'Anual':
                #Seleccion = Ninguna en precipitacion
                if str_rcps_sel == '2.5':

                    #Ninguna precipitacion
                    if (verif_est_precip == 'None' and verif_est_temp != 'None' and verif_est_evapot != 'None'):
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_ub2 = df_ub.set_index('CODIGO')

                        df_tempSup_2011_2040 = df_tempSup + 0.89

                        df_tempSup_2041_2070 = df_tempSup + 1.26

                        df_tempSup_2071_2100 = df_tempSup + 1.22

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 


                        

                                                
                        #----------------Evapotranspiracion--------------------
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)

                        df_evapo_2011_2040 = df_evapo + 0.89
                        df_evapo_2041_2070 = df_evapo + 1.26
                        df_evapo_2071_2100 = df_evapo + 1.22


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)      



                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_tempEvapot_2011_2040Columna')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_tempEvapot_2041_2070Columna')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_tempEvapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_tempEvapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_tempEvapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_tempEvapot_2071_2100CEDEX')
   
                    #Ninguna en temperatura
                    elif (verif_est_precip != 'None' and verif_est_temp == 'None' and verif_est_evapot != 'None'):
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


                                                
                        #----------------Evapotranspiracion--------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)
                        df_ub2 = df_ub.set_index('CODIGO')

                        df_evapo_2011_2040 = df_evapo + 0.89
                        df_evapo_2041_2070 = df_evapo + 1.26
                        df_evapo_2071_2100 = df_evapo + 1.22


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)      


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipEvapot_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipEvapot_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipEvapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipEvapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipEvapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipEvapot_2071_2100CEDEX')

                    #Ninguna en evapotranspiracion
                    elif (verif_est_precip != 'None' and verif_est_temp != 'None' and verif_est_evapot == 'None'):
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        df_precipSup_2011_2040 = df_precipSup * 1.0936
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1320
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 

                        df_precipSup_2071_2100 = df_precipSup * 1.0855
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                        df_tempSup_2011_2040 = df_tempSup + 0.89
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                        df_tempSup_2041_2070 = df_tempSup + 1.26
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                        df_tempSup_2071_2100 = df_tempSup + 1.22
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   

                        df_evapot = verif_est_evapot

                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTemp_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTemp_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTemp_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTemp_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTemp_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTemp_2071_2100CEDEX')

                    #Solo temperatura
                    elif (verif_est_precip == 'None' and verif_est_temp != 'None' and verif_est_evapot == 'None'):
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_ub2 = df_ub.set_index('CODIGO')

                        df_tempSup_2011_2040 = df_tempSup + 0.89

                        df_tempSup_2041_2070 = df_tempSup + 1.26

                        df_tempSup_2071_2100 = df_tempSup + 1.22

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                        df_evapot = verif_est_evapot

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_temp_2011_2040Columna')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_temp_2041_2070Columna')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_temp_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_temp_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_temp_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_temp_2071_2100CEDEX')
 
                    #Solo precipitación
                    elif (verif_est_precip != 'None' and verif_est_temp == 'None' and verif_est_evapot == 'None'):
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


                                                
                        #----------------Evapotranspiracion--------------------
                        df_evapot = verif_est_evapot  


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precip_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precip_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precip_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precip_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precip_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precip_2071_2100CEDEX')

                    #Solo evapotranspiracion
                    elif (verif_est_precip == 'None' and verif_est_temp == 'None' and verif_est_evapot != 'None'):
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        df_precipSup = verif_est_precip


                        df_tempSup = verif_est_temp




                                                
                        #----------------Evapotranspiracion--------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)
                        df_ub2 = df_ub.set_index('CODIGO')

                        df_evapo_2011_2040 = df_evapo + 0.89
                        df_evapo_2041_2070 = df_evapo + 1.26
                        df_evapo_2071_2100 = df_evapo + 1.22


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)      


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_Evapot_2011_2040Columna')
                            archivoEvento(df_precipSup, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_Evapot_2041_2070Columna')
                            archivoEvento(df_precipSup, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_Evapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_Evapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_Evapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_Evapot_2071_2100CEDEX')

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

                        #----------------Evapotranspiracion--------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)
                        df_ub2 = df_ub.set_index('CODIGO')

                        df_evapo_2011_2040 = df_evapo + 0.89
                        df_evapo_2041_2070 = df_evapo + 1.26
                        df_evapo_2071_2100 = df_evapo + 1.22


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)     


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTempEvapot_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTempEvapot_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTempEvapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTempEvapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTempEvapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_2.5_precipTempEvapot_2071_2100CEDEX')



                elif str_rcps_sel == '4.5':

                    #Ninguna precipitacion
                    if (verif_est_precip == 'None' and verif_est_temp != 'None' and verif_est_evapot != 'None'):
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_ub2 = df_ub.set_index('CODIGO')

                        df_tempSup_2011_2040 = df_tempSup + 1.01

                        df_tempSup_2041_2070 = df_tempSup + 1.79

                        df_tempSup_2071_2100 = df_tempSup + 2.01

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 


                        

                                                
                        #----------------Evapotranspiracion--------------------
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)

                        df_evapo_2011_2040 = df_evapo + 1.01
                        df_evapo_2041_2070 = df_evapo + 1.79
                        df_evapo_2071_2100 = df_evapo + 2.01


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)      



                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_tempEvapot_2011_2040Columna')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_tempEvapot_2041_2070Columna')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_tempEvapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_tempEvapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_tempEvapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_tempEvapot_2071_2100CEDEX')
   

                    #Ninguna en temperatura
                    elif (verif_est_precip != 'None' and verif_est_temp == 'None' and verif_est_evapot != 'None'):
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


                                                
                        #----------------Evapotranspiracion--------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)
                        df_ub2 = df_ub.set_index('CODIGO')

                        df_evapo_2011_2040 = df_evapo + 1.01
                        df_evapo_2041_2070 = df_evapo + 1.79
                        df_evapo_2071_2100 = df_evapo + 2.01


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)      


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipEvapot_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipEvapot_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipEvapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipEvapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipEvapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipEvapot_2071_2100CEDEX')

                    #Ninguna en evapotranspiracion
                    elif (verif_est_precip != 'None' and verif_est_temp != 'None' and verif_est_evapot == 'None'):
                                
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        rutaP = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/precipitacion_sup.csv'
                        df_precipSup = abrirArchivos(rutaP, "P", precpGet)

                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)
                        #--------------------------------Generar archivo Tetis-----------------------------------------------

                        df_precipSup_2011_2040 = df_precipSup * 1.1089
                        df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 

                        df_precipSup_2041_2070 = df_precipSup * 1.1221
                        df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 

                        df_precipSup_2071_2100 = df_precipSup * 1.1425
                        df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                        df_tempSup_2011_2040 = df_tempSup + 1.01
                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                        df_tempSup_2041_2070 = df_tempSup + 1.79
                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                        df_tempSup_2071_2100 = df_tempSup + 2.01
                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   

                        df_evapot = verif_est_evapot

                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTemp_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTemp_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTemp_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTemp_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTemp_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTemp_2071_2100CEDEX')

                    #Solo temperatura
                    elif (verif_est_precip == 'None' and verif_est_temp != 'None' and verif_est_evapot == 'None'):
                        #--------------------------Lectura datos de temperatura---------------------------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_tempSup = abrirArchivos(rutaT, "T", tempGet)

                        df_ub2 = df_ub.set_index('CODIGO')

                        df_tempSup_2011_2040 = df_tempSup + 1.01

                        df_tempSup_2041_2070 = df_tempSup + 1.79

                        df_tempSup_2071_2100 = df_tempSup + 2.01

                        df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                        df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                        df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                        df_evapot = verif_est_evapot

                        df_precipSup = verif_est_precip
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_temp_2011_2040Columna')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_temp_2041_2070Columna')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_temp_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_temp_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_temp_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_temp_2071_2100CEDEX')
 
                    #Solo precipitación
                    elif (verif_est_precip != 'None' and verif_est_temp == 'None' and verif_est_evapot == 'None'):
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


                                                
                        #----------------Evapotranspiracion--------------------
                        df_evapot = verif_est_evapot  


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precip_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precip_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precip_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precip_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precip_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup, df_evapot, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precip_2071_2100CEDEX')

                    #Solo evapotranspiracion
                    elif (verif_est_precip == 'None' and verif_est_temp == 'None' and verif_est_evapot != 'None'):
                        #--------------------------Lectura datos de precipitación-------------------------------------
                        df_precipSup = verif_est_precip


                        df_tempSup = verif_est_temp




                                                
                        #----------------Evapotranspiracion--------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)
                        df_ub2 = df_ub.set_index('CODIGO')

                        df_evapo_2011_2040 = df_evapo + 1.01
                        df_evapo_2041_2070 = df_evapo + 1.79
                        df_evapo_2071_2100 = df_evapo + 2.01


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)      


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_Evapot_2011_2040Columna')
                            archivoEvento(df_precipSup, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_Evapot_2041_2070Columna')
                            archivoEvento(df_precipSup, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_Evapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_Evapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_Evapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_Evapot_2071_2100CEDEX')

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

                        #----------------Evapotranspiracion--------------------
                        rutaT = 'C:/Users/Bender/Desktop/Mapas_ERA/Anexos_Final/Anexo A series IDEAM bruta/temperatura_sup.csv'
                        df_evapo = abrirArchivos(rutaT, "T", evapotGet)
                        df_ub2 = df_ub.set_index('CODIGO')

                        df_evapo_2011_2040 = df_evapo + 1.01
                        df_evapo_2041_2070 = df_evapo + 1.79
                        df_evapo_2071_2100 = df_evapo + 2.01


                        df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, evapotGet)
                        df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, evapotGet)     


                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTempEvapot_2011_2040Columna')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTempEvapot_2041_2070Columna')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTempEvapot_2071_2100Columna')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTempEvapot_2011_2040CEDEX')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTempEvapot_2041_2070CEDEX')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, precpGet, tempGet, evapotGet, 'anual_4.5_precipTempEvapot_2071_2100CEDEX')



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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')
                            
                        else:    
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')

                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')





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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070, df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070, df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')

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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')

                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')





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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')

                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')



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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')
                        
                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')

                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')




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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')

                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')





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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')



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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                        else:
                            archivoCEDEX(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                            archivoCEDEX(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                            archivoCEDEX(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')


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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')





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
                        if archivoTetis_sele == 'Columna':
                            archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')
                        
                        else:
                            archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'precip_2011_2040')
                            archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'precip_2041_2070')
                            archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'precip_2071_2100')


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
                    if archivoTetis_sele == 'Columna':
                        archivoEvento(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoEvento(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoEvento(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')

                    else:
                        archivoCEDEX(df_precipSup, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'temp_2011_2040')
                        archivoCEDEX(df_precipSup, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'temp_2041_2070')
                        archivoCEDEX(df_precipSup, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'temp_2071_2100')


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
                    if archivoTetis_sele == 'Columna':
                        archivoEvento(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')
                    else:
                        archivoCEDEX(df_precipSup_2011_2040, df_tempSup,df_ub, precpGet, tempGet, 'precip_2011_2040')
                        archivoCEDEX(df_precipSup_2041_2070, df_tempSup,df_ub, precpGet, tempGet, 'precip_2041_2070')
                        archivoCEDEX(df_precipSup_2071_2100, df_tempSup,df_ub, precpGet, tempGet, 'precip_2071_2100')





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
                    if archivoTetis_sele == 'Columna':
                        archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'datos_2011_2040')
                        archivoEvento(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'datos_2041_2070')
                        archivoEvento(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'datos_2071_2100')

                    else:
                        archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040,df_ub, precpGet, tempGet, 'datos_2011_2040')
                        archivoCEDEX(df_precipSup_2041_2070, df_tempSup_2041_2070,df_ub, precpGet, tempGet, 'datos_2041_2070')
                        archivoCEDEX(df_precipSup_2071_2100, df_tempSup_2071_2100,df_ub, precpGet, tempGet, 'datos_2071_2100')



                        

                        

            else:
                pass

        else:
            pass

        



            




        return render_template('climatologia.html', tables=[df_precip_sup.to_html(classes='data', index=False)], titles=df_precip_sup.columns.values, cambioClimatico=cambioClimatico, proyecTemporal=proyecTemporal, rcps=rcps, estaciones=estaciones, estacionesTemp=estacionesTemp, estacionesEvapot=estacionesEvapot, archivoTetis=archivoTetis)

        #return send_file(video, as_attachment=True)
            
        #return render_template('climatologia.html', result=result, result2=result2)# this redirects to my html file

    #except:
    #    return render_template('climatologia.html')


if __name__ == '__main__': #checks if our file executes directly and not imported
    app.run(debug=True) #


