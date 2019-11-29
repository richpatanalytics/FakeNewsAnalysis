# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 10:00:00 2019

@author: Rich Paterson
"""

# Name : FNa_CreateFileCorpus
# Author : Richard Paterson
# Original Date : 11/29/2019 
# Overview:
#
# From a dataset (in the first case using the “liar_dataset”) a tsv based file, 
# create a corpus with directories representing labels and 
# individual files containing the text.
#
# This will create the required directory structure as well
#                         start dir
#                         /  \
#                        /    \
#                      dir    dir   (equates to label on observation on file)
#                       /      \
#                      /        \
#                    filename  filename    (each filename equates to text observation on file)
#                    filename  filename
# Process:
# 1. Read observation from source
# 2. check and create directory as necessary
# 3. create file based on observation, using ID on file as filename 
#
# Credits:
#
###########################################################################
#setup
###########################################################################

import pandas as pd #data frame operations
import numpy as np #arrays and math functions

import sys
import warnings
import platform
import os
import datetime

warnings.simplefilter(action='ignore', category=FutureWarning)

def checkANDmakeDIR (inDir, makeDir):
    #inDir MUST exist as a starting point
    #makeDir migh exist, if exists skip, if NOT exists, create
    if not os.path.isdir(inDir):
        print ('inDir does NOT exist ==>'+inDir+"<==")
    else:
        #print ('inDir does exist ==>'+inDir+"<==")
        if (os.path.isdir(inDir+"/"+makeDir)):
            #print ('makeDir does exist ==>'+inDir+"/"+makeDir+"<==")
            camd=0 #dummy
        else:
            #print ('makeDir required ==>'+inDir+"/"+makeDir+"<==")
            os.mkdir(inDir+"/"+makeDir)

##########################
#-- M A I N   S T A R T --
##########################

wdir="C:/Users/Richpat/Documents/@syracuse coursework/@IST 736 Text Mining/@finalproject/"
sourceFileName="liar_dataset/train.tsv"
targetDir="liar_data_files"

print("Current Working Directory (before seeting for this execution) " , os.getcwd())
os.chdir(wdir)
print("Current Working Directory for this execution" , os.getcwd())
print("Datafile that input will be sourced from is", sourceFileName)
print("Directory that data files will be written to is", targetDir)

#print('Python is ' + platform.python_version())

#pd.show_versions(as_json=True) # True to shorten output

checkANDmakeDIR('.', targetDir)

cntLabelPipe={}
cntIter=0
with open (sourceFileName, "r", encoding="utf-8") as rawin:
    for data in rawin.readlines():
        cntIter+=1
        if 0 == cntIter%1000:
            print ('Created ==>', cntIter, '<== files so far spread across these labels')
            for i in cntLabelPipe:
                    print('\tFor label ==>', i, '<== Number of files created (from observations is)', cntLabelPipe.get(i))
        lowerdata=data.lower().strip()
        splitdata=lowerdata.split("\t")
        checkANDmakeDIR(targetDir, splitdata[1])
        cntLabelPipe.__setitem__(splitdata[1],1+cntLabelPipe.get(splitdata[1],0))
#        if cntIter > 5:
#            break
        newFN=targetDir+"/"+splitdata[1]+'/'+splitdata[0]
        rawout = open(newFN,"w", encoding="utf-8")
        rawout.write(splitdata[2])
        rawout.close()

rawin.close()

print ("\n")
print ("PROCESS COMPLETED")
print ("=================")
print ("No records on original file", cntIter)
print ("No records by label written to output dirs")
for i in cntLabelPipe:
    print('For label ==>', i, '<== Number of files created (from observations is)', cntLabelPipe.get(i))
