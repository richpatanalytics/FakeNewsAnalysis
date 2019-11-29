# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29, 2019 10:00 AM

@author: Rich Paterson
"""

# Name : assignment6
# Author : Richard Paterson
# Original Date : 11/10/2019
# Overview:
# Process:
## Credits:
#
###########################################################################
#setup environment; ensure working directory has rw permissions
###########################################################################

import pandas as pd #data frame operations
import numpy as np #arrays and math functions

import sys
import warnings
import platform
import os
import datetime
import time 
import re
import string

import matplotlib.pyplot as plt
 

warnings.simplefilter(action='ignore', category=FutureWarning)

#####################################################
# print driver counters etc 
class ShowCtlM:
  def __init__(self, msgLvl, msgCntMain, msgCntSub):
    self.msgLvl = msgLvl
    self.msgCntMain = msgCntMain
    self.msgCntSub = msgCntSub    
  def showDtls(self):
    print("msgLvl is " + str(self.msgLvl))
    print("msgCntMain is " + str(self.msgCntMain))
    print("msgCntSub is " + str(self.msgCntSub))

#####################################################
# sort out all driver parameters
# 1 - Input File Details
# 2 - Separator
# 3 - List of columns
# 4 - describeRawData (0 = no, 1 = yes)
# 5 - saveChart 
# 6 - must Vectorize (0 = no, dont vectorize, 1 = yes, do vectorize)
# 7 - must Model (0 = no dont model, 1 = yes do model)
#####################################################
class Driver:
  def __init__(self, inputFN, inputSep, inputFileEncoding
               , tempFN, tempSep, tempFileEncoding
               , describerawdata, saveChart
               , mustVectorize, mustModel, mustSummarize
               , whichProcess, KPIbars, BNBfolds
               , isRFrqd, isVecWCrqd):
    self.inputFN = inputFN
    self.inputSep = inputSep
    self.inputFileEncoding = inputFileEncoding
    self.tempFN = tempFN
    self.tempSep = tempSep
    self.tempFileEncoding = tempFileEncoding
    self.describerawdata = describerawdata
    self.saveChart = saveChart
    self.mustVectorize = mustVectorize
    self.mustModel = mustModel
    self.mustSummarize = mustSummarize
    self.whichProcess = whichProcess
    self.KPIbars = KPIbars
    self.BNBfolds = BNBfolds
    self.isRFrqd = isRFrqd
    self.isVecWCrqd = isVecWCrqd
  def showDtls(self):
    print("inputFN is " + self.inputFN)
    print("inputSep is " + self.inputSep)
    print("inputFileEncoding is " + self.inputFileEncoding)
    print("tempFN is " + self.tempFN)
    print("tempSep is " + self.tempSep)
    print("tempFileEncoding is " + self.tempFileEncoding)
    print("describerawdata is " + str(self.describerawdata))
    print("saveChart is " + str(self.saveChart))
    print("mustVectorize is " + str(self.mustVectorize))
    print("mustModel is " + str(self.mustModel))
    print("mustSummarize is " + str(self.mustSummarize))
    print("whichProcess is " + self.whichProcess)
    print("KPIbars to show are " + str(self.KPIbars))
    print("BNBfolds to execute are " + str(self.BNBfolds))
    print("Is Modeling using RF rqd " + str(self.isRFrqd))
    print("Is Word Count post VC rqd " + str(self.isVecWCrqd))

def show_run_msg(msgType, mORs, msg, Sctl, fh):
    if mORs == 'main':
        Sctl.msgCntMain+=1
        Sctl.msgCntSub=1
    elif mORs == 'sub':
        Sctl.msgCntSub+=1
    else:
        print("Message number", Sctl.msgCntMain, ":", Sctl.msgCntSub, "==>", "BAD mORs for show_run_msg")
        return(Sctl)
    if (msgType<=Sctl.msgLvl):
        if mORs=='main':
            print("Message number", Sctl.msgCntMain, ":", Sctl.msgCntSub, "==>", msg+"\n")
        if mORs=='sub':
            print("Message number", Sctl.msgCntMain, ":", Sctl.msgCntSub, "==>", msg+"\n")
        fh.write("Message number"+str(Sctl.msgCntMain)+":"+str(Sctl.msgCntSub)+"==>"+msg+"\n")
    return(Sctl)

def show_run_data(msgType, structData, actData, Sctl, fh):
    # Code for printing to a file 
    sample = open('_tmpfile_.txt', 'w') 
    print(actData, file = sample) 
    sample.close() 
    if (msgType<=Sctl.msgLvl):
        with open ("_tmpfile_.txt", "r") as rawin:
            for data in rawin.readlines():
                fh.write('\t'+data)
    return(Sctl)
    
def firstXinList(TheList, HowMany):
    SelList=[]
    for x in TheList:
        OneString = x[:HowMany]

        SelList.append(OneString)
    return(SelList)

def WCChart (wc_lbl, wc_ttl, wc_vec, wc_cvm, wc_iter, wc_fn, DRV, Sctl, msgfh_):
    ####################
    ## W O R D C L O U D
    ####################
    Sctl=show_run_msg (3, 'sub', 'Generate wordcloud', Sctl, msgfh_)
    sum_words = wc_vec.sum(axis=0)
    #print('sum', sum_words)
    words_freq = [(word, sum_words[0, idx]) for word, idx in wc_cvm.vocabulary_.items()]
    #print(words_freq)
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    #print(words_freq[:40])
    filter_words = (dict([(m, n) for m, n in words_freq if n > 5]))# if len(m) > 3]))
    #print(len(filter_words))
    wcloud = WordCloud().generate_from_frequencies(filter_words)
    #print(len(wcloud))
    plt.figure()
    fig, ax = plt.subplots(figsize=(11, 7))
    plt.imshow(wcloud, interpolation="bilinear")
    plt.axis("off")
    if DRV.saveChart==1:
        plt.savefig(wc_fn+"_wcl_"+wc_lbl+"_"+str(wc_iter)+".pdf")
    plt.show()
    return(Sctl)

###############################################################
# Chart showing accuracy prediction for Lie detection
# lwc_wl = whichLabel
# lwc_ttl = main part of title
# lwc_abb = abbreviated title
# x = x values
# y = y values
# lwc_iter = iteration number
# lwc_fn = start of filename
# DRV, Sctl, msgfh_ = standard control parameters
#
def ListedWordsChart(lwc_wl, lwc_ttl, lwc_abb, x, y, lwc_iter, lwc_fn, DRV, Sctl, msgfh_):
    chartTitle = lwc_ttl+" for label =>"+lwc_wl+"<= iteration no. "+str(lwc_iter)
    Sctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", Sctl, msgfh_)
    #accu=list((round((y),6)).astype('str'))
    #print(accu)
    from matplotlib.cm import inferno, viridis
    nbcurves=len(y) # either 20 or less than
    colors = viridis(np.linspace(0, 1, nbcurves))
    fig, ax = plt.subplots(figsize=(11, 7))
    #plt.ylim((0,.8))
    bars = plt.bar(x, height=y, width=.8, color=colors)
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in x]
    xlabs=[i for i in x]
    plt.ylabel('Rank')
    plt.xlabel('Words')
    plt.title(chartTitle)
    plt.xticks(xlocs, xlabs)
    ax.set_xticklabels(xlabs, rotation = 90)
    which=0
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x()+.4, yval + -.2, y[which], ha='center', color='#FFFFFF', size=8, rotation=90)
        which+=1
    if DRV.saveChart==1:
        plt.savefig(lwc_fn+"_lwc_"+lwc_wl+lwc_abb+"_"+str(lwc_iter)+".pdf")
    plt.show()
    return(Sctl)

def exitgracefully(Sctl, msgfh_):
    Sctl=show_run_msg (3, 'main', time.strftime('%c'), Sctl, msgfh_)
    Sctl=show_run_msg (3, 'main', 'exit gracefully', Sctl, msgfh_)
    msgfh_.close()
    sys.exit(1)

def describeData(dd_setname, dd_data, Sctl, msgfh_):
    Sctl=show_run_msg (3, 'main', 5*("Input set is >="+dd_setname+'  '), Sctl, msgfh_)
    Sctl=show_run_msg (3, 'sub', "Describe RAW data (long)", Sctl, msgfh_)
    Sctl=show_run_msg (3, 'sub' , "========================", Sctl, msgfh_)
    Sctl=show_run_msg (3, 'sub', "Describe shape", Sctl, msgfh_)
    Sctl=show_run_data (3, 'xxx' , (dd_data.shape, 'cols', dd_data.shape[1], 'rows', dd_data.shape[0]), Sctl, msgfh_)
    Sctl=show_run_msg (3, 'sub', "Describe count of null", Sctl, msgfh_)
    Sctl=show_run_data (3, 'xxx' , dd_data.isnull().sum(), Sctl, msgfh_)
    Sctl=show_run_msg (3, 'sub', "Describe dtypes", Sctl, msgfh_)
    Sctl=show_run_data (3, 'xxx' , dd_data.dtypes, Sctl, msgfh_)
    Sctl=show_run_msg (3, 'sub', "Show 1st 5 lines (aka head)", Sctl, msgfh_)
    Sctl=show_run_data (3, 'xxx' , pd.DataFrame.head(dd_data), Sctl, msgfh_)
    Sctl=show_run_msg (3, 'sub', "Show describe", Sctl, msgfh_)
    Sctl=show_run_data (3, 'xxx' , dd_data.describe(), Sctl, msgfh_)
    return (Sctl)

def summaryChart(dataSelector, whichModel, chartTitle, inDF, saveFileName, inDRV, inSctl, inmsgfh_):
    #
    inSctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", inSctl, inmsgfh_)
    ChartDF=inDF[inDF.whichLabel==dataSelector]
    ChartDF=ChartDF.reset_index(drop=True)
    if whichModel=='Overall':
        ChartDF['Accuracy']=ChartDF.AccuracyLinearSVC
        ChartDF['model']='lSVC'
        ChartDF['duration']=''
        ChartDF['conv']=''        
        for i in range(len(ChartDF)):
            cla_strt=datetime.datetime.strptime(str(KPIDF.linearSVCTrainStart[i]), "%Y%m%d%H%M%S")
            cla_end=datetime.datetime.strptime(str(KPIDF.linearSVCTestEnd[i]), "%Y%m%d%H%M%S")
            ChartDF.loc[i, 'duration']=cla_end-cla_strt
            ChartDF.loc[i, 'conv']=KPIDF.VlSVCconverge[i]
            if ChartDF.loc[i]['AccuracyMultiNB'] > ChartDF.loc[i]['Accuracy']:
                ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracyMultiNB']
                ChartDF.loc[i, 'model']="MNB"
                cla_strt=datetime.datetime.strptime(str(KPIDF.MNBStart[i]), "%Y%m%d%H%M%S")
                cla_end=datetime.datetime.strptime(str(KPIDF.MNBEnd[i]), "%Y%m%d%H%M%S")
                ChartDF.loc[i, 'duration']=cla_end-cla_strt
                ChartDF.loc[i, 'conv']=''
            if ChartDF.loc[i]['AccuracyRF'] > ChartDF.loc[i]['Accuracy']:
                ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracyRF']
                ChartDF.loc[i, 'model']="RF"
                cla_strt=datetime.datetime.strptime(str(KPIDF.RFStart[i]), "%Y%m%d%H%M%S")
                cla_end=datetime.datetime.strptime(str(KPIDF.RFEnd[i]), "%Y%m%d%H%M%S")
                ChartDF.loc[i, 'duration']=cla_end-cla_strt
                ChartDF.loc[i, 'conv']=''
        #    if ChartDF.loc[i]['AccuracySVM'] > ChartDF.loc[i]['Accuracy']:
        #        ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracySVM']
        #        ChartDF.loc[i, 'model']="SVM"
        #    if ChartDF.loc[i]['AccuracyMNBnnK'] > ChartDF.loc[i]['Accuracy']:
        #        ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracyMNBnnK']
        #        ChartDF.loc[i, 'model']="nnK"
    elif whichModel=='SVC':
        ChartDF['Accuracy']=ChartDF.AccuracyLinearSVC
        ChartDF['model']='lSVC'
        ChartDF['duration']=''
        ChartDF['conv']=''
        for i in range(len(ChartDF)):
            cla_strt=datetime.datetime.strptime(str(KPIDF.linearSVCTrainStart[i]), "%Y%m%d%H%M%S")
            cla_end=datetime.datetime.strptime(str(KPIDF.linearSVCTestEnd[i]), "%Y%m%d%H%M%S")
            ChartDF.loc[i, 'duration']=cla_end-cla_strt
            ChartDF.loc[i, 'conv']=KPIDF.VlSVCconverge[i]
    elif whichModel=='MNB':
        ChartDF['Accuracy']=ChartDF.AccuracyMultiNB
        ChartDF['model']='MNB'
        ChartDF['duration']=''
        ChartDF['conv']=''
        for i in range(len(ChartDF)):
            cla_strt=datetime.datetime.strptime(str(KPIDF.MNBStart[i]), "%Y%m%d%H%M%S")
            cla_end=datetime.datetime.strptime(str(KPIDF.MNBEnd[i]), "%Y%m%d%H%M%S")
            ChartDF.loc[i, 'duration']=cla_end-cla_strt
            
    if len(ChartDF)>inDRV.KPIbars:
        ChartDF=ChartDF.sort_values(by=["Accuracy"],ascending=False)
        ChartDF=ChartDF.head(inDRV.KPIbars)
        ChartDF=ChartDF.sort_values(by=["KPIcounter"],ascending=True)
    
    x=(list(range(len(ChartDF))))
    ydf=pd.DataFrame(ChartDF.Accuracy)
    ydf.columns=['Accuracy']
    ydf['model']=ChartDF.model
    ChartDF=ChartDF.reset_index(drop=True)
    ydf=ydf.reset_index(drop=True)
    y=(ydf.Accuracy*100)
    accu=(round((y),3)).astype('str')+'%'
    from matplotlib.cm import inferno, viridis
    nbcurves=len(ChartDF)
    colors = viridis(np.linspace(0, 1, nbcurves))
    fig, ax = plt.subplots(figsize=(11, 7))
    plt.ylim((30,70)) # plt.ylim((0,100))
    bars = plt.bar(x, height=y, width=.8, color=colors)

    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in x]
#    xlabs=[i for i in x]
    xlabs=ChartDF.KPIcounter
    plt.ylabel('Accuracy %')
    plt.xlabel('Iteration Number')
    plt.title(chartTitle)
    plt.xticks(xlocs, xlabs)
    which=0
    for bar in bars:
        rule1ix = inDF.Vrulename[which].find("_")
        rule1 = inDF.Vrulename[which][0:rule1ix]
        rule2ix = inDF.Vrulename[which].find("_", rule1ix+1)
        rule2 = inDF.Vrulename[which][rule1ix+1:rule2ix]
        yval = bar.get_height()
        plt.text(bar.get_x()+.4, yval + -2, accu[which], ha='center', color='#FFFFFF', size=11)
        plt.text(bar.get_x()+.4, yval + -5, 'rule\n'+str(rule1), ha='center', color='#FFFFFF', size=10)
        plt.text(bar.get_x()+.4, yval + -6.2, ''+str(rule2), ha='center', color='#FFFFFF', size=10)
        plt.text(bar.get_x()+.4, yval + -9, '#model\n'+ydf.model[which], ha='center', color='#FFFFFF', size=10)
        plt.text(bar.get_x()+.4, yval + -12, 'duration\n'+str(ChartDF.duration[which]), ha='center', color='#FFFFFF', size=10)
        plt.text(bar.get_x()+.4, yval + -15, 'min df\n'+str(ChartDF.Vmin_df_sel[which]), ha='center', color='#FFFFFF', size=10)
        plt.text(bar.get_x()+.4, yval + -18, 'max df\n'+str(ChartDF.Vmax_df_sel[which]), ha='center', color='#FFFFFF', size=10)
        plt.text(bar.get_x()+.4, yval + -21, 'features\n'+str(inDF.NoFeatures[which]), ha='center', color='#FFFFFF', size=10)
        if not ChartDF.conv[which]=='':
            plt.text(bar.get_x()+.4, yval + -24, 'converge\n'+str(ChartDF.conv[which]), ha='center', color='#FFFFFF', size=10)
        which+=1
    if DRV.saveChart==1:
        plt.savefig(saveFileName+"_accTOPNbar_"+dataSelector+"_"+whichModel+".pdf")
    plt.show()
    return inSctl

def summaryChartLineAccuracy(dataSelector, chartTitle, inDF, saveFileName, inDRV, inSctl, inmsgfh_):
    #
    inSctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", inSctl, inmsgfh_)
    ChartDF=inDF[inDF.whichLabel==dataSelector]
    ChartDF=ChartDF.reset_index(drop=True)
    ChartDF['Accuracy']=ChartDF.AccuracyLinearSVC
    ChartDF['model']='lSVC'
    ChartDF['duration']=''
    ChartDF['conv']=''
    
    for i in range(len(ChartDF)):
        cla_strt=datetime.datetime.strptime(str(KPIDF.linearSVCTrainStart[i]), "%Y%m%d%H%M%S")
        cla_end=datetime.datetime.strptime(str(KPIDF.linearSVCTestEnd[i]), "%Y%m%d%H%M%S")
        ChartDF.loc[i, 'duration']=cla_end-cla_strt
        ChartDF.loc[i, 'conv']=KPIDF.VlSVCconverge[i]
        if ChartDF.loc[i]['AccuracyMultiNB'] > ChartDF.loc[i]['Accuracy']:
            ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracyMultiNB']
            ChartDF.loc[i, 'model']="MNB"
            cla_strt=datetime.datetime.strptime(str(KPIDF.MNBStart[i]), "%Y%m%d%H%M%S")
            cla_end=datetime.datetime.strptime(str(KPIDF.MNBEnd[i]), "%Y%m%d%H%M%S")
            ChartDF.loc[i, 'duration']=cla_end-cla_strt
        if ChartDF.loc[i]['AccuracyRF'] > ChartDF.loc[i]['Accuracy']:
            ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracyRF']
            ChartDF.loc[i, 'model']="RF"
            cla_strt=datetime.datetime.strptime(str(KPIDF.RFStart[i]), "%Y%m%d%H%M%S")
            cla_end=datetime.datetime.strptime(str(KPIDF.RFEnd[i]), "%Y%m%d%H%M%S")
            ChartDF.loc[i, 'duration']=cla_end-cla_strt
    #    if ChartDF.loc[i]['AccuracySVM'] > ChartDF.loc[i]['Accuracy']:
    #        ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracySVM']
    #        ChartDF.loc[i, 'model']="SVM"
    #    if ChartDF.loc[i]['AccuracyMNBnnK'] > ChartDF.loc[i]['Accuracy']:
    #        ChartDF.loc[i,'Accuracy']=ChartDF.loc[i]['AccuracyMNBnnK']
    #        ChartDF.loc[i, 'model']="nnK"
            
    #ChartDF=ChartDF.sort_values(by=["Accuracy"],ascending=False)

    x=ChartDF.KPIcounter
    y=(ChartDF.Accuracy*100)
    from matplotlib.cm import inferno, viridis
    nbcurves=1
    colors = viridis(np.linspace(0, 1, nbcurves))
    fig, ax = plt.subplots(figsize=(11, 7))
    plt.ylim((50,70)) # plt.ylim((0,100))
    #plt.plot(x, ChartDF.Accuracy*100)
    plt.plot(x, ChartDF.AccuracyLinearSVC*100, label='lSVC')
    plt.plot(x, ChartDF.AccuracyMultiNB*100, label='MNB')
    plt.plot(x, ChartDF.AccuracyRF*100, label='RF')
#    plt.plot(x, ChartDF.AccuracySVM*100, label='SVM')
#    plt.plot(x, ChartDF.AccuracyMNBnnK*100, label='MNBnnK')
    plt.legend(loc='upper right')
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in x]
    xlabs=ChartDF.KPIcounter
    plt.ylabel('Accuracy %')
    plt.xlabel('Iteration Number')
    plt.title(chartTitle)
    plt.xticks(xlocs, xlabs)
    if DRV.saveChart==1:
        plt.savefig(saveFileName+"_accMODELline_"+dataSelector+".pdf")
    plt.show()
    return inSctl

def summaryChartLineBest(dataSelector, chartTitle, inDF, saveFileName, inDRV, inSctl, inmsgfh_):
    #
    inSctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", inSctl, inmsgfh_)
    ChartDF=pd.DataFrame()
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==2)].iter
    ChartDF['iter']=sclb
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==2)].numll
    ChartDF['numll']=sclb    
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==2)].valll
    ChartDF['2']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==4)].valll
    ChartDF['4']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==6)].valll
    ChartDF['6']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==8)].valll
    ChartDF['8']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==10)].valll
    ChartDF['10']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==15)].valll
    ChartDF['15']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==20)].valll
    ChartDF['20']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==30)].valll
    ChartDF['30']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==40)].valll
    ChartDF['40']=list(sclb)
    sclb=inDF[(inDF.dataset==dataSelector)&(inDF.numtopics==50)].valll
    ChartDF['50']=list(sclb)
    
    print(inDF.dataset)
    
    ydf=pd.DataFrame()
    ydf['2']=ChartDF['2']
    ydf['4']=ChartDF['4']
    ydf['6']=ChartDF['6']
    ydf['8']=ChartDF['8']
    ydf['10']=ChartDF['10']
    ydf['15']=ChartDF['15']
    ydf['20']=ChartDF['20']
    ydf['30']=ChartDF['30']
    ydf['40']=ChartDF['40']
    ydf['50']=ChartDF['50']
#    ydf['AccuracyCombined']=list(ChartDF[ChartDF.whichLabel=='combined'].Accuracy)    
    #ChartDF=ChartDF.sort_values(by=["Accuracy"],ascending=False)
    print (len(ydf))
    x=(list(range(len(ydf))))
    #y=(ydf.AccuracySentiment*100)
    from matplotlib.cm import inferno, viridis
    nbcurves=1
    colors = viridis(np.linspace(0, 1, nbcurves))
    fig, ax = plt.subplots(figsize=(11, 7))
    #plt.ylim((-7, -12)) # plt.ylim((0,100))
    #plt.plot(x, ChartDF.Accuracy*100)
#    plt.plot(x, ydf.AccuracyLie*100, label='Lie')
    plt.plot(x, ydf['2'], label='2')
    plt.plot(x, ydf['4'], label='4')
    plt.plot(x, ydf['6'], label='6')
    plt.plot(x, ydf['8'], label='8')
    plt.plot(x, ydf['10'], label='10')
    plt.plot(x, ydf['15'], label='15')
    plt.plot(x, ydf['20'], label='20')
    plt.plot(x, ydf['30'], label='30')    #    plt.plot(x, ydf.AccuracyCombined*100, label='Combined')
    plt.plot(x, ydf['40'], label='40')    #    plt.plot(x, ydf.AccuracyCombined*100, label='Combined')
    plt.plot(x, ydf['50'], label='50')    #    plt.plot(x, ydf.AccuracyCombined*100, label='Combined')
    plt.legend(loc='upper right')
    xlocs, xlabs = plt.xticks()
    xlocs=[i for i in x]
    xlabs=ChartDF.numll
    plt.ylabel('ll/token val')
    plt.xlabel('Report Every n (x15)')
    plt.title(chartTitle)
    plt.xticks(xlocs, xlabs)
    if DRV.saveChart==1:
        plt.savefig(saveFileName+"_accBESTline_"+dataSelector+".pdf")
    plt.show()
    return inSctl

###########################################################################
#-- M A I N   S T A R T --
###########################################################################

# THIS IS THE END OF ALL EXECUTION ############################################

wdir="C:/Users/Richpat/Documents/@syracuse coursework/@IST 736 Text Mining/@finalproject/"
print("Current Working Directory (before) " , os.getcwd())
os.chdir(wdir)
print("Current Working Directory (after)" , os.getcwd())
print('Python is ' + platform.python_version())
#pd.show_versions(as_json=True) # True to shorten output

stdt=time.strftime('%Y%m%d%H%M%S') # was %c
programName=sys.argv[0]
programName=programName[0:programName.find(".")]
logFileNamestrt=programName+"_"+stdt
logFileName=logFileNamestrt+".log"
FNbFileName="FNb_log_20191129_141306.txt"
tmpFileName="FNc_tmp_"+stdt+".txt"
KPIfilename=logFileNamestrt+"_KPI.csv"
KPIcounter=1

msgfh_ = open(logFileName,"w+") 

Sctl=ShowCtlM(3, 0, 0)
Sctl=show_run_msg (3, 'main', time.strftime('%c'), Sctl, msgfh_)
Sctl=show_run_msg (3, 'main', 'Startup parameter settings', Sctl, msgfh_)
Sctl=show_run_data (3, 'xxx' , (Sctl.showDtls()), Sctl, msgfh_)

DRVin = 1
if (DRVin == 1):
    DRV=Driver( FNbFileName, "\t", "utf-8"
               , tmpFileName, ",", "utf-8"
               , 1, 1, 1, 1, 1 
               , 'T+T', 10, 12, 1, 1)
                #show raw, save Chart, vectorize, model, summarize, 
                #whichprocess, KPIbars, BNB folds, is RF rqd, is post Vec wordcount+sum rqd (slow)
    Sctl=show_run_data (3, 'xxx' , (DRV.showDtls()), Sctl, msgfh_)

# Transform run output

###########################################################################
#create temporary pipe-delimited file - S T A R T   S T A R T
###########################################################################
 
Sctl=show_run_msg (3, 'main', 'Create temporary pipe-delimited from input file', Sctl, msgfh_)

Sctl=show_run_msg (3, 'main', "Parsing MALLET logfile =>"+DRV.inputFN+"<=", Sctl, msgfh_)

rawout = open(DRV.tempFN,"w+")
newline=('rowlabel' 
        + DRV.tempSep + "iter"
        + DRV.tempSep +  "date"
        + DRV.tempSep +  "time"
        + DRV.tempSep +  "type"
        + DRV.tempSep +  "dataset"
        + DRV.tempSep +  "numtopics"
        + DRV.tempSep +  "numiterations"
        + DRV.tempSep +  "max"
        + DRV.tempSep +  "total"
        + DRV.tempSep +  "numll"
        + DRV.tempSep +  "valll"
        + '\n')
rawout.write(newline)

withPipe=[]
cntIter=0
cntNumRecs=0
with open (DRV.inputFN, "r") as rawin:
    for data in rawin.readlines():
        cntIter+=1
        lowerdata=data.lower().strip()
        splitdata=lowerdata.split()
        if len(lowerdata) == 0 :
            z="no data"
        else:
            if len(splitdata) == 0:
                print ("no split", lowerdata)
            else:
#                print ("yes split", lowerdata)
                if splitdata[0]=='iter':
#                    print (lowerdata)
                    zziter=splitdata[1] #iteration number
                    zztype=splitdata[2] #import or train
                    zzdate=splitdata[4]
                    zztime=splitdata[5]
                    zzdataset=splitdata[9]
                    zzdataset=zzdataset.replace("\\","")
                    print ('zzdataset', zzdataset)
                    if zzdataset.find("liar_data_files") > 0:
                        zzdataset = "all"                        
                    elif zzdataset.find("TRUE") > 0:
                        zzdataset = "fd"                        
                    elif zzdataset.find("-m-r") > 0:
                        zzdataset = "mr"                        
                    elif zzdataset.find("-m-d") > 0:
                        zzdataset = "md"                        
                    elif zzdataset=="110":
                        zzdataset = "all"
                    elif zzdataset=="110f":
                        zzdataset = "f"
                    elif zzdataset=="110m":
                        zzdataset = "m"
                    elif zzdataset=="110d":
                        zzdataset = "d"
                    elif zzdataset=="110r":
                        zzdataset = "r"
                    zznumtopics=splitdata[11]
                    zznumiterations=splitdata[13]
                    zzmax='0'
                    zztotal='0'
                    #max tokens: 284433
                    #total tokens: 7591216
                if len(splitdata)==3 and splitdata[0]=='max' and splitdata[1] == 'tokens:':
                    zzmax=splitdata[2]
                if len(splitdata)==3 and splitdata[0]=='total' and splitdata[1] == 'tokens:':
                    zztotal=splitdata[2]
                if len(splitdata)==3 and splitdata[1]=='ll/token:':
                    zznumll=splitdata[0].replace(">", "").replace("<", "")
                    zzvalll=splitdata[2]
                    newline=('mallett-lltoken' 
                            + DRV.tempSep + zziter
                            + DRV.tempSep +  zzdate
                            + DRV.tempSep +  zztime
                            + DRV.tempSep +  zztype
                            + DRV.tempSep +  zzdataset
                            + DRV.tempSep +  zznumtopics
                            + DRV.tempSep +  zznumiterations
                            + DRV.tempSep +  zzmax
                            + DRV.tempSep +  zztotal
                            + DRV.tempSep +  zznumll
                            + DRV.tempSep +  zzvalll
                            + '\n')
                    print (newline)
                    rawout.write(newline)
                    cntNumRecs+=1
rawin.close()
rawout.close()


Sctl=show_run_msg (3, 'sub', "No records on MALLET logfile =>"+str(cntIter)+"<=", Sctl, msgfh_)

Sctl=show_run_msg (3, 'sub', "From MALLET logfile, created =>"+str(cntNumRecs)+"<= ll/token records for further analysis", Sctl, msgfh_)

###########################################################################
#create temporary pipe-delimited file - E N D   E N D   E N D
###########################################################################


OurInputDFraw = pd.read_csv(DRV.tempFN, sep=DRV.tempSep, encoding = DRV.tempFileEncoding)

if (DRV.describerawdata==1):
    Sctl=describeData ("lltoken",  OurInputDFraw, Sctl, msgfh_)

Sctl=summaryChartLineBest('liar_data_files'
                 , 'll/token value for ALL datasets per NumTopics\n (100 Training Iterations, Report ll/token Every 10)'
                 , OurInputDFraw
                 , logFileNamestrt
                 , DRV
                 , Sctl
                 , msgfh_)

#exitgracefully(Sctl, msgfh_)

##############################
## 
##############################
keysFN = "FNb_mallet_1_ALL_50_keys.txt"
keysSep="\t"
keysFileEncoding="utf-8"
Sctl=show_run_msg (3, 'main', "Load Mallet key file data from =>"+keysFN+"<=", Sctl, msgfh_)

OurKeysDFraw = pd.read_csv(keysFN, sep=keysSep, encoding = keysFileEncoding, header=None)

if (DRV.describerawdata==1):
    Sctl=describeData ("keys",  OurKeysDFraw, Sctl, msgfh_)

print (len(OurKeysDFraw))
colnames=['ID', 'num', 'keys']  
#'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'k8', 'k9', 'k10', 
# 'k11', 'k12', 'k13', 'k14', 'k15', 'k16', 'k17', 'k18', 'k19', 'k20']
OurKeysDFraw.columns=colnames
print(OurKeysDFraw.head())

topicsFN = "FNb_mallet_1_ALL_50_topics.txt"
topicsSep="\t"
topicsFileEncoding="utf-8"
Sctl=show_run_msg (3, 'main', "Load Mallet topics file data from =>"+topicsFN+"<=", Sctl, msgfh_)

OurTopicsDFraw = pd.read_csv(topicsFN, sep=topicsSep, encoding = topicsFileEncoding, header=None)

if (DRV.describerawdata==1):
    Sctl=describeData ("topics",  OurTopicsDFraw, Sctl, msgfh_)

print (len(OurTopicsDFraw))
colnames=['ID', 'FN', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10' 
          , 't11', 't12', 't13', 't14', 't15', 't16', 't17', 't18', 't19', 't20'
          , 't21', 't22', 't23', 't24', 't25', 't26', 't27', 't28', 't29', 't30'
          , 't31', 't32', 't33', 't34', 't35', 't36', 't37', 't38', 't39', 't40'
          , 't41', 't42', 't43', 't44', 't45', 't46', 't47', 't48', 't49', 't50']
OurTopicsDFraw.columns=colnames
print(OurTopicsDFraw.head())

Sctl=show_run_msg (3, 'sub', "Flatten Mallet topics file", Sctl, msgfh_)
#which columns has the max topic with max likelihood
isFlattenOurTopicsRqd=1
if isFlattenOurTopicsRqd==1:
    OurTopicsDFplus=OurTopicsDFraw
    OurTopicsDFplus['maxval']=OurTopicsDFraw.t1
    OurTopicsDFplus['whichCol']='t1'
    for i in range(len(OurTopicsDFplus)):
        for j in range(len(colnames)):
            if j>1:
                if OurTopicsDFplus.loc[i][j] > OurTopicsDFplus.loc[i,'maxval']:
                    OurTopicsDFplus.loc[i,'maxval']=OurTopicsDFplus.loc[i][j]
                    OurTopicsDFplus.loc[i, 'whichCol']=colnames[j]
        if 0==(i%1000):
            Sctl=show_run_msg (3, 'sub', ('iteration ==>'+str(i)+'<== of ==>'+str(len(OurTopicsDFplus))+"<=="), Sctl, msgfh_)

    topicsFLAT = "FNc_mallet_1_ALL_50_topics_flat.txt"
    OurTopicsDFplus.to_csv(topicsFLAT, sep=",", index=False)

#exitgracefully(Sctl, msgfh_)

################################################################################

#useWhat="Files"
createCorpus="Files"
#createCorpus=""
labelsAre=['Veracity']
textName='Phrase'
perfKPI=[]  #empty list
topicsFLAT = "FNc_mallet_1_ALL_50_topics_flat.txt"
OurTopicsDFplus=pd.read_csv(topicsFLAT, sep=",", index_col=False)
 

#maxdf, mindf, stopwords, ngramlength, lowercase, analyzer, tokenpattern
zztp=u'(?ui)\\b\\w*[a-z]+\\w*\\b'
zztp1='[^\d\W]+' #match any non-digit and (non-non-word) i.e. a word character.
# rulename, vectorizer type,
iterDict=[]
iterDict.append(['unigram_count_1', 'CountVectorizer'
                 , .4, 8,  'english', 1, False, 'word', zztp, 4000
                 , 5])

Sctl=show_run_msg (3, 'main', "Iterate thru this parameter set", Sctl, msgfh_)
Sctl=show_run_data (3, 'xxx' , iterDict, Sctl, msgfh_)

if DRV.mustVectorize==0 and DRV.mustModel==0:
    Sctl=show_run_msg (3, 'main', 'Skipping Vectorizing and Modeling', Sctl, msgfh_)
elif DRV.mustVectorize==0 and DRV.mustModel==1:
    Sctl=show_run_msg (3, 'main', 'PARAMETER ERROR: Vectorizing required for Modeling', Sctl, msgfh_)
elif DRV.mustVectorize==1 or DRV.mustModel==1:
    for whichLabel in labelsAre:
        Sctl=show_run_msg (3, 'main', "Processing label ==>"+whichLabel+"<==", Sctl, msgfh_)
        if createCorpus=="":
            Sctl=show_run_msg (3, 'main', "Skipping creating underlying data files", Sctl, msgfh_)
        elif createCorpus=="Files":
            Sctl=show_run_msg (3, 'main', "Creating underlying data files", Sctl, msgfh_)
            cnt=0
            ListOfCompleteFilePaths=[]
            ListOfLabels=[]
            start_path = './liar_data_files'
            for path,dirs,files in os.walk(start_path):
                for filename in files:
                    wfn=os.path.join(path,filename)
                    if wfn.find("barely-true") > 0:
                        wlabel = "bt"                        
                    elif wfn.find("half-true") > 0:
                        wlabel = "ht"                        
                    elif wfn.find("mostly-true") > 0:
                        wlabel = "mt"                        
                    elif wfn.find("pants-fire") > 0:
                        wlabel = "pf"
                    elif wfn.find("FALSE") > 0:
                        wlabel = "fls"
                    elif wfn.find("TRUE") > 0:
                        wlabel = "tr"
                    else:
                        wlabel = "zz"
                    ListOfCompleteFilePaths.append(wfn)
                    ListOfLabels.append(wlabel)
                    cnt=cnt+1
            print (len(ListOfCompleteFilePaths))
            print (len(ListOfLabels))
    
            Sctl=show_run_msg (3, 'sub', "Made a list containing all underlying data files =>"+str(len(ListOfCompleteFilePaths)), Sctl, msgfh_)
            Sctl=show_run_msg (3, 'sub', "first 20 file paths are ...", Sctl, msgfh_)
            Sctl=show_run_data (3, 'xxx' , ListOfCompleteFilePaths[:20], Sctl, msgfh_)
            Sctl=show_run_msg (3, 'sub', "first 20 labels are ...", Sctl, msgfh_)
            Sctl=show_run_data (3, 'xxx' , ListOfLabels[:20], Sctl, msgfh_)
            ##################################################################
            ### VALIDATION   VALIDATION   VALIDATION   VALIDATION
            ### make sure that len og filenames is the same length
            ### as the lengh ot file topics in the raw topics set
            ### this might be different because the rules to load
            ### these are coded manually!!! so they might have got out of step
            ##################################################################
            if len(ListOfCompleteFilePaths)!=len(OurTopicsDFraw):
                            Sctl=show_run_msg (3, 'main', "ERROR: MISMATCH IN RULES FOR LOADING DATASETS", Sctl, msgfh_)
                            1/0 #fore exit
            chkIsValid=0
            for i in range(len(ListOfCompleteFilePaths)):
                chkLCFP=ListOfCompleteFilePaths[i].rsplit('\\', 1)[-1]
                chkTOPIC=OurTopicsDFraw.iloc[i]['FN'].rsplit('/', 1)[-1]
                if (chkLCFP==chkTOPIC):
                    chkIsValid=chkIsValid+1
                #print(chkIsValid, chkLCFP, chkTOPIC)
            if (chkIsValid==0 | chkIsValid!=len(OurTopicsDFraw)):
                            Sctl=show_run_msg (3, 'main', "ERROR: MISMATCH IN FILENAME VS TOPICS FILE ORDER", Sctl, msgfh_)
                            1/0 #fore exit
            ### this is why we do the above - to add label to the MALLET topic list
            OurTopicsDFplus['label']=ListOfLabels
            #################################################
            ## print chart showing distribution across labels
            #################################################
            distFN=logFileNamestrt+"_dist_"+whichLabel+".pdf"
            miwsBars=30
            import collections
            #print(ListOfLabels)
            counter=collections.Counter(ListOfLabels)
#            counter=sorted(counter.items())
            #print(ListOfLabels)
            y=counter.values()
            x=counter.keys()
            if len(y) > miwsBars:
                y=y.head(miwsBars)
                x=x.head(miwsBars)
            print (x)
            # Chart showing accuracy prediction for Lie detection
            chartTitle = "Distribution of Observations by Label for Dataset =>"+whichLabel+"<="
            Sctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", Sctl, msgfh_)
            accu=list(y)
            #print(accu)
            from matplotlib.cm import inferno, viridis
            nbcurves=len(y) # either 20 or less than
            colors = viridis(np.linspace(0, 1, nbcurves))
            fig, ax = plt.subplots(figsize=(11, 7))
            plt.ylim(0,max(y)*1.2)
            #plt.ylim((0,.8))
            bars = plt.bar(x, height=y, width=.8, color=colors)
            xlocs, xlabs = plt.xticks()
            xlocs=[i for i in x]
            xlabs=[i for i in x]
            plt.ylabel('Count')
            plt.xlabel('Labels')
            plt.title(chartTitle)
            plt.xticks(xlocs, xlabs)
            ax.set_xticklabels(xlabs, rotation = 0)
            which=0
            print(y)
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x()+.4, yval + -20, accu[which], ha='center', color='#FFFFFF', size=8, rotation=0)
                which+=1
            if DRV.saveChart==1:
                plt.savefig(distFN)
            plt.show()

            ########################################################
            ## print chart showing count by topic of 
            ## documents whose best score is in the associated topic
            ########################################################
            bestTopicPerDocFN=logFileNamestrt+"_btpd_"+whichLabel+".pdf"
            bestTopicPerDocBars=30
            import collections
            #print(ListOfLabels)
            counter=collections.Counter(OurTopicsDFplus.whichCol)
            #print(ListOfLabels)
            y=counter.values()
            #print(y)
            #print (x)
            print (list(y)[0:29])
            x=counter.keys()
            if len(y) > bestTopicPerDocBars:
                #y=y.head(bestTopicPerDocBars)
                y=list(y)[0:bestTopicPerDocBars-1]
                #x=x.head(bestTopicPerDocBars)
                x=list(x)[0:bestTopicPerDocBars-1]
            # Chart showing accuracy prediction for Lie detection
            chartTitle = "Distribution of Best Topic by Document for Dataset =>"+whichLabel+"<="
            Sctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", Sctl, msgfh_)
            accu=list(y)
            #print(accu)
            from matplotlib.cm import inferno, viridis
            nbcurves=len(y) # either 20 or less than
            colors = viridis(np.linspace(0, 1, nbcurves))
            fig, ax = plt.subplots(figsize=(11, 7))
            plt.ylim(0,max(y)*1.2)
            #plt.ylim((0,.8))
            bars = plt.bar(x, height=y, width=.8, color=colors)
            xlocs, xlabs = plt.xticks()
            xlocs=[i for i in x]
            xlabs=[i for i in x]
            plt.ylabel('Count')
            plt.xlabel('Labels')
            plt.title(chartTitle)
            plt.xticks(xlocs, xlabs)
            ax.set_xticklabels(xlabs, rotation = 0)
            which=0
            print(y)
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x()+.4, yval + -5, accu[which], ha='center', color='#FFFFFF', size=8, rotation=0)
                which+=1
            if DRV.saveChart==1:
                plt.savefig(bestTopicPerDocFN)
            plt.show()
            #
            # no stack with labels
            # https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/bar_stacked.html
            # https://pstblog.com/2016/10/04/stacked-charts (shows how to organize data!)

            Sctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", Sctl, msgfh_)
            # set variables
            btpdsFN=logFileNamestrt+"_btpdStack_"+whichLabel+".pdf"
            btpdsBars=30
            chartTitle = "Distribution of Best Topic by Document By Label for Dataset =>"+whichLabel+"<="
            # prep the data
            zzz=pd.DataFrame(OurTopicsDFplus.groupby('label')['whichCol'].value_counts().unstack().fillna(0).stack())
            zzz.columns = ['count']
            zzz=zzz.reset_index()
            zzz.columns = ['label', 'topic', 'count']
            btpdStack = list(OurTopicsDFplus['label'].drop_duplicates())
            btpdY = np.zeros(len(OurTopicsDFplus['whichCol'].drop_duplicates()))
            # colors
            from matplotlib.cm import inferno, viridis
            nbcurves=len(btpdStack)
            colors = viridis(np.linspace(0, 1, nbcurves))
            #chart stuff
            fig, ax = plt.subplots(figsize=(10,7))
            #plt.ylim(0,max(y)*1.2)
            #plt.ylim((0,.8))
            #bars = plt.bar(x, height=y, width=.8, color=colors)
            #xlocs, xlabs = plt.xticks()
            #xlocs=[i for i in x]
            #xlabs=[i for i in x]
            plt.ylabel('Count')
            plt.xlabel('Labels')
            plt.title(chartTitle)
            #plt.xticks(xlocs, xlabs)
            #ax.set_xticklabels(xlabs, rotation = 0)            
            for num, label in enumerate(btpdStack):
                values=list(zzz[zzz.label==label]['count'])
                zzz[zzz.label==label].plot.bar(x='topic',y='count', ax=ax, stacked=True, 
                                    bottom = btpdY, color=colors[num], label=label, width=.8)
                btpdY = np.add(btpdY, values, dtype=float)
            if DRV.saveChart==1:
                plt.savefig(btpdsFN)
            plt.show()

                    ################
                    ################
                    #print (wlabel, "xxx", wfn)
    
        elif createCorpus=="Text":
            print ('no text')
            
        import nltk
        import pandas as pd
        import sklearn
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.feature_extraction.text import TfidfTransformer
        from nltk.tokenize import word_tokenize
        from nltk.probability import FreqDist
        import matplotlib.pyplot as plt
        from nltk.corpus import stopwords
        from wordcloud import WordCloud
        ## For Stemming
        from nltk.stem import PorterStemmer
        from nltk.tokenize import sent_tokenize, word_tokenize
    
        from nltk.stem.wordnet import WordNetLemmatizer
        from nltk.stem.porter import PorterStemmer
            
        cvIter=0 # Iteration count for each cycle through
#        AccuracyMNBnnK=0
#        AccuracyMultiNB=0
#        AccuracyBernoulliNB=0
#        AccuracySVM=0
#        AccuracyRF=0
    
    #    max_df_val = np.array([.4])
    #    min_df_val = np.array([8])
    #    #max_df_val = np.array([.2, .4, .6, .8])
    #    #min_df_val = np.array([4, 8, 12])
    #    for min_df_sel in min_df_val:
    #        for max_df_sel in max_df_val:
                
        for zzouterloop in iterDict:
            for zzinnerloop in [1]:
                zzrulename=zzouterloop[0]
                zzvtype=zzouterloop[1]
                max_df_sel=zzouterloop[2]
                min_df_sel=zzouterloop[3]
                zzstopwords=zzouterloop[4]
                zzngramlength=zzouterloop[5]
                zzlowercase=zzouterloop[6]
                zzanalyzer=zzouterloop[7]
                zztokenpattern=zzouterloop[8]
                zzmaxfeatures=zzouterloop[9]
                zzlSVCconverge=zzouterloop[10]
                cvIter+=1
                if DRV.mustVectorize==0:
                    Sctl=show_run_msg (3, 'main', "CountVectorizer iteration number not required", Sctl, msgfh_)
                elif DRV.mustVectorize==1:
                    zztitle='Iteration number =>'+str(cvIter)+'<= rule name =>'+zzrulename+'<= with process =>'+DRV.whichProcess+'<= and vectorizer =>'+zzvtype+"<="
                    Sctl=show_run_msg (3, 'main', zztitle, Sctl, msgfh_)
                    Sctl=show_run_msg (3, 'sub', 'min_df_sel==>'+str(min_df_sel)+' max_df_sel==>'+str(max_df_sel), Sctl, msgfh_)
                    kmeansstrt=time.strftime('%Y%m%d%H%M%S')
                    #MyVect3=CountVectorizer(input='filename'
                    if createCorpus=="":
                        Sctl=show_run_msg (3, 'main', "Skipping Vectorizer", Sctl, msgfh_)
                    elif createCorpus=="Files":
                        Sctl=show_run_msg (3, 'sub', zzvtype+" with filename list as input" +"", Sctl, msgfh_)
                        if zzvtype=='CountVectorizer':
                            MyVect5=CountVectorizer(input='filename'
                                            , encoding='latin-1'
                                            #, tokenizer=LemmaTokenizer()
                                            , lowercase=zzlowercase
                                            , stop_words=zzstopwords #string {‘english’}, list, or None (default)
                                            , ngram_range=(1, zzngramlength)
                                            , analyzer=zzanalyzer
                                            , token_pattern=zztokenpattern
                                            , max_df = max_df_sel # ignore terms that appears in more than 20% of documents
                                            , min_df = min_df_sel # ignore terms that appears in more than x documents
                                            , max_features = zzmaxfeatures
                                            ) 
                        elif zzvtype=='TfidfVectorizer':
                            MyVect5=TfidfVectorizer(input='filename'
                                            #, tokenizer=LemmaTokenizer()
                                            , encoding='latin-1'
                                            , use_idf=True
                                            , lowercase=zzlowercase
                                            , stop_words=zzstopwords #string {‘english’}, list, or None (default)
                                            , ngram_range=(1, zzngramlength)
                                            , analyzer=zzanalyzer
                                            , token_pattern=zztokenpattern
                                            , max_df = max_df_sel # ignore terms that appears in more than 20% of documents
                                            , min_df = min_df_sel # ignore terms that appears in more than x documents
                                            , max_features = zzmaxfeatures
                                            ) 
                        ## NOw I can vectorize using my list of complete paths to my files

                        X_train_vec=MyVect5.fit_transform(ListOfCompleteFilePaths)
                        #X_train_vec=MyVect5.fit_transform(X_train)
                        #print('xts', X_train_vec.shape)
    
                        # how many features        
                        ColumnNames5=MyVect5.get_feature_names()
                        Sctl=show_run_msg (3, 'sub', "Show feature names", Sctl, msgfh_)
                        Sctl=show_run_msg (3, 'sub', "Number of features", Sctl, msgfh_)
                        Sctl=show_run_data (3, 'xxx' , len(ColumnNames5), Sctl, msgfh_)
                        Sctl=show_run_msg (3, 'sub', "First 40 features", Sctl, msgfh_)
                        Sctl=show_run_data (3, 'xxx' , ColumnNames5[:40], Sctl, msgfh_)
     
                        #print("Features:")
                        #print(len(ColumnNames5))
                        #print (ColumnNames5)
                        #1/0
                
                        #print(builder)
                        builder=pd.DataFrame(X_train_vec.toarray(),columns=ColumnNames5)
                        Sctl=show_run_msg (3, 'sub', "Now we have a builder DTM", Sctl, msgfh_)
                        Sctl=show_run_msg (3, 'sub', "Shape of Topic Model (DTM)", Sctl, msgfh_)
                        Sctl=show_run_data (3, 'xxx' , builder.shape, Sctl, msgfh_)
                        Sctl=show_run_msg (3, 'sub', "Number of empty cells in DTM", Sctl, msgfh_)
                        if DRV.isVecWCrqd==1:
                            cntCellsEmpty=pd.DataFrame((builder==0).sum(axis=0)).sum(axis=0)[0]
                        elif DRV.isVecWCrqd==0:
                            cntCellsEmpty=0
                        Sctl=show_run_data (3, 'xxx' , cntCellsEmpty, Sctl, msgfh_)
                        Sctl=show_run_msg (3, 'sub', "Number of cells with a value in DTM", Sctl, msgfh_)
                        if DRV.isVecWCrqd==1:
                            cntCellsWithVal=pd.DataFrame((builder!=0).sum(axis=0)).sum(axis=0)[0]
                        elif DRV.isVecWCrqd==0:
                            cntCellsWithVal=0
                        Sctl=show_run_data (3, 'xxx' , cntCellsWithVal, Sctl, msgfh_)
                        Sctl=show_run_msg (3, 'sub', "Sum of values in DTM", Sctl, msgfh_)
                        if DRV.isVecWCrqd==1:
                            sumCellsWithVal=pd.DataFrame((builder).sum(axis=0)).sum(axis=0)[0]
                        elif DRV.isVecWCrqd==0:
                            sumCellsWithVal=0
                        Sctl=show_run_data (3, 'xxx' , sumCellsWithVal, Sctl, msgfh_)
    
                        ## Add column
                        #print("Adding new column....")
                        builder["Label"]=ListOfLabels
                        #print(builder)
                        FinalDF = builder

                    elif createCorpus=="Text":
                        Sctl=show_run_msg (3, 'main', "Skipping Vectorizer with TEXT", Sctl, msgfh_)
                                
                        ## Replace the NaN with 0 because it actually 
                        ## means none in this case
                    #FinalDF=FinalDF.fillna(0)
    
                    ###########################################################
                    # wordcloud
                    ###########################################################
                    
                    Sctl=WCChart(whichLabel
                                      , 'Wordcloud from Frequencies for '+whichLabel
                                      , X_train_vec
                                      , MyVect5
                                      , cvIter
                                      , logFileNamestrt
                                      , DRV
                                      , Sctl
                                      , msgfh_)
                    
                    ###############################################################
                    ## see ipynb in week 7 asynch week7_tutorial-sklearn-linearsvc RP
                    ## section 3.1
                    ###############################################################                    

                    # check the size of the constructed vocabulary
                    print(len(MyVect5.vocabulary_))
                    
                    # print out the first 10 items in the vocabulary
                    print(list(MyVect5.vocabulary_.items())[:10])

                    ###############################################################
                    ## see ipynb in week 7 asynch week7_tutorial-sklearn-linearsvc RP
                    ## section 3.2
                    ##
                    ## Vectorize TEST data based on using TRAINING data vocabulary
                    ###############################################################                    
                    #Sctl=show_run_msg (3, 'sub', "Vectorize TEST data" +"", Sctl, msgfh_)

                    #X_test_vec = MyVect5.transform(X_test)
                    # print out #examples and #features in the test set
                    #print(X_test_vec.shape)
                    
                    ###############################################################
                    #### Print important words chart ##############################
                    ###############################################################
                    miwsFN=logFileNamestrt+"_miws_"+whichLabel+"_"+str(cvIter)+".pdf"
                    miwsBars=30
                    miwsDF = pd.DataFrame(X_train_vec.todense(), columns=ColumnNames5)
                    miwsDFgt0 = pd.melt(miwsDF.reset_index(), 
                                          id_vars=['index'], 
                                          value_name='tfidf').query('tfidf > 0')
                    miwsDFlg=miwsDFgt0.groupby('variable', as_index=False)['tfidf'].mean()
                    miwsDFls=miwsDFlg.sort_values(by=["tfidf"],ascending=False)
                    if len(miwsDFls) > miwsBars:
                        miwsDFls=miwsDFls.head(miwsBars)
                
                    # Chart showing accuracy prediction for Lie detection
                    chartTitle = "Top "+str(miwsBars)+" most Important Words for label =>"+whichLabel+"<= eval no. "+str(cvIter)
                    #Sctl=show_run_msg (3, 'main', 'Chart for '+chartTitle+"", Sctl, msgfh_)
                    x=miwsDFls.variable
                    ydf=pd.DataFrame(miwsDFls.tfidf)
                    ydf.reset_index(drop=True)
                    ydf.columns=['tfidf']
                    y=(ydf.tfidf)
                    #print(y)
                    accu=list((round((y),4)).astype('str'))
                    #print(accu)
                    from matplotlib.cm import inferno, viridis
                    nbcurves=len(miwsDFls) # either 20 or less than
                    colors = viridis(np.linspace(0, 1, nbcurves))
                    fig, ax = plt.subplots(figsize=(11, 7))
                    plt.ylim(0,max(y)*1.2)
                    #plt.ylim((0,.8))
                    bars = plt.bar(x, height=y, width=.8, color=colors)
                    xlocs, xlabs = plt.xticks()
                    xlocs=[i for i in x]
                    xlabs=[i for i in x]
                    plt.ylabel('term frequency')
                    plt.xlabel('Words')
                    plt.title(chartTitle)
                    plt.xticks(xlocs, xlabs)
                    ax.set_xticklabels(xlabs, rotation = 90)
                    which=0
                    for bar in bars:
                        yval = bar.get_height()
                        plt.text(bar.get_x()+.4, yval + -5, accu[which], ha='center', color='#FFFFFF', size=8, rotation=90)
                        which+=1
                    if DRV.saveChart==1:
                        plt.savefig(miwsFN)
                    plt.show()
                    #end of must Vectorize

               
                #################################################################
                #################################################################
                ### RUN MODELS HERE - look at HW_7_Paterson_Richard.py line 637-639
                #################################################################
                #################################################################

                AccuracyMNBnnK=0
                AccuracyMultiNB=0
                AccuracyBernoulliNB=0
                AccuracySVM=0
                AccuracyRF=0
                accuracyLinearSVC=0
                linearSVCTrainStart=''
                linearSVCTrainEnd=''
                linearSVCTestStart=''
                linearSVCTestEnd=''
    
                if DRV.mustModel==0:
                    Sctl=show_run_msg (3, 'main', "Model execution not requested", Sctl, msgfh_)
                elif DRV.mustModel==1:
                    Sctl=show_run_msg (3, 'main', "Model execution requested - NOTHING TO RUN", Sctl, msgfh_)
                elif DRV.mustModel==999: #old version under HW_6
                    ###################################
                    ## I took out a significant amount of prediction code from HW6...
                    1/0 # this is here to make sure that all subsequent code indentation is good
                # end of mustModel
                
                thisKPI=[KPIcounter
                     , whichLabel
                     , createCorpus
                     , cvIter
                     , zzrulename
                     , zzvtype
                     , DRV.whichProcess
                     , max_df_sel
                     , min_df_sel
                     , zzstopwords
                     , zzngramlength
                     , zzlowercase
                     , zzanalyzer
                     , zztokenpattern
                     , zzmaxfeatures
                     , zzlSVCconverge
                     , DRV.mustVectorize
                     , DRV.mustModel
                     , (builder.shape)[0]# number of docs / text items
                     , len(ColumnNames5) # of features
                     , cntCellsEmpty
                     , cntCellsWithVal
                     , sumCellsWithVal
                     ]
                perfKPI.append(thisKPI)
                KPIcounter+=1
    
    ####################################
    ## end of processing for al llabels
    ####################################
    Sctl=show_run_msg (3, 'main', 'Print table of all KPIs', Sctl, msgfh_)   
    for oneKPI in perfKPI:
        print(oneKPI, '\n')
        
    KPIDF=pd.DataFrame(perfKPI)
    KPIDF.columns=['KPIcounter'
                     , 'whichLabel'
                     , 'createCorpus'
                     , 'cvIter'
                     , 'Vrulename'
                     , 'Vvtype'
                     , 'Vwhichprocess'
                     , 'Vmax_df_sel'
                     , 'Vmin_df_sel'
                     , 'Vstopwords'
                     , 'Vngramlength'
                     , 'Vlowercase'
                     , 'Vanalyzer'
                     , 'Vtokenpattern'
                     , 'Vmaxfeatures'
                     , 'VlSVCconverge'
                     , 'mustVectorize'
                     , 'mustModel'
                     , 'NoObservations'
                     , 'NoFeatures'
                     , 'cntCellsEmpty'
                     , 'cntCellsWithVal'
                     , 'sumCellsWithVal'
                     ]
    KPIDF.to_csv(KPIfilename, sep=",", index=False)
else:
    Sctl=show_run_msg (3, 'main', 'PARAMETER ERROR: Vectorizing and Modeling can only be 0 or 1', Sctl, msgfh_)


# THIS IS THE END OF ALL EXECUTION ############################################

Sctl=show_run_msg (3, 'main', time.strftime('%c'), Sctl, msgfh_)

msgfh_.close()
