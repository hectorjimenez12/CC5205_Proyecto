# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 22:56:35 2023

@author: HJ
"""

#library
import json
import numpy as np
import pandas as pd
import requests
import pickle
import os
import pdb
pd.set_option('display.max_columns', 50)

os.chdir('C:/Users/hecto/OneDrive/Documentos/GitHub/Cursos_U/CC5205/CC5205_Proyecto/')
#https://medium.com/@senchooo/scraping-all-game-in-steam-using-python-e9f0ad206add
#https://andrew-muller.medium.com/scraping-steam-user-reviews-9a43f9e38c92
#https://nik-davis.github.io/posts/2019/steam-data-collection/
#https://github.com/TR-1000/GameScraper
#https://geezam.com/steam-api-with-python/

#%% Web Scraping 
from bs4 import BeautifulSoup

def get_n_appids(n=100,pageN=0):
    #pdb.set_trace()
    appids = []
    url = 'https://store.steampowered.com/search?category1=998&page='#'https://store.steampowered.com/search?category1=998&ndl='
    page = pageN
    while len(appids) < n:
        #print(page)
        page += 1
        response = requests.get(url=url+str(page), headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser') #Nrows = len(soup.find_all(class_='search_result_row'))
        for row in soup.find_all(class_='search_result_row'):
            appids.append(row['data-ds-appid'])
    with open('Save_Scrap/' +str(pageN*25)+'_'+str(page*25) +'.pickle', 'wb') as handle:
        pickle.dump(appids, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return appids[:n]

#for ipage in range(0,int(80000/25),4):
#    print(ipage)
#    try:
#        get_n_appids(n=100,pageN=ipage)
#    except:
#        print('error ' + str(ipage) )
    

def get_id_pickle(n=100):
    appids = [] 
    for i in range(0,n,100):
        with open( 'Save_Scrap/' +str(i)+'_'+str(i+100) +'.pickle', 'rb') as file:
            appids += pickle.load(file)
    return appids
appids = np.unique(get_id_pickle(n=80000))



#%% Descarga de atributos de appids
def get_data_appid(appid):
    url = 'http://store.steampowered.com/api/appdetails/'
    parameters = {"appids": appid}
    json_req = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0'},params = parameters).json()
    return json_req

#json_req = get_data_appid(appid= appids[0] )

def get_atributes_appids(appids,idname='1'):
    data = {}
    ids_fail = []
    for i in appids:
        try:
            json_atributes = get_data_appid(appid= i )
            data = dict(data, **json_atributes)
        except:
            ids_fail.append(i)
    with open('Save_Scrap/' + idname +'AppDatav2.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(len(ids_fail))
    return data, ids_fail


url = 'https://raw.githubusercontent.com/hectorjimenez12/Mineria_Datos/main/steam.csv'
df = pd.read_csv(url)
app_kaggle = df.appid.values

step=1000
ids_obj = appids
#for i in range(69000,len(ids_obj),step): # 13 min
#    print(i)
#    try:
#        get_atributes_appids(ids_obj[i:(i+step)], idname= str(i) + '_'+str(i+step) )
#    except:
#        print('error ' + str(i) )
   
#data_ids , idsfail  = get_atributes_appids(appids[:20], idname='1')



#%% Cargar dataset de juegos

def get_appdata_pickle(max_id,step=1000):
    appids = {} 
    for i in range(0,max_id,step):
        with open( 'Save_Scrap/'+ str(i)+'_'+str(i+step) +'AppDatav2.pickle', 'rb') as file:
            appids = dict(appids,**pickle.load(file))
    return appids

appdata = get_appdata_pickle(max_id = 71000 ,step=1000)
len(appdata.keys())

#%% DESCARGA DE REVIEWS


def get_reviews(appid, params={'json':1}):
        url = 'https://store.steampowered.com/appreviews/'
        response = requests.get(url=url+appid, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        return response.json()
    
def get_n_reviews(appid, n=100):
    reviews = []
    cursor = '*'
    params = {
            'json' : 1,
            'filter' : 'all',
            'language' : 'english',
            'day_range' : 9223372036854775807,
            'review_type' : 'all',
            'purchase_type' : 'all'
            }
    while n > 0:
        params['cursor'] = cursor.encode()
        params['num_per_page'] = min(100, n)
        n -= 100

        response = get_reviews(appid, params)
        cursor = response['cursor']
        reviews += response['reviews']

        if len(response['reviews']) < 100: break

    return reviews    


#%% Descarga Test

params = {'json':1}
response = get_reviews('10', params)
cursor = response['cursor']
params['cursor'] = cursor.encode()
response_2 = get_reviews('10', params)
print(response)
print(response_2)
response_3 = get_n_reviews('10', n=1000)


