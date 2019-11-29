@echo off

rem Text Mining IST 736 Assignment Final Project 
rem objective of this program is to run thru multiple sets of execution of MALLET
rem each iteration set = one set of data
rem   ALL means use all data f-d, f-r, m-d, m-r
rem   fd means f-d
rem   md means m-d
rem   fr means f-rd
rem   etc
rem within iteration set run an iteration and vary the number of topics
rem   topic range is 2, 4, 6, 8, 10, 12 (6 different ranges)
rem allow for number of iterations within a training set, this is set to 
rem   100
rem with a training set optimize interval of 10
rem
rem this means that we have 9 x 6 x 10 ll/token reported

rem Date in 24h fformat
FOR /F "skip=1" %%A IN ('WMIC OS GET LOCALDATETIME') DO (SET "t=%%A" & GOTO break_1)
:break_1
set brf="FNb_log_%t:~0,4%%t:~4,2%%t:~6,2%_%t:~8,2%%t:~10,2%%t:~12,2%.txt"
rem echo "%brf%"
echo start > %brf%

rem number of iterations per train
set mni=150

rem #######################
rem iteration 1 ALL dir 110
set iter=1
set mtp=ALL
set mid=liar_data_files

set mto=2
call :subr
set mto=4
call :subr
set mto=6
call :subr
set mto=8
call :subr
set mto=10
call :subr
set mto=15
call :subr
set mto=20
call :subr
set mto=30
call :subr
set mto=40
call :subr
set mto=50
call :subr

exit /b

rem **********************************************************************************

:subr

set mfn=FNb_mallet_%iter%_%mtp%_%mto%_file.mallet
set mosfn=FNb_mallet_%iter%_%mtp%_%mto%_outputstate.gz
set mkefn=FNb_mallet_%iter%_%mtp%_%mto%_keys.txt
set mtofn=FNb_mallet_%iter%_%mtp%_%mto%_topics.txt

echo iter %iter% import %date% %time% with files in %mid% topics %mto% num_iterations %mni%
echo iter %iter% import %date% %time% with files in %mid% topics %mto% num_iterations %mni% %mfn% %mosfn% %mkefn% %mtofn% >> "%brf%" 2>&1

call c:\\Users\Richpat\\mallet-2.0.8\\bin\\mallet.bat import-dir --input  "%mid%"  --output "%mfn%" --keep-sequence --remove-stopwords --gram-sizes 1 >> %brf% 2>&1

echo iter %iter% train %date% %time% with files in %mid% topics %mto% num_iterations %mni%
echo iter %iter% train %date% %time% with files in %mid% topics %mto% num_iterations %mni% %mfn% %mosfn% %mkefn% %mtofn%>> "%brf%" 2>&1

call c:\\Users\Richpat\\mallet-2.0.8\\bin\\mallet.bat train-topics --input "%mfn%" --num-topics "%mto%" --optimize-interval 15 --output-state "%mosfn%" --output-topic-keys "%mkefn%" --output-doc-topics "%mtofn%" --num-iterations "%mni%" >> %brf% 2>&1
