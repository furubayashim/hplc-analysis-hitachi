#!/usr/bin/env python

# script to draw PDA chromatogram & spectrum figure using Hitachi HPLC Chromaster stx/ctx files

import pandas as pd
import numpy as np
import glob
import os
import sys
import matplotlib.pyplot as plt

# change this if using different user/folder
data_dir = "raw/"

# can give sample name file as argv
if len(sys.argv) >1:
    samplenamefile = sys.argv[1]
else:
    samplenamefile = 'sample_info.xlsx'

sample_df = pd.read_excel(samplenamefile)

# load parameter from the xls file
sample_nos = [str(s) for s in sample_df['sample no'].values]
sample_names = sample_df['name'].values
sample_dir = sorted([f+'/' for f in os.listdir(data_dir) if not os.path.isfile(f)])

# Time range (x axis)
start_time = 2
end_time = 18
if 'start time' in sample_df.columns:
    start_time = sample_df['start time'].values[0]
if 'end time' in sample_df.columns:
    end_time = sample_df['end time'].values[0]

# which chart to draw
all_chromato = sample_df['all chromato'].values[0]
each_data = sample_df['each data'].values[0]

# output folder and name
if not os.path.exists('processed'): os.mkdir('processed')
output_name = 'all_chromato'
if 'output name' in sample_df.columns:
    output_name = sample_df['output name'].values[0]

# draw chromato for all samples in one fig ############################
if all_chromato == 'y':
    ctx_files = sorted(glob.glob(data_dir+'*/*.ctx'))
    chromato_dfs = [pd.read_csv(file,skiprows=38,delimiter=';',header=None,names=[sample_names[n],'NaN']).iloc[:,:1] for n,file in enumerate(ctx_files)]
    chromato_df = pd.concat(chromato_dfs,axis=1)
    chromato_df_cut = chromato_df.loc[start_time:end_time]

    fig,axes = plt.subplots(1,2,figsize=[10,8])

    for n,(name,col) in enumerate(chromato_df_cut.iteritems()):
        time = chromato_df_cut.index.values
        abs450 = col.values - 0.1 * n
        axes[0].plot(time,abs450,label=name)
    axes[0].legend()
    axes[0].set_ylabel('Absorbance')
    axes[0].set_xlabel('Time (min)')
    #axes[0].set_ylim([-0.45,0.1])
    axes[0].set_xlim([start_time,end_time])
    axes[0].set_title('Height as it is')

    for n,(name,col) in enumerate(chromato_df_cut.iteritems()):
        abs450 = col.values / np.nanmax(col.values) - 1.1 * n
        time = chromato_df_cut.index.values
        axes[1].plot(time,abs450,label=name)
    axes[1].legend()
    axes[1].set_ylabel('Absorbance (Normalized)')
    axes[1].set_xlabel('Time (min)')
    #axes[1].set_ylim([-0.45,1])
    axes[1].set_xlim([start_time,end_time])
    axes[1].set_title('Height Normalized')

    plt.savefig("processed/{}.pdf".format(output_name),bbox_inches = "tight");

# draw chromato/spec for each sample ############################
if each_data == 'y':
    for sample_no,sample_name,sample_dir in zip(sample_nos,sample_names,sample_dir):
        # load chromato files. Can import several ctx file
        ctx_files = sorted(glob.glob(data_dir+sample_dir+'*.ctx'))
        chromato_dfs = [pd.read_csv(file,skiprows=38,delimiter=';',header=None,names=[os.path.basename(file)[:-4],'NaN']).iloc[:,:1] for file in ctx_files]
        chromato_df = pd.concat(chromato_dfs,axis=1)
        if chromato_df.index.min() < start_time:
            chromato_df_cut = chromato_df.loc[start_time:]
        else:
            chromato_df_cut = chromato_df
        if chromato_df_cut.index.max() > end_time:
            chromato_df_cut = chromato_df_cut.loc[:end_time]

        # load stx files
        stx_files = sorted(glob.glob(data_dir+sample_dir+'*.stx'),key=lambda x: float(os.path.basename(x[:-4])))
        stx_dfs = [pd.read_csv(f,delimiter=';',skiprows=44).iloc[:,:1] for f in stx_files]
        stx_df = pd.concat(stx_dfs,axis=1)
        stx_df_cut = stx_df.loc[250:600]

        # draw figure
        fig = plt.figure(figsize=[6,8])

        for name,col in chromato_df_cut.iteritems():
            time = chromato_df_cut.index.values
            abs450 = col.values
            plt.subplot(3,1,1)
            plt.plot(time,abs450,label=name)
            plt.legend()
            plt.xticks(np.arange(start_time,end_time,1))
            plt.xlabel('Time (min)')
            plt.ylabel('Absorbance')
            ymax = chromato_df.loc[1.5:,'475'].values.max()
            if ymax < 0.01: ymax = chromato_df.loc[:,'475'].values.max()
            plt.ylim([-(ymax*0.05),ymax + ymax*0.05])
            plt.title(sample_no + '-' + sample_name)

        for n,(rt,series) in enumerate(stx_df_cut.iteritems()):
            wavelength = series.index.values
            absorbance = series.values
            plt.subplot(6,3,7+n)
            plt.plot(wavelength,absorbance,label=rt)
            plt.xlim([250,600])
            plt.xticks(np.arange(300,700,100))
            plt.ylim([series.min(),series.max()])
            plt.title(rt[:-2]+' min')

        plt.tight_layout(pad=-0.1);

        plt.savefig('processed/'+sample_no+'-'+sample_name+'.pdf',bbox_inches = "tight");
