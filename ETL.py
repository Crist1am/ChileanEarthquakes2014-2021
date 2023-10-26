#importamos las librerias necesarias
import pandas as pd
import numpy as np
import os


#ETL

# Obtener el directorio actual
path_var = os.getcwd()
path_interno = '/Dataset/sismos_chile_2012_2022.csv'

ruta = path_var+path_interno
df_sismos = pd.read_csv(ruta)

#un vistazo a los primeros 5 datos del df

print("\nPrimeras 5 filas del data set \n\n",df_sismos.head())

#dimension del df
print('\nLa dimension del df es',df_sismos.shape)
'Vemos que el df cuenta con 22 columnas y 10043 datos'

#columnas del df
print('\nLas columnas de df son:',df_sismos.columns)

#Elegimos las columnas de interes
col_interes = ['time', 'latitude', 'longitude', 'depth', 'mag', 'magType',
        'dmin', 'place']

#definimos el df a tratar
df = df_sismos[col_interes]
print('\nEl nuevo df es:\n\n',df)

#limpieza de datos
'vemos los valores nulos en el nuevo df'
print('\nLos valores nulos del df por columna:\n',df.isnull().sum())

'''vemos que la columna "dmin" es la que posee 2040 nulos y la columna "place" 5.
Como los 2045 datos equivalen al 20% del total, eliminamos las filas para no alterar los datos'''

#eliminamos las filas con datos nulos en ambas columnas
df = df.dropna(subset=["dmin", "place"]).reset_index(drop=True)
print('\nEl nuevo df sin nulos en columna <dmin> y <place>:\n',df)
print('\nLa nueva dimension del df es',df.shape)

#extraemos el pais de la columna 'place' y lo añadimos a una nueva columna
df['country'] = df['place'].str.split(',').str[-1].str.strip()

#extraemos la ciudad de la columna 'place' y lo añadimos a una nueva columna
df['city'] = df['place'].str.extract(r'of\s+(.*?),')

#eliminamos la columna 'place' ya que descompusimos la informacion clave
df.drop(columns=['place'], axis=1, inplace=True)

#creamos una nueva columna llamanda 'range' para agrupar las magnitudes
    #definimos lo intervalos y los labels
bins = [1.0, 3.0, 5.0, 7.0, 9.0]
labels = ['1.0 - 2.9', '3.0 - 4.9', '5.0 - 6.9', '7.0 - 8.9']

    #creamos la columna
df['range'] = pd.cut(df['mag'], bins=bins, labels=labels, right=False)
#print(df)

'''Segun el origen de la base de datos, 'dmin' corresponde a la distancia horizontal entre el epicentro del sismo
y la estación más cercana (en grados), donde 1 grado equivale a 111.2 kilometros aproximadamente, por lo que 
transformamos la unidad de medida'''

#transformamos la unidad de medida de la columna 'dmin' (de grado a km)
df['dmin'] = (df['dmin'] * 111.2).round(3)

#vemos el nuevo df
print('\nUn resumen de datos en cada columna del df:\n')
df.info()

#vemos las filas con nulos en columna 'city'
filas_con_nulos = df[pd.isnull(df['city'])]
print('\nLas filas con nulos:\n\n',filas_con_nulos)
'''Como vemos, son datos que no tienen un país en especifico y por ende una ciudad tampoco
entonces borramos estos datos nulos en columna <city>'''

#eliminamos los nulos en columna city que se generaron al descomponer la columna 'place'
df = df.dropna(subset=["city"]).reset_index(drop=True)

#vemos el df final
print('\nEl df final sin valores nulos:\n\n',df)

#transforamos la columna 'time' a tipo tiempo en formato año-mes-dia hora-minutos
df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%dT%H:%M:%S.%fZ')

