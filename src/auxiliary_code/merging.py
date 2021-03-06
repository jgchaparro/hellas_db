# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

import pandas as pd
import numpy as np
import re
import requests as req
from auxiliary_code.utils import io_excepts
import time

#%%

# =============================================================================
# def merge_census_urban(df, dfu):
#     """Adds terrain information from ELSTAT urban table to
#     the main dataframe based on the full code of the town
#     (NUT1 + NUTS2 + code)."""
#     
#     #Create empty columns to be populated later
#     new_cols = ['astikotita', 'orinotita']
#     for col in new_cols:
#         df[col] = np.nan
#     
#     # Create column `full_koinot_id` with the full code of the 
#     # corresponding koinotita.
#     df['full_koinot_id'] = df['nuts1'].astype(str) + df['nut2'].astype(str) + df['koinot_id'].astype(str)
#     df['full_koinot_id'] = df['full_koinot_id'].apply(lambda x: int(x))
#     
#     # Add information
#     for i in df.index:
#         try:
#             code = df.loc[i, 'full_koinot_id']
#             for col in new_cols:
#                 df.loc[i, col] = dfu.loc[code, col]
#         except:
#             print(f'Invalid code: i = {i}')
# 
#     # Correct datatype
#     df['astikotita'] = df['astikotita'].astype(bool)
# =============================================================================

def merge_census_urban_simple(df, dfu_alt):
    """Adds terrain information from ELSTAT urban table to
    the main dataframe based on prevoiuosly processed information.
    Used as an auxiliary function to bypass problems generated by 
    the merge_census_urban function."""
    
    # Concat two last columns of dfu_alt
    df = pd.concat([df, dfu_alt[['astikotita', 'orinotita']]], axis = 1)
    
    return df
    
    
    



def add_info(res, df, i, cols = None):
    """Adds information to the main census df 
    based on a given index i. By default, 
    adds coordinates and elevation."""
    
    if cols is None:
        search_cols = { # Column in census : column in coord
                        'lat' : 'lat',
                        'long' : 'lon',
                        'h': 'h'
                        }
        
    for cc, coord_c in search_cols.items(): # Census column, coord column
        df.loc[i, cc] = res[coord_c].iloc[0]
        
    
    
    
def merge_census_coord(df, dfc, corr):
    """Adds coordinates from the ELSTAT coordinates document
    to the ELSTAT census table. It uses several support funtions
    as most location names are repeated, so different methods are
    employed to find only one location within different combinations
    of administrative units."""
        
    def filter_town(i):
        
        

        def search_by_nomos_dimenot_name(nomos, dimenot, town):
            """Searches a location based on the location name, 
            the dimotiki enotita and the nomos it belongs.""" 
            
            try:
                in_dimenot = corr[(corr['nomos_kal'] == nomos) & 
                                   (corr['dimenot_kal'] == dimenot)]
                 
                nomarchia_kap = in_dimenot['nomarchia_kap'].unique().tolist()[0]
                dimos_kap = in_dimenot['dimos_kap'].unique().tolist()[0]
             
                # Filter by Kapodistrias nomarchia
                res = dfc[(dfc['nomos']  == nomarchia_kap) &
                           (dfc['dimos'] == dimos_kap) & 
                           (dfc['original_location_name'] == town)]        
            except:
                res = []
            
            return res
        
        
        def search_by_nomos_dimos_town(nomos, dimos, town):
            """Searches a location based on the location name, the dimos and
            the nomos it belongs."""
            
            try:
                in_dimenot = corr[(corr['nomos_kal'] == nomos) & 
                                  (corr['dimos_kal'] == dimos)]
    
                nomarchia_kap = in_dimenot['nomarchia_kap'].unique().tolist()[0]
                dimos_kap = in_dimenot['dimos_kap'].unique().tolist()[0]
            
                # Filter by Kapodistrias dimos and nomarchia
                res = dfc[(dfc['nomos']  == nomarchia_kap) &
                          (dfc['dimos'] == dimos_kap) & 
                          (dfc['original_location_name'] == town)]
            except:
                res = []
                
            return res
        

         
        # `koinot` in KAP corresponds to 'dimenot' in KAL
        def search_by_koinot_name(koinot, town):
            """Searches a location based on the location name and the 
            koinotita it belongs."""
            
            res = dfc[(dfc['original_location_name'] == town) &
                          (dfc['dimenot'] == koinot)]
                
            return res
            
        
        def search_by_nomos_name(nomos, town):
            """Searches a location based on the location name and its nomos."""
            
            in_nomos = corr[corr['nomos_kal'] == nomos]            
            
            try:
                nomarchia_kap = in_nomos['nomarchia_kap'].unique().tolist()[0]
            
                # Filter by name
                res = dfc[(dfc['nomos']  == nomarchia_kap) &
                          (dfc['original_location_name'] == town)]
                
            except:
                res = []
            
            return res
        
        
        # Get basic data
        town = df.loc[i, 'original_location_name']
        koinot = df.loc[i, 'koinot']
        dimenot = df.loc[i, 'dimenot']
        dimos = df.loc[i, 'dimos']
        nomos = df.loc[i, 'nomos']
        print(f'Merging {town} ({nomos})')
        
        # Excute functions
        
        res = search_by_nomos_dimenot_name(nomos, dimenot, town)
        # If there is a unique match
        if len(res) == 1:
            add_info(res, df, i)
            print('Adding unique coincidence')
            
        else:
           res = search_by_nomos_dimos_town(nomos, dimos, town)
           # If there is a unique match
           if len(res) == 1:
               add_info(res, df, i)
               print('Adding unique coincidence')
           else:
               res = search_by_koinot_name(koinot, town)
               if len(res) == 1:
                   add_info(res, df, i)
                   print('Adding unique coincidence')
               else:
                   res = search_by_nomos_name(nomos, town)
                   if len(res) == 1:
                       add_info(res, df, i)
                       print('Adding unique coincidence')
                       
                
    # Initialize
    for i in df.index:
        filter_town(i)            
    
    #list(map(filter_town, df.index))
    
    
