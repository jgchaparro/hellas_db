# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
import urllib.request
import numpy as np
from os.path import exists 
from functions import unroll_census, dimotiki
from utils import filenames

#%% Obtain census .csv

census_url = 'https://geodata.gov.gr/geoserver/wfs/?service=WFS&version=1.0.0&request=GetFeature&typeName=geodata.gov.gr:f45c73bd-d733-4fe0-871b-49f270c56a75&outputFormat=csv&srsName=epsg:3857'
raw_census_filename = '../data/census_coord.csv'

get_raw = False

# Retrieve census only if it does not exist
if not exists(raw_census_filename) or get_raw:
    urllib.request.urlretrieve(census_url, raw_census_filename)

#%% Read census

dfs = {}
dfs['raw'] = pd.read_csv(raw_census_filename)

#%% Clean df

df = dfs['raw']

# Select necessary columns
sel_cols = ['NAME_OIK', 'NAMEF_OIK', 'lat', 'lon', 'h', 
            'NAME_DIAM', 'NAME_OTA', 'NAME_NOM']
df = df[sel_cols]

# Rename cols
ren_cols = ['name', 'full_name', 'lat', 'lon', 'h', 'dimenot', 'dimos', 'nomos']
df.columns = ren_cols

# Replace 'A

rep_cols = ['name', 'full_name', 'dimenot']
for c in rep_cols:
    df[c] = df[c].str.replace('¶', 'Ά')

#%% Clean columns

df['dimenot'] = df['dimenot'].str.replace('Τ.Δ.', '')
df['dimos'] = df['dimos'].str.replace('ΔΗΜΟΣ ', '')
df['dimos'] = df['dimos'].str.replace('ΚΟΙΝΟΤΗΤΑ ', '')
df['nomos'] = df['nomos'].str.replace('ΝΟΜΟΣ ', '')

#%% Create joining columns

df['nomos-dimos'] = df['nomos'] + '-' + df['dimos']
df['nomos-dimenot'] = df['nomos'] + '-' + df['dimenot']

df['name-nomos-dimos'] = df['full_name'] + '-' + df['nomos'] + '-' + df['dimos']
df['names-nomos-dimenot'] = df['full_name'] + '-' + df['nomos'] + '-' + df['dimenot']

#df['plith-name-nomos'] = df['iure11'] + '-' + df['original_name'] + '-' + df['nomos']

#%% Save csv

df.to_csv(f'../data/{filenames["ELSTAT_coord"]}.csv', index = False)
df.to_excel(f'../data/{filenames["ELSTAT_coord"]}.xlsx')