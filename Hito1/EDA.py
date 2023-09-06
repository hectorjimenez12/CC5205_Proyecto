# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 22:56:35 2023

@author: HJ
"""

import pandas as pd
import requests
import seaborn as sns
import datetime
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
pd.set_option('display.max_columns', 50)

#%% Cargar data
url = 'https://raw.githubusercontent.com/hectorjimenez12/Mineria_Datos/main/steam.csv'
df = pd.read_csv(url)
df.head()


#%% Describir data frame
df = df.astype({'english':object})
print('Info:')
print(df.info())
types_data = df.dtypes.values


#%% Dates

df_dates = df.loc[:,['release_date']]
df_dates.index = pd.to_datetime(df_dates['release_date'],format='%Y-%m-%d')  #[ datetime.date( int(i.split('-')[0]) ,int(i.split('-')[1]) ,int(i.split('-')[2]) ) for i in df_dates['release_date'].values ]
df_dates['count'] = 1
df_dates.head()
#grouped = df_dates.groupby( df_dates['release_date'].map(lambda x: x.year) )
grouped = df_dates.resample( rule = 'Y' ).agg(['sum'])
grouped.columns = df_dates.columns
plt.plot(grouped.iloc[:-1,1])
plt.xlabel('Año');plt.ylabel('Numero de juegos liberados en Steam [-]')



#%% VARIABLES CATEGORICAS
cat_data = df[ [ df.columns[i] for i in range(len(types_data)) if types_data[i] == object  ]  ]
print('Resumen de Atributos Numericos:')
print(cat_data.describe())
#np.unique(cat_data.developer);np.unique(cat_data.publisher)
cat_data = cat_data.drop(labels = ['name','release_date','developer','publisher'] ,axis='columns')


def melt_genres(df,atr):
    list_atr = list(df[atr].map(lambda x: x.split(';')))
    uniques = np.unique(sum(list_atr,[]))
    dict_count = {iatr:0 for iatr in uniques}
    for ilist in list_atr:
        for val in ilist:
            dict_count.update({val:dict_count.get(val)+1})
    dfcount = pd.DataFrame.from_dict(dict_count,orient='index')
    dfcount[atr] = dfcount.index
    dfcount.columns = ['Frecuencia',atr]
    return dfcount

df_genres, df_steamspy, df_categories = melt_genres(df, 'genres'),melt_genres(df, 'steamspy_tags'),melt_genres(df, 'categories')
cat_data = cat_data.drop(labels = ['genres','steamspy_tags','categories'] ,axis='columns')



cat_data['platforms'].value_counts().sort_values(ascending=False).plot(kind='bar')

cat_freq = [df_genres,df_categories]
df_categories.sort_values(by='Frecuencia',ascending=False).plot(kind='bar',legend=False)
df_genres.sort_values(by='Frecuencia',ascending=False).plot(kind='bar',legend=False)




#%%Plot categorico
import  matplotlib.pyplot as plt
X1,X2 = [ (2,3,i,j) for i,j in zip(range(1,4),list(cat_data.columns)) ] , [ [2,2,i,j] for i,j in zip(range(3,5),cat_freq) ]

fig =plt.figure(figsize=(12,6))
for nrows, ncols, plot_number,atr in  X1:
    ax = fig.add_subplot(nrows, ncols, plot_number)
    cat_data[atr].value_counts().sort_values(ascending=False).plot(ax=ax,kind='bar')
    ax.set_title(atr);plt.xticks(rotation=90)
for nrows, ncols, plot_number,df in X2:
    ax = fig.add_subplot(nrows, ncols, plot_number)
    df.sort_values(by='Frecuencia',ascending=False).plot(ax=ax,kind='bar',legend=False)
    ax.set_title(df.columns[1]);plt.xticks(rotation=90)
#plt.figtext(0.5, 0.4, 'Frecuencia de generos y categorias', ha='center', va='center',
#            size=25)
fig.subplots_adjust(bottom=0.025, left=0.025, top = 0.975, right=0.975,hspace=1)
plt.savefig('plot.png',dpi=1000,bbox_inches='tight')




