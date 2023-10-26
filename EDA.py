import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

# Obtenemos los csv limpios
path_var = os.getcwd()
path_interno = '/Dataset/'
archivos = ['Fecha', 'Magnitud', 'Sismos', 'Ubicacion']
dataframes = {}

for i in archivos:
    ruta = path_var + path_interno
    archivo_ruta = f'{ruta}{i}.csv'
    dataframes[i] = pd.read_csv(archivo_ruta)

# Cambiamos los nombres de los df
df_fecha = dataframes['Fecha']
df_magnitud = dataframes['Magnitud']
df_sismos = dataframes['Sismos']
df_ubicacion = dataframes['Ubicacion']



# Vemos los sismos de mayor magnitud por año
merge_1 = pd.merge(df_fecha, df_sismos, on='ID_Date', how='inner')
max_mag_year = merge_1.groupby('year')['mag'].max()

## graficamos 
plt.figure(figsize=(10, 6))
fig = px.line(max_mag_year, x=max_mag_year.index, y=max_mag_year.values,
            title='Magnitud máxima de sismos por Año',
            )
fig.update_layout(
    xaxis_title='Año', 
    yaxis_title='Magnitud máxima',  
)
fig.show()

'''Segun el grafico, vemos que entre los años 2014 y 2021, el 2015 fue donde ocurrió el sismo de mayor magnitud percibido en Chile,
por lo que veremos en detalle ese año '''



# Filtramos df_fecha para incluir solo los datos del año 2015
df_fecha_2015 = df_fecha[df_fecha['year'] == 2015]

## Fusionar df_fecha_2015 con df_sismos
merge_2 = pd.merge(df_fecha_2015, df_sismos, on='ID_Date', how='inner')
mag_year_2015 = merge_2.groupby('month')['mag'].agg(['max', 'min', 'mean', 'count'])


## Veamos los maximos, minimos y promedios de cada mes en 2015
plt.figure(figsize=(10, 6))
fig = px.line(mag_year_2015, x=mag_year_2015.index, y=['max', 'min', 'mean'],
              title='Magnitud máxima, mínima y promedio en 2015',
              color_discrete_sequence=['blue', 'green', 'red'])
fig.update_layout(
    xaxis_title='Mes', 
    yaxis_title='Magnitud',  
)
fig.show()


"""Segun lo que se ve en el segundo gráfico, en septiembre fue cuando ocurrió el terremoto de 8.3, 
sin embargo, el promedio de ese año fue muy parejo, alrededor de 4.5, pese a que en septiembre hay un maximo de 8.3.
Esto puede deberse a una alta cantidad de sismos de menor magnitud en ese mes, haciendo que disminuya el promedio"""

## Veamos la cantidad de sismos por mes
plt.figure(figsize=(10, 6))
fig = px.bar(mag_year_2015, x=mag_year_2015.index, y='count',
              title='Cantidad de sismos por mes en 2015')
fig.update_layout(
    xaxis_title='Meses', 
    yaxis_title='Frecuencia',  
)
fig.show()


# Veamos en que año hubo más sismos
cant_sismos = df_fecha.groupby('year')['ID_Date'].count().reset_index()

## Graficamos
plt.figure(figsize=(10, 6))
fig = px.pie(cant_sismos, values='ID_Date', names='year', title='Cantidad de sismos por Año')
fig.show()

"""Podemos ver que en 2015 fue el año con mayor cantidad de sismos, algo habitual en años donde hay terremoto,
sin embargo no es sinonimo de correlación, es decir, pueden haber años con seguidillas de temblores, pero no significa
que habrá un terremoto"""



#Ahora veamos la cantidad de sismos por país
merge_3 = pd.merge(df_ubicacion, df_sismos, on='ID_Place', how='inner')
cant_sismos_pais = merge_3.groupby('country')['mag'].agg(['max', 'min', 'mean', 'count'])
print(cant_sismos_pais)

# Graficamos
plt.figure(figsize=(10, 6))
fig = px.pie(cant_sismos_pais, values='count', names=cant_sismos_pais.index, title='Cantidad de sismos por país')
fig.show()


## Veamos los maximos, minimos y promedios en cada país
plt.figure(figsize=(10, 6))
fig = px.line(cant_sismos_pais, x=cant_sismos_pais.index, y=['max', 'min', 'mean'],
              title='Magnitud máxima, mínima y promedio en Argentina, Bolivia, Chile y Perú',
              color_discrete_sequence=['blue', 'green', 'red'])
fig.update_layout(
    xaxis_title='País', 
    yaxis_title='Magnitud',  
)
fig.show()