#%% Secondary merging functions
    
def merge_agion_oros(df, dfc):
    """Merges locations only for Agion Oros."""
       
    # Extract dataframes
    df_ao_i = df[df['dimos'] == 'ΑΓΙΟ ΟΡΟΣ'].index
    dfc_ao = dfc[dfc['dimos'] == 'ΑΓΙΟΝ ΟΡΟΣ']
    
    # Add irregularities
    irregs = {# Census original_location_name : coord full_name
              'Προβάτα - Μορφονού,η (Ιερά Μονή Μεγίστης Λαύρας)' : 'Προβάτα-Μορφονού,η (Ιερά Μονή Μεγίστης Λαύρας)'}
    
    for i in df_ao_i:
        town = df.loc[i, 'original_location_name']
        desc = df.loc[i, 'location']
        
        res = dfc_ao[dfc_ao['original_location_name'] == town]
        if len(res) == 1:
            add_info(res, df, i)
        elif town in irregs:
            res = dfc_ao[dfc_ao['original_location_name'] == irregs[town]]
        else:
            res = dfc_ao[dfc_ao['location'] == desc]
            if len(res) == 1:
                add_info(res, df, i)
            
            
    
def reverse_merging(df, dfc):
    """Merges based on unused census coordinates"""

    # Copy df
    df2 = df.copy()
    dfc2 = dfc.copy()
    
    # Create lat+long column to compare
    df2['lat+long'] = [(lat, long) for lat, long in zip(df2['lat'], df2['long'])]
    dfc2['lat+long'] = [(lat, long) for lat, long in zip(dfc2['lat'], dfc2['lon'])]
    
    # Get unused lats
    used_lats = df2['lat+long'].tolist()
    dfc2['used'] = [True if r in used_lats else False for r in dfc2['lat+long'].tolist()]
    dfc3 = dfc2[dfc2['used'] == False]
    
    # Filter using the names and codes
    for i in dfc3.index:
        name = dfc3.loc[i, 'location']
        full_name = dfc3.loc[i, 'original_location_name']
        
        res = df[df['location'] == name]
        if len(res) == 1:
            index = res.index[0]
            res_c = dfc2.loc[i].to_frame().T
            add_info(res_c, df, index)
        else:
            res = df[df['original_location_name'] == full_name]
            if len(res) == 1:
                index = res.index[0]
                res_c = dfc2.loc[i].to_frame().T
                add_info(res_c, df, index)
                
