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
pd.set_option('display.max_columns', 50)

#https://medium.com/@senchooo/scraping-all-game-in-steam-using-python-e9f0ad206add
#https://andrew-muller.medium.com/scraping-steam-user-reviews-9a43f9e38c92


#%% Web Scraping 
from bs4 import BeautifulSoup

def get_app_id(game_name):
    response = requests.get(url=f'https://store.steampowered.com/search/?term={game_name}&category1=998', headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    app_id = soup.find(class_='search_result_row')['data-ds-appid']
    return app_id

def get_n_appids(n=100):
    appids = []
    url = f'https://store.steampowered.com/search?category1=998&ndl='
    page = 0
    while page*25 < n:
        print(page)
        page += 1
        response = requests.get(url=url+str(page), headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find_all(class_='search_result_row'):
            appids.append(row['data-ds-appid'])
    return appids[:n]

appid_1000 = get_n_appids()


#%% Descarga de detalles de appids

def get_data_appid(appid):
    url = 'http://store.steampowered.com/api/appdetails/'
    parameters = {"appids": appid}
    json_req = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0'},params = parameters).json()
    return json_req

json_req = get_data_appid(appid=10)
r1 = get_data_appid(appid=10)

#for appid in appids:
#    reviews += get_n_reviews(appid, 100)
#df = pd.DataFrame(reviews)[['review', 'voted_up']]
#df




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


