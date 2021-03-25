#!/usr/bin/env python

# Hitachi HPLC Chromaster
# script to reformat the area table inside "REPRC0001.xls"
# put the exported data (REPRC0001.XLS) into "data" directory
# prepare "peak.xls" where you assign the peak RT and molecule name

import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

area_files = sorted(glob.glob('data/*'))

# carotenoid peak assignment
if os.path.exists('peak.xlsx'):
    peak_file = 'peak.xlsx'
    peak = pd.read_excel(peak_file)
    rt_temp = [[round(x-0.1,1),x,round(x+0.1,1)] for x in peak['RT']]
    rt_range = [n for x in rt_temp for n in x]

def extract_table(file):
    # read excel
    df = pd.read_excel(file,sheet_name='Tables',skiprows=9,skipfooter=5,usecols='B:D',names=['No','RT','Area'])
    samplename = pd.read_excel(file,sheet_name='Manager Report',skiprows=9,usecols='F',header=None).iloc[0,0]

    # clean df
    df['RT'] = round(df['RT'],1)
    df['Sample'] = samplename

    # extract carotenoid peak data
    if os.path.exists('peak.xlsx'):
        condition = df['RT'].isin(rt_range)
        df_ext = df.loc[condition]
    else:
        df_ext = []
    return (df,df_ext)

df_list = []
dfext_list = []

for file in area_files:
    df,df_ext = extract_table(file)
    df_list.append(df)
    dfext_list.append(df_ext)

# output
if not os.path.exists('output'): os.mkdir('output')

pd.concat(df_list).to_excel('output/all_peak.xlsx')
if os.path.exists('peak.xlsx'):
    pd.concat(dfext_list).to_excel('output/carotenoids_peak.xlsx')