def get_unused_lats(df, dfc):
    """Returns a dataframe with unused coordinates"""
    
    df2 = df.copy()
    dfc2 = dfc.copy()
    
    # Create lat+long column to compare
    df2['lat+long'] = [(lat, long) for lat, long in zip(df2['lat'], df2['long'])]
    dfc2['lat+long'] = [(lat, long) for lat, long in zip(dfc2['lat'], dfc2['lon'])]
    
    # Get unused lats
    used_lats = df2['lat+long'].tolist()
    dfc2['used'] = [True if r in used_lats else False for r in dfc2['lat+long'].tolist()]
    dfc3 = dfc2[dfc2['used'] == False]
    return dfc3

def merge_parenthesis(df, dfc, corr):
    """Merges towns with parenthesis and no coords"""
    
    # Create temporary dfs
    df_mod = df.copy()[df['lat'].isnull()]
    dfc_mod = get_unused_lats(df, dfc)
    
    #Modify dfs
    df_mod['original_location_name'] = df_mod['original_location_name'].apply(lambda x: x.split(' (')[0])
    dfc_mod['original_location_name'] = dfc_mod['original_location_name'].apply(lambda x: x.split(' (')[0])

    merge_census_coord(df_mod, dfc_mod, corr)
    
    # Correct column name
    df_mod.rename({'long' : 'lon'}, axis = 1, inplace = True)
    
    for i in df_mod[~df_mod['lat'].isnull()].index:
       res = df_mod.loc[i].to_frame().T
       add_info(res, df, i)

def merge_root_koinot_name(df, dfc):
    
    # Create temporary dfs
    df_mod = df.copy()[df['lat'].isnull()]
    dfc_mod = get_unused_lats(df, dfc)
    
    # Remove accents to avoid divergences
    df_mod['original_location_name'] = df_mod['original_location_name'].apply(remove_accents)
    df_mod['koinot'] = df_mod['koinot'].apply(remove_accents)
    
    
    dfc_mod['original_location_name'] = dfc_mod['original_location_name'].apply(remove_accents)
    dfc_mod['dimenot'] = dfc_mod['dimenot'].apply(remove_accents)
    
    def filter_town(i):
    
        town = df_mod.loc[i, 'original_location_name']
        koinot = df_mod.loc[i, 'koinot']
    
        # `koinot` in KAP corresponds to 'dimenot' in KAL
        def search_by_koinot_name(koinot, town):
            res = dfc_mod[(dfc_mod['original_location_name'] == town) &
                          (dfc_mod['dimenot'].str[:-2] == koinot[:-2])]
            return res
        
        res = search_by_koinot_name(koinot, town)
        if len(res) == 1:
            add_info(res, df, i)
    
    #i = 10232
    #filter_town(i)
    for i in df_mod.index:
       filter_town(i)
     
def merge_simple(df, dfc):
    # Create temporary dfs
    df_mod = df.copy()[df['lat'].isnull()]
    dfc_mod = get_unused_lats(df, dfc)
    
    def filter_town(i):
        town = df_mod.loc[i, 'original_location_name']
        res = dfc_mod[dfc_mod['original_location_name'] == town]
                      
        if len(res) == 1:
            add_info(res, df, i)
    
    list(map(filter_town, df_mod.index))

def remove_accents(string):
    to_replace = {
                'ά' : 'α',
                'έ' : 'ε',
                'ή' : 'η',
                'ί' : 'ι',
                'ύ' : 'υ', 
                'ό' : 'ο',
                'ώ' : 'ω',
                'Ά' : 'Α',
                'Έ' : 'Ε',
                'Ή' : 'Η',
                'Ί' : 'Ι',
                'Ύ' : 'Υ', 
                'Ό' : 'Ο',
                'Ώ' : 'Ω'
        }
    
    for key, value in to_replace.items():
        string = string.replace(key, value)
    
    return string

def merge_dimos_name(df, dfc):
    # Create temporary dfs
    df_mod = df.copy()[df['lat'].isnull()]
    dfc_mod = get_unused_lats(df, dfc)
    
    def filter_town(i):
        town = df_mod.loc[i, 'original_location_name']
        dimos = df_mod.loc[i, 'dimos']
        res = dfc_mod[(dfc_mod['original_location_name'] == town) & (dfc_mod['dimos'] == dimos)]
                      
        if len(res) == 1:
            add_info(res, df, i)
    
    list(map(filter_town, df_mod.index))

def add_manual_locations(df, filepath, index_col = 'index'):
    
    manual_df = pd.read_excel(filepath, index_col = index_col)
    
    for i in manual_df.index:
        df.loc[i, ['lat', 'long', 'h']] = manual_df.loc[i, ['lat', 'long', 'h']]