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
df = df.astype({'english':object,'required_age':object})
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
cat_data = cat_data.drop(labels = ['genres','steamspy_tags','categories','english'] ,axis='columns')



cat_data['platforms'].value_counts().sort_values(ascending=False).plot(kind='bar')



cat_freq = [df_genres,df_categories]
df_categories.sort_values(by='Frecuencia',ascending=False)[0:13].plot(kind='bar',legend=False,edgecolor='black')
df_genres.sort_values(by='Frecuencia',ascending=False)[0:13].plot(kind='bar',legend=False,edgecolor='black')




#%%Plot categorico
import  matplotlib.pyplot as plt
X1,X2 = [ (2,3,i,j) for i,j in zip(range(1,4),list(cat_data.columns)) ] , [ [2,2,i,j] for i,j in zip(range(3,5),cat_freq) ]

units = [' (-)']*10
props,props2 = dict(boxstyle='round', facecolor='wheat', alpha=0.5),dict(boxstyle='round', facecolor='aqua', alpha=0.5)
k=0
fig =plt.figure(figsize=(12,6))
for nrows, ncols, plot_number,atr in  X1:
    ax = fig.add_subplot(nrows, ncols, plot_number)
    cat_data[atr].value_counts().sort_values(ascending=False).plot(ax=ax,kind='bar',edgecolor='black')
    plt.xticks(rotation=90)
    # place a text box in upper left in axes coords
    ax.text(0.34, 0.8, atr, transform=ax.transAxes, fontsize=14,verticalalignment='top', bbox=props)
    if k==0:
        ax.set_ylabel('$Frecuencia$ (-)',size=18)
    if k==1:
        ax.set_xlabel('$Valor ~ categórico$ (-)',size=18)
    k+=1
plt.savefig('Categories1.png',dpi=1000,bbox_inches='tight')
fig =plt.figure(figsize=(12,6))     
k=0    
for nrows, ncols, plot_number,dfplot in X2:
    ax = fig.add_subplot(nrows, ncols, plot_number)
    dfplot.sort_values(by='Frecuencia',ascending=False).plot(ax=ax,kind='bar',legend=False)
    ax.text(0.5, 0.8, dfplot.columns[1], transform=ax.transAxes, fontsize=18,verticalalignment='top', bbox=props)
    if k==0:
        ax.set_ylabel('$Frecuencia$ (-)',size=18)
        ax.set_xlabel('                                                 $Valor ~ categórico$ (-)',size=18)
    k+=1

plt.savefig('Categories2.png',dpi=1000,bbox_inches='tight')



#%% VARIABLES NUMERICAS

num_data = df[ [ df.columns[i] for i in range(len(types_data)) if types_data[i] != object  ]  ]
print('Resumen de Atributos Numericos:')
num_data.describe()
num_data = num_data.drop(labels = ['appid'] ,axis='columns')

cbar = sns.heatmap(data=np.round(num_data.corr(),2), annot=True,cmap = "GnBu", 
                             cbar_kws={'label': 'Correlación Pearson [-]'})
plt.savefig('Corr.png',dpi=1000,bbox_inches='tight')

num_data = num_data.drop(labels = ['average_playtime'] ,axis='columns')

#%% 
from matplotlib import axes
groups = [iatr for iatr in num_data.columns] #[ ['required_age'],['median_playtime'], ['achievements','positive_ratings','negative_ratings','price'] ]
fig, axes = plt.subplots(ncols=3,nrows=2,figsize=(8,4))

outliersTF = [True,False,False,False,True] + [False]

for i, group, ax in zip(range(len(groups)),groups,axes.flat):
  sns.boxplot(ax=ax, x = group, data= num_data ,showfliers=True) #pd.melt(num_data.loc[:,group])
  ax.set_xscale('log')
plt.tight_layout()

#%%
num_data['pos_r/tot_r'] = np.array(num_data['positive_ratings'])/(np.array(num_data['positive_ratings'])+np.array(num_data['negative_ratings']))

units,sign,alphas = ['(-)','(-)','(-)','(hr)','(£)','(%)'],[None]*5+[2],[1]*5+[0.9]
k=0
import matplotlib.ticker as ticker
fig, axes = plt.subplots(ncols=3,nrows=2,figsize=(12,5))
atributes = list(num_data.columns)
for atr, ax in zip(atributes,axes.flat):
    ax.hist(num_data[atr],bins=100,color = 'blue', edgecolor = 'black',alpha=0.8)
    #sns.distplot(ax=ax,data = num_data[atr], hist = True, kde = True)
    median, mean = round(np.median(num_data[atr]), ndigits= sign[k] ) , round(np.mean(num_data[atr]), ndigits= sign[k] )
    if k < 5:
        ax.text(0.35, 0.9, atr +' ' +units[k] ,
            transform=ax.transAxes, fontsize=14,verticalalignment='top', bbox=props,alpha=alphas[k])
        ax.text(0.35, 0.75, 'Median = '+str(median)+'\nMean = '+str(mean) ,
            transform=ax.transAxes, fontsize=14,verticalalignment='top', bbox=props,alpha=alphas[k])
    ax.set_yscale('log')
    if k==3:
        ax.set_ylabel('$Frecuencia$ (-) [Escala Log]',size=18)
        ax.yaxis.set_label_coords(-0.1,1.1)
        x_labels = ax.get_xticks()
        ax.set_xticklabels(ax.get_xticks(), rotation = 30)
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
    if k==4:
        ax.set_xlabel('$Valor ~ numérico$',size=18)
       
    k+=1
    
bboxAnn = dict(boxstyle="round", facecolor='wheat',alpha=0.9)
arrowprops = dict( arrowstyle="->",color='blue') #, connectionstyle="angle,angleA=0,angleB=90,rad=10")
ax.annotate(' $\\frac{positive\\_ratings}{(positive\\_ratings+negative\\_ratings)}$ ' ,
    (0.5, 0.5),
    xytext=(0.15,0.2), xycoords='axes fraction',
    bbox=bboxAnn, arrowprops=arrowprops,fontsize=16)
#ax.text(0.15,0.2, '$\\frac{positive\\_ratings}{(positive\\_ratings+negative\\_ratings)}$' ,
#    transform=ax.transAxes, fontsize=14, bbox=bboxAnn,alpha=0.9)


plt.tight_layout()
plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0.15)
plt.savefig('Num.png',dpi=1000,bbox_inches='tight')
#for i,column in enumerate(atributes):
#  axes = plt.subplot(G[1, i  ])
#  sns.histplot(ax=axes,data=num_data,x=column)


df_order_owners = df.sort_values(by='owners',ascending=False)
df_order_owners.name