#Creamos las columnas 'day', 'month', 'year', 'hour' y 'minute'
df['day'] = df['time'].dt.day
df['month'] = df['time'].dt.month
df['year'] = df['time'].dt.year
df['hour'] = df['time'].dt.hour
df['minutes'] = df['time'].dt.minute

#Ordenamos los datos por fecha para ver cuando comenzó la base de datos
dates = df.sort_values(by='time')
print('\nComienzo de la base de datos\n', dates)

'''Como vemos, los datos comienzan el 2 de agosto de 2013, por lo que este año no está completo,
se opta por eliminarlos y que la base de datos comience en el año 2014 '''

#Eliminamos las filas correspondientes al año 2013 del df 
df = df[df['time'].dt.year >= 2014]

#Verificamos que el df comience en 2014-01-01
dates = df.sort_values(by='time')
print('\nVerificación del comienzo del df\n', dates)

#vemos nuevamente el df
print('\nEl detalle de cada columna del df final\n')
df.info()

'''ahora el df se encuentra limpio, sin nulos o informacion incompleta y con las columnas de interes.'''

#Como cada sismo no ocurre al mismo tiempo, creamos un ID distinto para cada dato
df['ID_Date'] = 'Date_' + (df.index + 1).astype(str).str.zfill(4)

#De la misma manera, para cada ubicacion creamos un ID distinto, ya que es poco probable que ocurran exactamente en el mismo punto
df['ID_Place'] = 'Place_' + (df.index + 1).astype(str).str.zfill(4)

#La columna magType la transformaremos en ID_Mag
df.rename(columns={'magType': 'ID_Mag'}, inplace=True)

#Creamos una nueva columna llamada 'magnitude_name' para saber de que trata ID_Mag
    #Condiciones y sus valores correspondientes para la columna 'magnitude_name'
condiciones = [
    (df['ID_Mag'] == 'mb'), 
    (df['ID_Mag'] == 'mb_lg'), 
    (df['ID_Mag'] == 'md'),
    (df['ID_Mag'] == 'ml'), 
    (df['ID_Mag'] == 'mwb'),
    (df['ID_Mag'] == 'mwc'), 
    (df['ID_Mag'] == 'mwr'),
    (df['ID_Mag'] == 'mww')
]

valores = ['Magnitud de ondas internas', 'Magnitud a partir de la amplitud de la fase Lg',
            'Magnitud de duracion', 'Magnitud local', 'Magnitud de momento','Magnitud de momento',
            'Magnitud de momento','Magnitud de momento']

#Creamos la nueva columna 'magnitude_name'
df['magnitude_name'] = np.select(condiciones, valores, default='Otro tipo de magnitud')

#vemos la base de datos limpia y con las columnas de ID
print('\ndf limpio con columnas de ID\n\n', df)


#Separamos el df en 4 df linkeadas mediante los ID creados
col_fecha=['ID_Date', 'time','day','month','year','hour','minutes']
col_ubi=['ID_Place','country', 'city', 'latitude', 'longitude']
col_mag=['ID_Mag', 'magnitude_name']
col_sismos=['ID_Date', 'ID_Place', 'ID_Mag', 'mag', 'depth', 'dmin']



fecha=df[col_fecha]
ubicacion=df[col_ubi]
magnitud=df[col_mag]
sismos=df[col_sismos]


#vemos los nuevos df separados
names = ['fecha', 'ubicacion', 'magnitud', 'sismos']
for i in names:
    dfs = globals()[i]  #Esto accede al DataFrame utilizando el nombre almacenado 'names'
    print(f'\ndf de {i}:\n', dfs)

#Guardamos cada DataFrame en su archivo CSV correspondiente 
df_names = [df,fecha, ubicacion, magnitud, sismos]
for i, df in enumerate(df_names):
    nombre_archivo = ['Sismos_Chile_Limpio','Fecha', 'Ubicacion', 'Magnitud', 'Sismos'][i]
    df.to_csv(f'{path_var}/Dataset/{nombre_archivo}.csv', index=False)
