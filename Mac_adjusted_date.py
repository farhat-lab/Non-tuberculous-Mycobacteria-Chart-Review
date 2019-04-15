
import re
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
#%matplotlib inline
import numpy as np
import pickle
import sys
from med_reports import MedicalReport
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats import multitest
import scipy.stats as stats
from datetime import datetime
from tableone import TableOne
import math
import nltk

#------------Demographics Extraction--------------#
file = 'Demographics.txt'
Demographics = open(file, 'r')
text = Demographics.read()
Demographics.close()
pattern = re.compile(r'(\d+)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|(\w+)\|(\d+\/\d+\/\d+)\|(\d+)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|(.*)')
matches = pattern.findall(text)


demodict_age = defaultdict(list)
demodict_dob = defaultdict(list)
demodict_race = defaultdict(list)
demodict_death = defaultdict(list)
demodict_gender = defaultdict(list)
demodict_EMPI = defaultdict(list)
demodict_datedeath = defaultdict(list)
demodict_MRN = defaultdict(list)
demodict_MRN_type = defaultdict(list)
for match in matches:
    demodict_age[match[0]] = match[5]
    demodict_dob[match[0]] = match[4]
    demodict_race[match[0]] = match[7]
    demodict_death[match[0]] = match[13]
    demodict_gender[match[0]] = match[3]
    demodict_EMPI[match[0]] = match[0]
    demodict_datedeath[match[0]] = match[14]

Age = pd.Series(demodict_age)
Age = pd.DataFrame(Age, columns = ['Age'])
dob = pd.Series(demodict_dob)
dob = pd.DataFrame(dob, columns = ['DOB'])
Race = pd.Series(demodict_race)
Race = pd.DataFrame(Race, columns = ['Race'])
Death = pd.Series(demodict_death)
Death = pd.DataFrame(Death, columns = ['Death'])
Gender = pd.Series(demodict_gender)
Gender = pd.DataFrame(Gender, columns = ['Gender'])
Death = pd.Series(demodict_death)
Death = pd.DataFrame(Death, columns = ['Living?'])
Date_death = pd.Series(demodict_datedeath)
Date_death = pd.DataFrame(Date_death, columns = ['Date of Death'])

NTB_diagnosis_mindate_pickle_in = open('NTB_diagnosis_mindate.pickle','rb') ##### Note that Diagnosis file should be extracted first in order to produce data frames for date of first diagnosis, date of last diagnosis, and dataframe for  comorbidities (this expedities extraction speed because .pickle files can be loaded)
NTB_diagnosis_mindate = pickle.load(NTB_diagnosis_mindate_pickle_in)

NTB_diagnosis_mindate = pd.DataFrame(NTB_diagnosis_mindate)
Demographics = []
Age_atDx = NTB_diagnosis_mindate.join(dob)
Age_atDx['DOB'] = pd.to_datetime(Age_atDx['DOB'])
Age_atDx['Age at the time of Dx'] = ((Age_atDx['Date of first Dx'] - Age_atDx['DOB']).dt.days/365)
Age_atDx['Age at the time of Dx']
Demographics = Race.join(Gender)
Demographics = Demographics.join(Death, how='outer')
Demographics = Demographics.join(Date_death, how='outer')

Demographics.index.name = 'Index'
Demographics = Demographics.astype({'Gender':'category', 'Race':'category'})
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(White|WHITE).*)', 'White')
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(Black|BLACK).*)', 'Black/African American')
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(Not|not|no|NO|other|OT).*)', 'Not Available')
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(Hispa|hispa|Latino|latino).*)', 'Hispanic/Latino')
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(Asian|ASIAN).*)', 'Asian')
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(Hawa|HA).*)', 'Native Hawaiian')
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(Americ).*)', 'American Indian')
Demographics['Race'] = Demographics['Race'].str.replace(r'(^.*(Asian|ASIAN).*)', 'Asian')
def func(c):
    if c['Race'] == 'White':
        return 'White/Caucasian'
    else:
        return 'Race other than White/Caucasian'
Demographics['Race'] = Demographics.apply(func, axis=1)
Demographics['Living?'] = Demographics['Living?'].str.replace(r'(^.*(Not|no|not|No).*)', 'Living')
Demographics['Living?'] = Demographics['Living?'].str.replace(r'(^.*(Reported|reported).*)', 'Deceased')
Demographics['Date of Death'] = Demographics['Date of Death'].str.replace(r'(^.*(Unknown).*)', '')
Demographics['Date of Death'] = pd.to_datetime(Demographics['Date of Death'])
Demographics['Age at the time of Dx'] = Age_atDx['Age at the time of Dx']
Demographics
# Demographics['Age at the time of Dx'] = Demographics['Age at the time of Dx'].fillna(0).astype(int)
# Demographics['Age at the time of Dx'

#---------------Medications-------------------#
Med_file = 'Medications.txt'
med_f = open(Med_file, 'r+')
Med_text = med_f.read()
pattern_med =re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(?:(?!\|).)*\|(?:(?!\|).)*\|(?:(?!\|).)*\|(?:(?!\|).)*\|(?:(?!\|).)*\|(?:(?!\|).)*\|')
matches_med = pattern_med.findall(Med_text)
NTB_diagnosis_mindate
ethambutol_date = []
ethambutol = []
ethambutol_EMPI = []
clarithromycin = []
clarithromycin_date = []
clarithromycin_EMPI = []
rifampicin = []
rifampicin_date = []
rifampicin_EMPI = []
rifabutin = []
rifabutin_date = []
rifabutin_EMPI = []
bedaquiline = []
bedaquiline_date = []
bedaquiline_EMPI = []
isoniazid = []
isoniazid_date = []
isoniazid_EMPI = []
clofazimine = []
clofazimine_date = []
clofazimine_EMPI = []
amikacin = []
amikacin_date = []
amikacin_EMPI = []
azithromycin = []
azithromycin_date = []
azithromycin_EMPI = []
moxifloxacin = []
moxifloxacin_date = []
moxifloxacin_EMPI = []
levofloxacin = []
levofloxacin_date =[]
levofloxacin_EMPI = []
kanamycin = []
kanamycin_date = []
kanamycin_EMPI = []
tobramycin = []
tobramycin_date = []
tobramycin_EMPI = []
capreomycin = []
capreomycin_date = []
capreomycin_EMPI = []
gentamicin = []
gentamicin_date = []
gentamicin_EMPI = []
linezolid = []
linezolid_date = []
linezolid_EMPI = []
cefoxitin = []
cefoxitin_date = []
cefoxitin_EMPI = []
ceftaroline = []
ceftaroline_date = []
ceftaroline_EMPI = []
imipenem = []
imipenem_date = []
imipenem_EMPI = []
meropenem = []
meropenem_date = []
meropenem_EMPI = []
tigecycline = []
tigecycline_date = []
tigecycline_EMPI = []
bactrim = []
bactrim_date = []
bactrim_EMPI = []
doxycycline = []
doxycycline_date = []
doxycycline_EMPI = []

for match_med  in pattern_med.findall(Med_text):
    if re.search(r'(?i)ethambutol', match_med[4]):
        ethambutol_date.append(match_med[3])
        ethambutol_EMPI.append(match_med[0])
        ethambutol.append('Ethambutol')
    elif re.search(r'(?i)clarithromycin', match_med[4]):
        clarithromycin_date.append(match_med[3])
        clarithromycin_EMPI.append(match_med[0])
        clarithromycin.append('Clarithromycin')
    elif re.search(r'(?i)(rifamp|rifabutin)', match_med[4]):
        rifampicin_date.append(match_med[3])
        rifampicin_EMPI.append(match_med[0])
        rifampicin.append('Rifampicin')
    elif re.search(r'(?i)rifabutin', match_med[4]):
        rifabutin_date.append(match_med[3])
        rifabutin_EMPI.append(match_med[0])
        rifabutin.append('Rifampicin')
    elif re.search(r'(?i)Bedaquiline', match_med[4]):
        bedaquiline_date.append(match_med[3])
        bedaquiline_EMPI.append(match_med[0])
        bedaquiline.append('Bedaquiline')
    elif re.search(r'(?i)isoniazid', match_med[4]):
        isoniazid_date.append(match_med[3])
        isoniazid_EMPI.append(match_med[0])
        isoniazid.append('Isoniazid')
    elif re.search(r'(?i)clofazimine', match_med[4]):
        clofazimine_date.append(match_med[3])
        clofazimine_EMPI.append(match_med[0])
        clofazimine.append('Clofazimine')
    elif re.search(r'(?i)amikacin', match_med[4]):
        amikacin_date.append(match_med[3])
        amikacin_EMPI.append(match_med[0])
        amikacin.append('Amikacin')
    elif re.search(r'(?i)azithromycin', match_med[4]):
        azithromycin_date.append(match_med[3])
        azithromycin_EMPI.append(match_med[0])
        azithromycin.append('Azithromycin')
    elif re.search(r'(?i)Moxifloxacin', match_med[4]):
        moxifloxacin_date.append(match_med[3])
        moxifloxacin_EMPI.append(match_med[0])
        moxifloxacin.append('Moxifloxacin')
    elif re.search(r'(?i)Levofloxacin', match_med[4]):
        levofloxacin_date.append(match_med[3])
        levofloxacin_EMPI.append(match_med[0])
        levofloxacin.append('Levofloxacin')
    elif re.search(r'(?i)Kanamycin', match_med[4]):
        kanamycin_date.append(match_med[3])
        kanamycin_EMPI.append(match_med[0])
        kanamycin.append('Kanamycin')
    elif re.search(r'(?i)Tobramycin', match_med[4]):
        tobramycin_date.append(match_med[3])
        tobramycin_EMPI.append(match_med[0])
        tobramycin.append('Tobramycin')
    elif re.search(r'(?i)Capreomycin', match_med[4]):
        capreomycin_date.append(match_med[3])
        capreomycin_EMPI.append(match_med[0])
        capreomycin.append('Capreomycin')
    elif re.search(r'(?i)Gentamicin', match_med[4]):
        gentamicin_date.append(match_med[3])
        gentamicin_EMPI.append(match_med[0])
        gentamicin.append('Gentamicin')
    elif re.search(r'(?i)Linezolid', match_med[4]):
        linezolid_date.append(match_med[3])
        linezolid_EMPI.append(match_med[0])
        linezolid.append('Linezolid')
    elif re.search(r'(?i)Cefoxitin', match_med[4]):
        cefoxitin_date.append(match_med[3])
        cefoxitin_EMPI.append(match_med[0])
        cefoxitin.append('Cefoxitin')
    elif re.search(r'(?i)Ceftaroline', match_med[4]):
        ceftaroline_date.append(match_med[3])
        ceftaroline_EMPI.append(match_med[0])
        ceftaroline.append('Ceftaroline')
    elif re.search(r'(?i)Imipenem', match_med[4]):
        imipenem_date.append(match_med[3])
        imipenem_EMPI.append(match_med[0])
        imipenem.append('Imipenem')
    elif re.search(r'(?i)Meropenem', match_med[4]):
        meropenem_date.append(match_med[3])
        meropenem_EMPI.append(match_med[0])
        meropenem.append('Meropenem')
    elif re.search(r'(?i)Tigecycline', match_med[4]):
        tigecycline_date.append(match_med[3])
        tigecycline_EMPI.append(match_med[0])
        tigecycline.append('Tigecycline')
    elif re.search(r'(?i)Bactrim', match_med[4]):
        bactrim_date.append(match_med[3])
        bactrim_EMPI.append(match_med[0])
        bactrim.append('Bactrim')
    elif re.search(r'(?i)Doxycycline', match_med[4]):
        doxycycline_date.append(match_med[3])
        doxycycline_EMPI.append(match_med[0])
        doxycycline.append('Doxycycline')





Ethambutol = pd.DataFrame({'Index':ethambutol_EMPI, 'Date':ethambutol_date, 'Ethambutol':ethambutol})
Ethambutol['Date'] = pd.to_datetime(Ethambutol['Date'])
Ethambutol_gb = Ethambutol.groupby('Index')
Ethambutol_min = Ethambutol_gb.agg({'Date':np.min})
Ethambutol_max = Ethambutol_gb.agg({'Date':np.max})
Ethambutol_min = Ethambutol_min.rename(columns={"Date": "Date of first Ethambutol Rx"})
Ethambutol_max = Ethambutol_max.rename(columns={"Date": "Date of last Ethambutol Rx"})
Ethambutol_minmax = Ethambutol_min.join(Ethambutol_max, how='outer')
Ethambutol_minmax['Duration of Ethambutol Rx days'] = ((Ethambutol_minmax['Date of last Ethambutol Rx'] - Ethambutol_minmax['Date of first Ethambutol Rx']).dt.days).abs()
Ethambutol_counts = Ethambutol_gb['Ethambutol'].value_counts()
Ethambutol_counts = pd.DataFrame(Ethambutol_counts)
Ethambutol_counts = Ethambutol_counts.rename(columns={"Ethambutol": "# of Ethambutol Rx"})
Ethambutol_counts = Ethambutol_counts.reset_index()
Ethambutol_counts = Ethambutol_counts.set_index('Index')
Ethambutol_minmax['# of Ethambutol Rx'] = Ethambutol_counts["# of Ethambutol Rx"]
def function_Ethambutol(c):
    if c['Duration of Ethambutol Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Ethambutol_minmax['Multiple Ethambutol Tx courses'] = Ethambutol_minmax.apply(function_Ethambutol, axis=1)
Ethambutol = Ethambutol.set_index('Index')
Ethambutol = Ethambutol.drop('Ethambutol', axis=1)
Ethambutol_ori = Ethambutol
Ethambutol = Ethambutol.join(Ethambutol_max, how='outer')
Ethambutol['Difference'] = ((Ethambutol['Date'] - Ethambutol['Date of last Ethambutol Rx']).dt.days).abs()
Ethambutol_recent = Ethambutol.loc[Ethambutol['Difference'] <= 274]
Ethambutol_recent = Ethambutol_recent.reset_index()
Ethambutol_recent_txcourse = Ethambutol_recent.loc[Ethambutol_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Ethambutol_minmax['Most recent Ethambutol course start date'] = Ethambutol_recent_txcourse['Date']
Ethambutol = Ethambutol.drop('Date of last Ethambutol Rx', axis=1)
Ethambutol['Date of first Ethambutol Rx'] = Ethambutol_minmax['Date of first Ethambutol Rx']
Ethambutol['Difference'] = ((Ethambutol['Date'] - Ethambutol['Date of first Ethambutol Rx']).dt.days)
Ethambutol['Multiple Ethambutol Tx Courses'] = Ethambutol_minmax['Multiple Ethambutol Tx courses']
Ethambutol = Ethambutol.loc[Ethambutol['Multiple Ethambutol Tx Courses'] == 'Multiple Courses']
Ethambutol = Ethambutol.drop('Multiple Ethambutol Tx Courses', axis=1)
Ethambutol_previous = Ethambutol.loc[Ethambutol['Difference'] <= 274]
Ethambutol_previous = Ethambutol_previous.reset_index()
Ethambutol_previous_tx =  Ethambutol_previous.loc[Ethambutol_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Ethambutol_minmax['Prior Ethambutol course end date'] = Ethambutol_previous_tx['Date']
Ethambutol_minmax_copy = Ethambutol_ori.join(Ethambutol_minmax)
def function_Ethambutol1(c):
    if c['Duration of Ethambutol Rx days'] >= 1460:
        if c['Date'] in (c['Prior Ethambutol course end date'], c['Most recent Ethambutol course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Ethambutol_minmax_copy['3rd course of Ethambutol?'] = Ethambutol_minmax_copy.apply(function_Ethambutol1, axis=1)
Ethambutol_minmax_copy = Ethambutol_minmax_copy['3rd course of Ethambutol?']
Ethambutol_minmax_copy = Ethambutol_minmax_copy.dropna().drop_duplicates()
Ethambutol_minmax = Ethambutol_minmax.join(Ethambutol_minmax_copy)
col = ['Date of first Ethambutol Rx', 'Prior Ethambutol course end date', 'Most recent Ethambutol course start date', 'Date of last Ethambutol Rx', 'Multiple Ethambutol Tx courses', '3rd course of Ethambutol?', 'Duration of Ethambutol Rx days', '# of Ethambutol Rx']
Ethambutol_minmax = Ethambutol_minmax[col]
Ethambutol_minmax

Clarithromycin = pd.DataFrame({'Index':clarithromycin_EMPI, 'Date':clarithromycin_date, 'Clarithromycin':clarithromycin})
Clarithromycin['Date'] = pd.to_datetime(Clarithromycin['Date'])
Clarithromycin_min = Clarithromycin.loc[Clarithromycin.groupby(['Index'])['Date'].idxmin()].set_index(['Index'])
Clarithromycin_max = Clarithromycin.loc[Clarithromycin.groupby(['Index'])['Date'].idxmax()].set_index(['Index'])
Clarithromycin_min = Clarithromycin_min.rename(columns={"Date": "Date of first Clarithromycin Rx"})
Clarithromycin_max = Clarithromycin_max.rename(columns={"Date": "Date of last Clarithromycin Rx"})
Clarithromycin_min['Date of last Clarithromycin Rx'] = Clarithromycin_max['Date of last Clarithromycin Rx']
Clarithromycin_minmax= Clarithromycin_min
Clarithromycin_minmax['Duration of Clarithromycin Rx days'] = (Clarithromycin_minmax['Date of last Clarithromycin Rx'] - Clarithromycin_minmax['Date of first Clarithromycin Rx']).dt.days
Clarithromycin_gb = Clarithromycin.groupby('Index')
Clarithromycin_counts = Clarithromycin_gb['Clarithromycin'].value_counts()
Clarithromycin_counts = pd.DataFrame(Clarithromycin_counts)
Clarithromycin_counts = Clarithromycin_counts.rename(columns={"Clarithromycin": "# of Clarithromycin Rx"})
Clarithromycin_counts = Clarithromycin_counts.reset_index()
Clarithromycin_counts = Clarithromycin_counts.set_index('Index')
Clarithromycin_minmax['# of Clarithromycin Rx'] = Clarithromycin_counts["# of Clarithromycin Rx"]
def function_clarithro(c):
    if c['Duration of Clarithromycin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Clarithromycin_minmax['Multiple Clarithromycin Tx courses'] = Clarithromycin_minmax.apply(function_clarithro, axis=1)
Clarithromycin = Clarithromycin.set_index('Index')
Clarithromycin = Clarithromycin.drop('Clarithromycin', axis=1)
Clarithromycin_ori = Clarithromycin
Clarithromycin = Clarithromycin.join(Clarithromycin_max, how='outer')
Clarithromycin['Difference'] = ((Clarithromycin['Date'] - Clarithromycin['Date of last Clarithromycin Rx']).dt.days).abs()
Clarithromycin_recent = Clarithromycin.loc[Clarithromycin['Difference'] <= 274]
Clarithromycin_recent = Clarithromycin_recent.reset_index()
Clarithromycin_recent_txcourse = Clarithromycin_recent.loc[Clarithromycin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Clarithromycin_minmax['Most recent Clarithromycin course start date'] = Clarithromycin_recent_txcourse['Date']
Clarithromycin = Clarithromycin.drop('Date of last Clarithromycin Rx', axis=1)
Clarithromycin['Date of first Clarithromycin Rx'] = Clarithromycin_minmax['Date of first Clarithromycin Rx']
Clarithromycin['Difference'] = ((Clarithromycin['Date'] - Clarithromycin['Date of first Clarithromycin Rx']).dt.days)
Clarithromycin['Multiple Clarithromycin Tx Courses'] = Clarithromycin_minmax['Multiple Clarithromycin Tx courses']
Clarithromycin = Clarithromycin.loc[Clarithromycin['Multiple Clarithromycin Tx Courses'] == 'Multiple Courses']
Clarithromycin = Clarithromycin.drop('Multiple Clarithromycin Tx Courses', axis=1)
Clarithromycin_previous = Clarithromycin.loc[Clarithromycin['Difference'] <= 274]
Clarithromycin_previous = Clarithromycin_previous.reset_index()
Clarithromycin_previous_tx =  Clarithromycin_previous.loc[Clarithromycin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Clarithromycin_minmax['Prior Clarithromycin course end date'] = Clarithromycin_previous_tx['Date']
Clarithromycin_minmax = Clarithromycin_minmax.drop('Clarithromycin', axis=1)
Clarithromycin_minmax_copy = Clarithromycin_ori.join(Clarithromycin_minmax)
def function_Clarithromycin1(c):
    if c['Duration of Clarithromycin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Clarithromycin course end date'], c['Most recent Clarithromycin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Clarithromycin_minmax_copy['3rd course of Clarithromycin?'] = Clarithromycin_minmax_copy.apply(function_Clarithromycin1, axis=1)
Clarithromycin_minmax_copy = Clarithromycin_minmax_copy['3rd course of Clarithromycin?']
Clarithromycin_minmax_copy = Clarithromycin_minmax_copy.dropna().drop_duplicates()
Clarithromycin_minmax = Clarithromycin_minmax.join(Clarithromycin_minmax_copy)
col = ['Date of first Clarithromycin Rx', 'Prior Clarithromycin course end date', 'Most recent Clarithromycin course start date', 'Date of last Clarithromycin Rx', 'Multiple Clarithromycin Tx courses', '3rd course of Clarithromycin?', 'Duration of Clarithromycin Rx days', '# of Clarithromycin Rx']
Clarithromycin_minmax = Clarithromycin_minmax[col]


Rifampicin = pd.DataFrame({'Index':rifampicin_EMPI, 'Date':rifampicin_date, 'Rifampicin':rifampicin})
Rifampicin['Date'] = pd.to_datetime(Rifampicin['Date'])
Rifampicin_gb = Rifampicin.groupby('Index')
Rifampicin_min = Rifampicin_gb.agg({'Date':np.min})
Rifampicin_max = Rifampicin_gb.agg({'Date':np.max})
Rifampicin_min = Rifampicin_min.rename(columns={"Date": "Date of first Rifampicin Rx"})
Rifampicin_max = Rifampicin_max.rename(columns={"Date": "Date of last Rifampicin Rx"})
Rifampicin_minmax = Rifampicin_min.join(Rifampicin_max, how='outer')
Rifampicin_minmax['Duration of Rifampicin Rx days'] = ((Rifampicin_minmax['Date of last Rifampicin Rx'] - Rifampicin_minmax['Date of first Rifampicin Rx']).dt.days).abs()
Rifampicin_counts = Rifampicin_gb['Rifampicin'].value_counts()
Rifampicin_counts = pd.DataFrame(Rifampicin_counts)
Rifampicin_counts = Rifampicin_counts.rename(columns={"Rifampicin": "# of Rifampicin Rx"})
Rifampicin_counts = Rifampicin_counts.reset_index()
Rifampicin_counts = Rifampicin_counts.set_index('Index')
Rifampicin_minmax['# of Rifampicin Rx'] = Rifampicin_counts["# of Rifampicin Rx"]
def function_Rifampicin(c):
    if c['Duration of Rifampicin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Rifampicin_minmax['Multiple Rifampicin Tx courses'] = Rifampicin_minmax.apply(function_Rifampicin, axis=1)
Rifampicin = Rifampicin.set_index('Index')
Rifampicin = Rifampicin.drop('Rifampicin', axis=1)
Rifampicin_ori = Rifampicin
Rifampicin = Rifampicin.join(Rifampicin_max, how='outer')
Rifampicin['Difference'] = ((Rifampicin['Date'] - Rifampicin['Date of last Rifampicin Rx']).dt.days).abs()
Rifampicin_recent = Rifampicin.loc[Rifampicin['Difference'] <= 274]
Rifampicin_recent = Rifampicin_recent.reset_index()
Rifampicin_recent_txcourse = Rifampicin_recent.loc[Rifampicin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Rifampicin_minmax['Most recent Rifampicin course start date'] = Rifampicin_recent_txcourse['Date']
Rifampicin = Rifampicin.drop('Date of last Rifampicin Rx', axis=1)
Rifampicin['Date of first Rifampicin Rx'] = Rifampicin_minmax['Date of first Rifampicin Rx']
Rifampicin['Difference'] = ((Rifampicin['Date'] - Rifampicin['Date of first Rifampicin Rx']).dt.days)
Rifampicin['Multiple Rifampicin Tx Courses'] = Rifampicin_minmax['Multiple Rifampicin Tx courses']
Rifampicin = Rifampicin.loc[Rifampicin['Multiple Rifampicin Tx Courses'] == 'Multiple Courses']
Rifampicin = Rifampicin.drop('Multiple Rifampicin Tx Courses', axis=1)
Rifampicin_previous = Rifampicin.loc[Rifampicin['Difference'] <= 274]
Rifampicin_previous = Rifampicin_previous.reset_index()
Rifampicin_previous_tx =  Rifampicin_previous.loc[Rifampicin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Rifampicin_minmax['Prior Rifampicin course end date'] = Rifampicin_previous_tx['Date']
Rifampicin_minmax_copy = Rifampicin_ori.join(Rifampicin_minmax)
def function_Rifampicin1(c):
    if c['Duration of Rifampicin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Rifampicin course end date'], c['Most recent Rifampicin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Rifampicin_minmax_copy['3rd course of Rifampicin?'] = Rifampicin_minmax_copy.apply(function_Rifampicin1, axis=1)
Rifampicin_minmax_copy = Rifampicin_minmax_copy['3rd course of Rifampicin?']
Rifampicin_minmax_copy = Rifampicin_minmax_copy.dropna().drop_duplicates()
Rifampicin_minmax = Rifampicin_minmax.join(Rifampicin_minmax_copy)
col = ['Date of first Rifampicin Rx', 'Prior Rifampicin course end date', 'Most recent Rifampicin course start date', 'Date of last Rifampicin Rx', 'Multiple Rifampicin Tx courses', '3rd course of Rifampicin?', 'Duration of Rifampicin Rx days', '# of Rifampicin Rx']
Rifampicin_minmax = Rifampicin_minmax[col]


# Rifabutin = pd.DataFrame({'Index':rifabutin_EMPI, 'Date':rifabutin_date, 'Rifabutin':rifabutin})
# Rifabutin['Date'] = pd.to_datetime(Rifabutin['Date'])
# Rifabutin_gb = Rifabutin.groupby('Index')
# Rifabutin_min = Rifabutin_gb.agg({'Date':np.min})
# Rifabutin_max = Rifabutin_gb.agg({'Date':np.max})
# Rifabutin_min = Rifabutin_min.rename(columns={"Date": "Date of first Rifabutin Rx"})
# Rifabutin_max = Rifabutin_max.rename(columns={"Date": "Date of last Rifabutin Rx"})
# Rifabutin_minmax = Rifabutin_min.join(Rifabutin_max, how='outer')
# Rifabutin_minmax['Duration of Rifabutin Rx days'] = ((Rifabutin_minmax['Date of last Rifabutin Rx'] - Rifabutin_minmax['Date of first Rifabutin Rx']).dt.days).abs()
# Rifabutin_counts = Rifabutin_gb['Rifabutin'].value_counts()
# Rifabutin_counts = pd.DataFrame(Rifabutin_counts)
# Rifabutin_counts = Rifabutin_counts.rename(columns={"Rifabutin": "# of Rifabutin Rx"})
# Rifabutin_counts = Rifabutin_counts.reset_index()
# Rifabutin_counts = Rifabutin_counts.set_index('Index')
# Rifabutin_minmax['# of Rifabutin Rx'] = Rifabutin_counts["# of Rifabutin Rx"]
# def function_Rifabutin(c):
#     if c['Duration of Rifabutin Rx days'] >= 274:
#         return 'Multiple Courses'
#     else:
#         return np.nan
# Rifabutin_minmax['Multiple Rifabutin Tx courses'] = Rifabutin_minmax.apply(function_Rifabutin, axis=1)
# Rifabutin = Rifabutin.set_index('Index')
# Rifabutin = Rifabutin.drop('Rifabutin', axis=1)
# Rifabutin_ori = Rifabutin
# Rifabutin = Rifabutin.join(Rifabutin_max, how='outer')
# Rifabutin['Difference'] = ((Rifabutin['Date'] - Rifabutin['Date of last Rifabutin Rx']).dt.days).abs()
# Rifabutin_recent = Rifabutin.loc[Rifabutin['Difference'] <= 274]
# Rifabutin_recent = Rifabutin_recent.reset_index()
# Rifabutin_recent_txcourse = Rifabutin_recent.loc[Rifabutin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
# Rifabutin_minmax['Most recent Rifabutin course start date'] = Rifabutin_recent_txcourse['Date']
# Rifabutin = Rifabutin.drop('Date of last Rifabutin Rx', axis=1)
# Rifabutin['Date of first Rifabutin Rx'] = Rifabutin_minmax['Date of first Rifabutin Rx']
# Rifabutin['Difference'] = ((Rifabutin['Date'] - Rifabutin['Date of first Rifabutin Rx']).dt.days)
# Rifabutin['Multiple Rifabutin Tx Courses'] = Rifabutin_minmax['Multiple Rifabutin Tx courses']
# Rifabutin = Rifabutin.loc[Rifabutin['Multiple Rifabutin Tx Courses'] == 'Multiple Courses']
# Rifabutin = Rifabutin.drop('Multiple Rifabutin Tx Courses', axis=1)
# Rifabutin_previous = Rifabutin.loc[Rifabutin['Difference'] <= 274]
# Rifabutin_previous = Rifabutin_previous.reset_index()
# Rifabutin_previous_tx =  Rifabutin_previous.loc[Rifabutin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
# Rifabutin_minmax['Prior Rifabutin course end date'] = Rifabutin_previous_tx['Date']
# Rifabutin_minmax_copy = Rifabutin_ori.join(Rifabutin_minmax)
# def function_Rifabutin1(c):
#     if c['Duration of Rifabutin Rx days'] >= 1460:
#         if c['Date'] in (c['Prior Rifabutin course end date'], c['Most recent Rifabutin course start date']):
#             return '3rd course recieved'
#         else:
#             return np.nan
# Rifabutin_minmax_copy['3rd course of Rifabutin?'] = Rifabutin_minmax_copy.apply(function_Rifabutin1, axis=1)
# Rifabutin_minmax_copy = Rifabutin_minmax_copy['3rd course of Rifabutin?']
# Rifabutin_minmax_copy = Rifabutin_minmax_copy.dropna().drop_duplicates()
# Rifabutin_minmax = Rifabutin_minmax.join(Rifabutin_minmax_copy)
# col = ['Date of first Rifabutin Rx', 'Prior Rifabutin course end date', 'Most recent Rifabutin course start date', 'Date of last Rifabutin Rx', 'Multiple Rifabutin Tx courses', '3rd course of Rifabutin?', 'Duration of Rifabutin Rx days', '# of Rifabutin Rx']
# Rifabutin_minmax = Rifabutin_minmax[col]

Bedaqualine = pd.DataFrame({'Index':bedaquiline_EMPI, 'Date':bedaquiline_date, 'Bedaqualine':bedaquiline})
Bedaqualine['Date'] = pd.to_datetime(Bedaqualine['Date'])
Bedaqualine_gb = Bedaqualine.groupby('Index')
Bedaqualine_min = Bedaqualine_gb.agg({'Date':np.min})
Bedaqualine_max = Bedaqualine_gb.agg({'Date':np.max})
Bedaqualine_min = Bedaqualine_min.rename(columns={"Date": "Date of first Bedaqualine Rx"})
Bedaqualine_max = Bedaqualine_max.rename(columns={"Date": "Date of last Bedaqualine Rx"})
Bedaqualine_minmax = Bedaqualine_min.join(Bedaqualine_max, how='outer')
Bedaqualine_minmax['Duration of Bedaqualine Rx days'] = ((Bedaqualine_minmax['Date of last Bedaqualine Rx'] - Bedaqualine_minmax['Date of first Bedaqualine Rx']).dt.days).abs()
Bedaqualine_counts = Bedaqualine_gb['Bedaqualine'].value_counts()
Bedaqualine_counts = pd.DataFrame(Bedaqualine_counts)
Bedaqualine_counts = Bedaqualine_counts.rename(columns={"Bedaqualine": "# of Bedaqualine Rx"})
Bedaqualine_counts = Bedaqualine_counts.reset_index()
Bedaqualine_counts = Bedaqualine_counts.set_index('Index')
Bedaqualine_minmax['# of Bedaqualine Rx'] = Bedaqualine_counts["# of Bedaqualine Rx"]
def function_Bedaqualine(c):
    if c['Duration of Bedaqualine Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Bedaqualine_minmax['Multiple Bedaqualine Tx courses'] = Bedaqualine_minmax.apply(function_Bedaqualine, axis=1)
Bedaqualine = Bedaqualine.set_index('Index')
Bedaqualine = Bedaqualine.drop('Bedaqualine', axis=1)
Bedaqualine_ori = Bedaqualine
Bedaqualine = Bedaqualine.join(Bedaqualine_max, how='outer')
Bedaqualine['Difference'] = ((Bedaqualine['Date'] - Bedaqualine['Date of last Bedaqualine Rx']).dt.days).abs()
Bedaqualine_recent = Bedaqualine.loc[Bedaqualine['Difference'] <= 274]
Bedaqualine_recent = Bedaqualine_recent.reset_index()
Bedaqualine_recent_txcourse = Bedaqualine_recent.loc[Bedaqualine_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Bedaqualine_minmax['Most recent Bedaqualine course start date'] = Bedaqualine_recent_txcourse['Date']
col = ['Date of first Bedaqualine Rx', 'Date of last Bedaqualine Rx', 'Multiple Bedaqualine Tx courses', 'Duration of Bedaqualine Rx days', '# of Bedaqualine Rx']
Bedaqualine_minmax = Bedaqualine_minmax[col]

Isoniazid = pd.DataFrame({'Index':isoniazid_EMPI, 'Date':isoniazid_date, 'Isoniazid':isoniazid})
Isoniazid['Date'] = pd.to_datetime(Isoniazid['Date'])
Isoniazid_gb = Isoniazid.groupby('Index')
Isoniazid_min = Isoniazid_gb.agg({'Date':np.min})
Isoniazid_max = Isoniazid_gb.agg({'Date':np.max})
Isoniazid_min = Isoniazid_min.rename(columns={"Date": "Date of first Isoniazid Rx"})
Isoniazid_max = Isoniazid_max.rename(columns={"Date": "Date of last Isoniazid Rx"})
Isoniazid_minmax = Isoniazid_min.join(Isoniazid_max, how='outer')
Isoniazid_minmax['Duration of Isoniazid Rx days'] = ((Isoniazid_minmax['Date of last Isoniazid Rx'] - Isoniazid_minmax['Date of first Isoniazid Rx']).dt.days).abs()
Isoniazid_counts = Isoniazid_gb['Isoniazid'].value_counts()
Isoniazid_counts = pd.DataFrame(Isoniazid_counts)
Isoniazid_counts = Isoniazid_counts.rename(columns={"Isoniazid": "# of Isoniazid Rx"})
Isoniazid_counts = Isoniazid_counts.reset_index()
Isoniazid_counts = Isoniazid_counts.set_index('Index')
Isoniazid_minmax['# of Isoniazid Rx'] = Isoniazid_counts["# of Isoniazid Rx"]
def function_Isoniazid(c):
    if c['Duration of Isoniazid Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Isoniazid_minmax['Multiple Isoniazid Tx courses'] = Isoniazid_minmax.apply(function_Isoniazid, axis=1)
Isoniazid = Isoniazid.set_index('Index')
Isoniazid = Isoniazid.drop('Isoniazid', axis=1)
Isoniazid_ori = Isoniazid
Isoniazid = Isoniazid.join(Isoniazid_max, how='outer')
Isoniazid['Difference'] = ((Isoniazid['Date'] - Isoniazid['Date of last Isoniazid Rx']).dt.days).abs()
Isoniazid_recent = Isoniazid.loc[Isoniazid['Difference'] <= 274]
Isoniazid_recent = Isoniazid_recent.reset_index()
Isoniazid_recent_txcourse = Isoniazid_recent.loc[Isoniazid_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Isoniazid_minmax['Most recent Isoniazid course start date'] = Isoniazid_recent_txcourse['Date']
Isoniazid = Isoniazid.drop('Date of last Isoniazid Rx', axis=1)
Isoniazid['Date of first Isoniazid Rx'] = Isoniazid_minmax['Date of first Isoniazid Rx']
Isoniazid['Difference'] = ((Isoniazid['Date'] - Isoniazid['Date of first Isoniazid Rx']).dt.days)
Isoniazid['Multiple Isoniazid Tx Courses'] = Isoniazid_minmax['Multiple Isoniazid Tx courses']
Isoniazid = Isoniazid.loc[Isoniazid['Multiple Isoniazid Tx Courses'] == 'Multiple Courses']
Isoniazid = Isoniazid.drop('Multiple Isoniazid Tx Courses', axis=1)
Isoniazid_previous = Isoniazid.loc[Isoniazid['Difference'] <= 274]
Isoniazid_previous = Isoniazid_previous.reset_index()
Isoniazid_previous_tx =  Isoniazid_previous.loc[Isoniazid_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Isoniazid_minmax['Prior Isoniazid course end date'] = Isoniazid_previous_tx['Date']
Isoniazid_minmax_copy = Isoniazid_ori.join(Isoniazid_minmax)
def function_Isoniazid1(c):
    if c['Duration of Isoniazid Rx days'] >= 1460:
        if c['Date'] in (c['Prior Isoniazid course end date'], c['Most recent Isoniazid course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Isoniazid_minmax_copy['3rd course of Isoniazid?'] = Isoniazid_minmax_copy.apply(function_Isoniazid1, axis=1)
Isoniazid_minmax_copy = Isoniazid_minmax_copy['3rd course of Isoniazid?']
Isoniazid_minmax_copy = Isoniazid_minmax_copy.dropna().drop_duplicates()
Isoniazid_minmax = Isoniazid_minmax.join(Isoniazid_minmax_copy)
col = ['Date of first Isoniazid Rx', 'Prior Isoniazid course end date', 'Most recent Isoniazid course start date', 'Date of last Isoniazid Rx', 'Multiple Isoniazid Tx courses', '3rd course of Isoniazid?', 'Duration of Isoniazid Rx days', '# of Isoniazid Rx']
Isoniazid_minmax = Isoniazid_minmax[col]

Clofazimine = pd.DataFrame({'Index':clofazimine_EMPI, 'Date':clofazimine_date, 'Clofazimine':clofazimine})
Clofazimine['Date'] = pd.to_datetime(Clofazimine['Date'])
Clofazimine_gb = Clofazimine.groupby('Index')
Clofazimine_min = Clofazimine_gb.agg({'Date':np.min})
Clofazimine_max = Clofazimine_gb.agg({'Date':np.max})
Clofazimine_min = Clofazimine_min.rename(columns={"Date": "Date of first Clofazimine Rx"})
Clofazimine_max = Clofazimine_max.rename(columns={"Date": "Date of last Clofazimine Rx"})
Clofazimine_minmax = Clofazimine_min.join(Clofazimine_max, how='outer')
Clofazimine_minmax['Duration of Clofazimine Rx days'] = ((Clofazimine_minmax['Date of last Clofazimine Rx'] - Clofazimine_minmax['Date of first Clofazimine Rx']).dt.days).abs()
Clofazimine_counts = Clofazimine_gb['Clofazimine'].value_counts()
Clofazimine_counts = pd.DataFrame(Clofazimine_counts)
Clofazimine_counts = Clofazimine_counts.rename(columns={"Clofazimine": "# of Clofazimine Rx"})
Clofazimine_counts = Clofazimine_counts.reset_index()
Clofazimine_counts = Clofazimine_counts.set_index('Index')
Clofazimine_minmax['# of Clofazimine Rx'] = Clofazimine_counts["# of Clofazimine Rx"]
def function_Clofazimine(c):
    if c['Duration of Clofazimine Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Clofazimine_minmax['Multiple Clofazimine Tx courses'] = Clofazimine_minmax.apply(function_Clofazimine, axis=1)
Clofazimine = Clofazimine.set_index('Index')
Clofazimine = Clofazimine.drop('Clofazimine', axis=1)
Clofazimine_ori = Clofazimine
Clofazimine = Clofazimine.join(Clofazimine_max, how='outer')
Clofazimine['Difference'] = ((Clofazimine['Date'] - Clofazimine['Date of last Clofazimine Rx']).dt.days).abs()
Clofazimine_recent = Clofazimine.loc[Clofazimine['Difference'] <= 274]
Clofazimine_recent = Clofazimine_recent.reset_index()
Clofazimine_recent_txcourse = Clofazimine_recent.loc[Clofazimine_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Clofazimine_minmax['Most recent Clofazimine course start date'] = Clofazimine_recent_txcourse['Date']

col = ['Date of first Clofazimine Rx', 'Date of last Clofazimine Rx', 'Multiple Clofazimine Tx courses', 'Duration of Clofazimine Rx days', '# of Clofazimine Rx']
Clofazimine_minmax = Clofazimine_minmax[col]

Amikacin = pd.DataFrame({'Index':amikacin_EMPI, 'Date':amikacin_date, 'Amikacin':amikacin})
Amikacin['Date'] = pd.to_datetime(Amikacin['Date'])
Amikacin_gb = Amikacin.groupby('Index')
Amikacin_min = Amikacin_gb.agg({'Date':np.min})
Amikacin_max = Amikacin_gb.agg({'Date':np.max})
Amikacin_min = Amikacin_min.rename(columns={"Date": "Date of first Amikacin Rx"})
Amikacin_max = Amikacin_max.rename(columns={"Date": "Date of last Amikacin Rx"})
Amikacin_minmax = Amikacin_min.join(Amikacin_max, how='outer')
Amikacin_minmax['Duration of Amikacin Rx days'] = ((Amikacin_minmax['Date of last Amikacin Rx'] - Amikacin_minmax['Date of first Amikacin Rx']).dt.days).abs()
Amikacin_counts = Amikacin_gb['Amikacin'].value_counts()
Amikacin_counts = pd.DataFrame(Amikacin_counts)
Amikacin_counts = Amikacin_counts.rename(columns={"Amikacin": "# of Amikacin Rx"})
Amikacin_counts = Amikacin_counts.reset_index()
Amikacin_counts = Amikacin_counts.set_index('Index')
Amikacin_minmax['# of Amikacin Rx'] = Amikacin_counts["# of Amikacin Rx"]
def function_Amikacin(c):
    if c['Duration of Amikacin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Amikacin_minmax['Multiple Amikacin Tx courses'] = Amikacin_minmax.apply(function_Amikacin, axis=1)
Amikacin = Amikacin.set_index('Index')
Amikacin = Amikacin.drop('Amikacin', axis=1)
Amikacin_ori = Amikacin
Amikacin = Amikacin.join(Amikacin_max, how='outer')
Amikacin['Difference'] = ((Amikacin['Date'] - Amikacin['Date of last Amikacin Rx']).dt.days).abs()
Amikacin_recent = Amikacin.loc[Amikacin['Difference'] <= 274]
Amikacin_recent = Amikacin_recent.reset_index()
Amikacin_recent_txcourse = Amikacin_recent.loc[Amikacin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Amikacin_minmax['Most recent Amikacin course start date'] = Amikacin_recent_txcourse['Date']
Amikacin = Amikacin.drop('Date of last Amikacin Rx', axis=1)
Amikacin['Date of first Amikacin Rx'] = Amikacin_minmax['Date of first Amikacin Rx']
Amikacin['Difference'] = ((Amikacin['Date'] - Amikacin['Date of first Amikacin Rx']).dt.days)
Amikacin['Multiple Amikacin Tx Courses'] = Amikacin_minmax['Multiple Amikacin Tx courses']
Amikacin = Amikacin.loc[Amikacin['Multiple Amikacin Tx Courses'] == 'Multiple Courses']
Amikacin = Amikacin.drop('Multiple Amikacin Tx Courses', axis=1)
Amikacin_previous = Amikacin.loc[Amikacin['Difference'] <= 274]
Amikacin_previous = Amikacin_previous.reset_index()
Amikacin_previous_tx =  Amikacin_previous.loc[Amikacin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Amikacin_minmax['Prior Amikacin course end date'] = Amikacin_previous_tx['Date']
Amikacin_minmax_copy = Amikacin_ori.join(Amikacin_minmax)
def function_Amikacin1(c):
    if c['Duration of Amikacin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Amikacin course end date'], c['Most recent Amikacin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Amikacin_minmax_copy['3rd course of Amikacin?'] = Amikacin_minmax_copy.apply(function_Amikacin1, axis=1)
Amikacin_minmax_copy = Amikacin_minmax_copy['3rd course of Amikacin?']
Amikacin_minmax_copy = Amikacin_minmax_copy.dropna().drop_duplicates()
Amikacin_minmax = Amikacin_minmax.join(Amikacin_minmax_copy)
col = ['Date of first Amikacin Rx', 'Prior Amikacin course end date', 'Most recent Amikacin course start date', 'Date of last Amikacin Rx', 'Multiple Amikacin Tx courses', '3rd course of Amikacin?', 'Duration of Amikacin Rx days', '# of Amikacin Rx']
Amikacin_minmax = Amikacin_minmax[col]

Azithromycin = pd.DataFrame({'Index':azithromycin_EMPI, 'Date':azithromycin_date, 'Azithromycin':azithromycin})
Azithromycin['Date'] = pd.to_datetime(Azithromycin['Date'])
Azithromycin_gb = Azithromycin.groupby('Index')
Azithromycin_min = Azithromycin_gb.agg({'Date':np.min})
Azithromycin_max = Azithromycin_gb.agg({'Date':np.max})
Azithromycin_min = Azithromycin_min.rename(columns={"Date": "Date of first Azithromycin Rx"})
Azithromycin_max = Azithromycin_max.rename(columns={"Date": "Date of last Azithromycin Rx"})
Azithromycin_minmax = Azithromycin_min.join(Azithromycin_max, how='outer')
Azithromycin_minmax['Duration of Azithromycin Rx days'] = ((Azithromycin_minmax['Date of last Azithromycin Rx'] - Azithromycin_minmax['Date of first Azithromycin Rx']).dt.days).abs()
Azithromycin_counts = Azithromycin_gb['Azithromycin'].value_counts()
Azithromycin_counts = pd.DataFrame(Azithromycin_counts)
Azithromycin_counts = Azithromycin_counts.rename(columns={"Azithromycin": "# of Azithromycin Rx"})
Azithromycin_counts = Azithromycin_counts.reset_index()
Azithromycin_counts = Azithromycin_counts.set_index('Index')
Azithromycin_minmax['# of Azithromycin Rx'] = Azithromycin_counts["# of Azithromycin Rx"]
def function_Azithromycin(c):
  if c['Duration of Azithromycin Rx days'] >= 274:
      return 'Multiple Courses'
  else:
      return np.nan
Azithromycin_minmax['Multiple Azithromycin Tx courses'] = Azithromycin_minmax.apply(function_Azithromycin, axis=1)
Azithromycin = Azithromycin.set_index('Index')
Azithromycin = Azithromycin.drop('Azithromycin', axis=1)
Azithromycin_ori = Azithromycin
Azithromycin = Azithromycin.join(Azithromycin_max, how='outer')
Azithromycin['Difference'] = ((Azithromycin['Date'] - Azithromycin['Date of last Azithromycin Rx']).dt.days).abs()
Azithromycin_recent = Azithromycin.loc[Azithromycin['Difference'] <= 274]
Azithromycin_recent = Azithromycin_recent.reset_index()
Azithromycin_recent_txcourse = Azithromycin_recent.loc[Azithromycin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Azithromycin_minmax['Most recent Azithromycin course start date'] = Azithromycin_recent_txcourse['Date']
Azithromycin = Azithromycin.drop('Date of last Azithromycin Rx', axis=1)
Azithromycin['Date of first Azithromycin Rx'] = Azithromycin_minmax['Date of first Azithromycin Rx']
Azithromycin['Difference'] = ((Azithromycin['Date'] - Azithromycin['Date of first Azithromycin Rx']).dt.days)
Azithromycin['Multiple Azithromycin Tx Courses'] = Azithromycin_minmax['Multiple Azithromycin Tx courses']
Azithromycin = Azithromycin.loc[Azithromycin['Multiple Azithromycin Tx Courses'] == 'Multiple Courses']
Azithromycin = Azithromycin.drop('Multiple Azithromycin Tx Courses', axis=1)
Azithromycin_previous = Azithromycin.loc[Azithromycin['Difference'] <= 274]
Azithromycin_previous = Azithromycin_previous.reset_index()
Azithromycin_previous_tx =  Azithromycin_previous.loc[Azithromycin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Azithromycin_minmax['Prior Azithromycin course end date'] = Azithromycin_previous_tx['Date']
Azithromycin_minmax_copy = Azithromycin_ori.join(Azithromycin_minmax)
def function_Azithromycin1(c):
  if c['Duration of Azithromycin Rx days'] >= 1460:
      if c['Date'] in (c['Prior Azithromycin course end date'], c['Most recent Azithromycin course start date']):
          return '3rd course recieved'
      else:
          return np.nan
Azithromycin_minmax_copy['3rd course of Azithromycin?'] = Azithromycin_minmax_copy.apply(function_Azithromycin1, axis=1)
Azithromycin_minmax_copy = Azithromycin_minmax_copy['3rd course of Azithromycin?']
Azithromycin_minmax_copy = Azithromycin_minmax_copy.dropna().drop_duplicates()
Azithromycin_minmax = Azithromycin_minmax.join(Azithromycin_minmax_copy)
col = ['Date of first Azithromycin Rx', 'Prior Azithromycin course end date', 'Most recent Azithromycin course start date', 'Date of last Azithromycin Rx', 'Multiple Azithromycin Tx courses', '3rd course of Azithromycin?', 'Duration of Azithromycin Rx days', '# of Azithromycin Rx']
Azithromycin_minmax = Azithromycin_minmax[col]


Moxifloxacin = pd.DataFrame({'Index':moxifloxacin_EMPI, 'Date':moxifloxacin_date, 'Moxifloxacin':moxifloxacin})
Moxifloxacin['Date'] = pd.to_datetime(Moxifloxacin['Date'])
Moxifloxacin_gb = Moxifloxacin.groupby('Index')
Moxifloxacin_min = Moxifloxacin_gb.agg({'Date':np.min})
Moxifloxacin_max = Moxifloxacin_gb.agg({'Date':np.max})
Moxifloxacin_min = Moxifloxacin_min.rename(columns={"Date": "Date of first Moxifloxacin Rx"})
Moxifloxacin_max = Moxifloxacin_max.rename(columns={"Date": "Date of last Moxifloxacin Rx"})
Moxifloxacin_minmax = Moxifloxacin_min.join(Moxifloxacin_max, how='outer')
Moxifloxacin_minmax['Duration of Moxifloxacin Rx days'] = ((Moxifloxacin_minmax['Date of last Moxifloxacin Rx'] - Moxifloxacin_minmax['Date of first Moxifloxacin Rx']).dt.days).abs()
Moxifloxacin_minmax
Moxifloxacin_counts = Moxifloxacin_gb['Moxifloxacin'].value_counts()
Moxifloxacin_counts = pd.DataFrame(Moxifloxacin_counts)
Moxifloxacin_counts = Moxifloxacin_counts.rename(columns={"Moxifloxacin": "# of Moxifloxacin Rx"})
Moxifloxacin_counts = Moxifloxacin_counts.reset_index()
Moxifloxacin_counts = Moxifloxacin_counts.set_index('Index')
Moxifloxacin_minmax['# of Moxifloxacin Rx'] = Moxifloxacin_counts["# of Moxifloxacin Rx"]
def function_Moxifloxacin(c):
    if c['Duration of Moxifloxacin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Moxifloxacin_minmax['Multiple Moxifloxacin Tx courses'] = Moxifloxacin_minmax.apply(function_Moxifloxacin, axis=1)
Moxifloxacin = Moxifloxacin.set_index('Index')
Moxifloxacin = Moxifloxacin.drop('Moxifloxacin', axis=1)
Moxifloxacin_ori = Moxifloxacin
Moxifloxacin = Moxifloxacin.join(Moxifloxacin_max, how='outer')
Moxifloxacin['Difference'] = ((Moxifloxacin['Date'] - Moxifloxacin['Date of last Moxifloxacin Rx']).dt.days).abs()
Moxifloxacin_recent = Moxifloxacin.loc[Moxifloxacin['Difference'] <= 274]
Moxifloxacin_recent = Moxifloxacin_recent.reset_index()
Moxifloxacin_recent_txcourse = Moxifloxacin_recent.loc[Moxifloxacin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Moxifloxacin_minmax['Most recent Moxifloxacin course start date'] = Moxifloxacin_recent_txcourse['Date']
Moxifloxacin = Moxifloxacin.drop('Date of last Moxifloxacin Rx', axis=1)
Moxifloxacin['Date of first Moxifloxacin Rx'] = Moxifloxacin_minmax['Date of first Moxifloxacin Rx']
Moxifloxacin['Difference'] = ((Moxifloxacin['Date'] - Moxifloxacin['Date of first Moxifloxacin Rx']).dt.days)
Moxifloxacin['Multiple Moxifloxacin Tx Courses'] = Moxifloxacin_minmax['Multiple Moxifloxacin Tx courses']
Moxifloxacin = Moxifloxacin.loc[Moxifloxacin['Multiple Moxifloxacin Tx Courses'] == 'Multiple Courses']
Moxifloxacin = Moxifloxacin.drop('Multiple Moxifloxacin Tx Courses', axis=1)
Moxifloxacin_previous = Moxifloxacin.loc[Moxifloxacin['Difference'] <= 274]
Moxifloxacin_previous = Moxifloxacin_previous.reset_index()
Moxifloxacin_previous_tx =  Moxifloxacin_previous.loc[Moxifloxacin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Moxifloxacin_minmax['Prior Moxifloxacin course end date'] = Moxifloxacin_previous_tx['Date']
Moxifloxacin_minmax_copy = Moxifloxacin_ori.join(Moxifloxacin_minmax)
def function_Moxifloxacin1(c):
    if c['Duration of Moxifloxacin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Moxifloxacin course end date'], c['Most recent Moxifloxacin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Moxifloxacin_minmax_copy['3rd course of Moxifloxacin?'] = Moxifloxacin_minmax_copy.apply(function_Moxifloxacin1, axis=1)
Moxifloxacin_minmax_copy = Moxifloxacin_minmax_copy['3rd course of Moxifloxacin?']
Moxifloxacin_minmax_copy = Moxifloxacin_minmax_copy.dropna().drop_duplicates()
Moxifloxacin_minmax = Moxifloxacin_minmax.join(Moxifloxacin_minmax_copy)
col = ['Date of first Moxifloxacin Rx', 'Prior Moxifloxacin course end date', 'Most recent Moxifloxacin course start date', 'Date of last Moxifloxacin Rx', 'Multiple Moxifloxacin Tx courses', '3rd course of Moxifloxacin?', 'Duration of Moxifloxacin Rx days', '# of Moxifloxacin Rx']
Moxifloxacin_minmax = Moxifloxacin_minmax[col]


Levofloxacin = pd.DataFrame({'Index':levofloxacin_EMPI, 'Date':levofloxacin_date, 'Levofloxacin':levofloxacin})
Levofloxacin['Date'] = pd.to_datetime(Levofloxacin['Date'])
Levofloxacin_gb = Levofloxacin.groupby('Index')
Levofloxacin_min = Levofloxacin_gb.agg({'Date':np.min})
Levofloxacin_max = Levofloxacin_gb.agg({'Date':np.max})
Levofloxacin_min = Levofloxacin_min.rename(columns={"Date": "Date of first Levofloxacin Rx"})
Levofloxacin_max = Levofloxacin_max.rename(columns={"Date": "Date of last Levofloxacin Rx"})
Levofloxacin_minmax = Levofloxacin_min.join(Levofloxacin_max, how='outer')
Levofloxacin_minmax['Duration of Levofloxacin Rx days'] = ((Levofloxacin_minmax['Date of last Levofloxacin Rx'] - Levofloxacin_minmax['Date of first Levofloxacin Rx']).dt.days).abs()
Levofloxacin_counts = Levofloxacin_gb['Levofloxacin'].value_counts()
Levofloxacin_counts = pd.DataFrame(Levofloxacin_counts)
Levofloxacin_counts = Levofloxacin_counts.rename(columns={"Levofloxacin": "# of Levofloxacin Rx"})
Levofloxacin_counts = Levofloxacin_counts.reset_index()
Levofloxacin_counts = Levofloxacin_counts.set_index('Index')
Levofloxacin_minmax['# of Levofloxacin Rx'] = Levofloxacin_counts["# of Levofloxacin Rx"]
def function_Levofloxacin(c):
    if c['Duration of Levofloxacin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Levofloxacin_minmax['Multiple Levofloxacin Tx courses'] = Levofloxacin_minmax.apply(function_Levofloxacin, axis=1)
Levofloxacin = Levofloxacin.set_index('Index')
Levofloxacin = Levofloxacin.drop('Levofloxacin', axis=1)
Levofloxacin_ori = Levofloxacin
Levofloxacin = Levofloxacin.join(Levofloxacin_max, how='outer')
Levofloxacin['Difference'] = ((Levofloxacin['Date'] - Levofloxacin['Date of last Levofloxacin Rx']).dt.days).abs()
Levofloxacin_recent = Levofloxacin.loc[Levofloxacin['Difference'] <= 274]
Levofloxacin_recent = Levofloxacin_recent.reset_index()
Levofloxacin_recent_txcourse = Levofloxacin_recent.loc[Levofloxacin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Levofloxacin_minmax['Most recent Levofloxacin course start date'] = Levofloxacin_recent_txcourse['Date']
Levofloxacin = Levofloxacin.drop('Date of last Levofloxacin Rx', axis=1)
Levofloxacin['Date of first Levofloxacin Rx'] = Levofloxacin_minmax['Date of first Levofloxacin Rx']
Levofloxacin['Difference'] = ((Levofloxacin['Date'] - Levofloxacin['Date of first Levofloxacin Rx']).dt.days)
Levofloxacin['Multiple Levofloxacin Tx Courses'] = Levofloxacin_minmax['Multiple Levofloxacin Tx courses']
Levofloxacin = Levofloxacin.loc[Levofloxacin['Multiple Levofloxacin Tx Courses'] == 'Multiple Courses']
Levofloxacin = Levofloxacin.drop('Multiple Levofloxacin Tx Courses', axis=1)
Levofloxacin_previous = Levofloxacin.loc[Levofloxacin['Difference'] <= 274]
Levofloxacin_previous = Levofloxacin_previous.reset_index()
Levofloxacin_previous_tx =  Levofloxacin_previous.loc[Levofloxacin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Levofloxacin_minmax['Prior Levofloxacin course end date'] = Levofloxacin_previous_tx['Date']
Levofloxacin_minmax_copy = Levofloxacin_ori.join(Levofloxacin_minmax)
def function_Levofloxacin1(c):
    if c['Duration of Levofloxacin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Levofloxacin course end date'], c['Most recent Levofloxacin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Levofloxacin_minmax_copy['3rd course of Levofloxacin?'] = Levofloxacin_minmax_copy.apply(function_Levofloxacin1, axis=1)
Levofloxacin_minmax_copy = Levofloxacin_minmax_copy['3rd course of Levofloxacin?']
Levofloxacin_minmax_copy = Levofloxacin_minmax_copy.dropna().drop_duplicates()
Levofloxacin_minmax = Levofloxacin_minmax.join(Levofloxacin_minmax_copy)
col = ['Date of first Levofloxacin Rx', 'Prior Levofloxacin course end date', 'Most recent Levofloxacin course start date', 'Date of last Levofloxacin Rx', 'Multiple Levofloxacin Tx courses', '3rd course of Levofloxacin?', 'Duration of Levofloxacin Rx days', '# of Levofloxacin Rx']
Levofloxacin_minmax = Levofloxacin_minmax[col]



Tobramycin = pd.DataFrame({'Index':tobramycin_EMPI, 'Date':tobramycin_date, 'Tobramycin':tobramycin})
Tobramycin['Date'] = pd.to_datetime(Tobramycin['Date'])
Tobramycin_gb = Tobramycin.groupby('Index')
Tobramycin_min = Tobramycin_gb.agg({'Date':np.min})
Tobramycin_max = Tobramycin_gb.agg({'Date':np.max})
Tobramycin_min = Tobramycin_min.rename(columns={"Date": "Date of first Tobramycin Rx"})
Tobramycin_max = Tobramycin_max.rename(columns={"Date": "Date of last Tobramycin Rx"})
Tobramycin_minmax = Tobramycin_min.join(Tobramycin_max, how='outer')
Tobramycin_minmax['Duration of Tobramycin Rx days'] = ((Tobramycin_minmax['Date of last Tobramycin Rx'] - Tobramycin_minmax['Date of first Tobramycin Rx']).dt.days).abs()
Tobramycin_counts = Tobramycin_gb['Tobramycin'].value_counts()
Tobramycin_counts = pd.DataFrame(Tobramycin_counts)
Tobramycin_counts = Tobramycin_counts.rename(columns={"Tobramycin": "# of Tobramycin Rx"})
Tobramycin_counts = Tobramycin_counts.reset_index()
Tobramycin_counts = Tobramycin_counts.set_index('Index')
Tobramycin_minmax['# of Tobramycin Rx'] = Tobramycin_counts["# of Tobramycin Rx"]
def function_Tobramycin(c):
    if c['Duration of Tobramycin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Tobramycin_minmax['Multiple Tobramycin Tx courses'] = Tobramycin_minmax.apply(function_Tobramycin, axis=1)
Tobramycin = Tobramycin.set_index('Index')
Tobramycin = Tobramycin.drop('Tobramycin', axis=1)
Tobramycin_ori = Tobramycin
Tobramycin = Tobramycin.join(Tobramycin_max, how='outer')
Tobramycin['Difference'] = ((Tobramycin['Date'] - Tobramycin['Date of last Tobramycin Rx']).dt.days).abs()
Tobramycin_recent = Tobramycin.loc[Tobramycin['Difference'] <= 274]
Tobramycin_recent = Tobramycin_recent.reset_index()
Tobramycin_recent_txcourse = Tobramycin_recent.loc[Tobramycin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Tobramycin_minmax['Most recent Tobramycin course start date'] = Tobramycin_recent_txcourse['Date']
Tobramycin = Tobramycin.drop('Date of last Tobramycin Rx', axis=1)
Tobramycin['Date of first Tobramycin Rx'] = Tobramycin_minmax['Date of first Tobramycin Rx']
Tobramycin['Difference'] = ((Tobramycin['Date'] - Tobramycin['Date of first Tobramycin Rx']).dt.days)
Tobramycin['Multiple Tobramycin Tx Courses'] = Tobramycin_minmax['Multiple Tobramycin Tx courses']
Tobramycin = Tobramycin.loc[Tobramycin['Multiple Tobramycin Tx Courses'] == 'Multiple Courses']
Tobramycin = Tobramycin.drop('Multiple Tobramycin Tx Courses', axis=1)
Tobramycin_previous = Tobramycin.loc[Tobramycin['Difference'] <= 274]
Tobramycin_previous = Tobramycin_previous.reset_index()
Tobramycin_previous_tx =  Tobramycin_previous.loc[Tobramycin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Tobramycin_minmax['Prior Tobramycin course end date'] = Tobramycin_previous_tx['Date']
Tobramycin_minmax_copy = Tobramycin_ori.join(Tobramycin_minmax)
def function_Tobramycin1(c):
    if c['Duration of Tobramycin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Tobramycin course end date'], c['Most recent Tobramycin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Tobramycin_minmax_copy['3rd course of Tobramycin?'] = Tobramycin_minmax_copy.apply(function_Tobramycin1, axis=1)
Tobramycin_minmax_copy = Tobramycin_minmax_copy['3rd course of Tobramycin?']
Tobramycin_minmax_copy = Tobramycin_minmax_copy.dropna().drop_duplicates()
Tobramycin_minmax = Tobramycin_minmax.join(Tobramycin_minmax_copy)
col = ['Date of first Tobramycin Rx', 'Prior Tobramycin course end date', 'Most recent Tobramycin course start date', 'Date of last Tobramycin Rx', 'Multiple Tobramycin Tx courses', '3rd course of Tobramycin?', 'Duration of Tobramycin Rx days', '# of Tobramycin Rx']
Tobramycin_minmax = Tobramycin_minmax[col]


Gentamicin = pd.DataFrame({'Index':gentamicin_EMPI, 'Date':gentamicin_date, 'Gentamicin':gentamicin})
Gentamicin['Date'] = pd.to_datetime(Gentamicin['Date'])
Gentamicin_gb = Gentamicin.groupby('Index')
Gentamicin_min = Gentamicin_gb.agg({'Date':np.min})
Gentamicin_max = Gentamicin_gb.agg({'Date':np.max})
Gentamicin_min = Gentamicin_min.rename(columns={"Date": "Date of first Gentamicin Rx"})
Gentamicin_max = Gentamicin_max.rename(columns={"Date": "Date of last Gentamicin Rx"})
Gentamicin_minmax = Gentamicin_min.join(Gentamicin_max, how='outer')
Gentamicin_minmax['Duration of Gentamicin Rx days'] = ((Gentamicin_minmax['Date of last Gentamicin Rx'] - Gentamicin_minmax['Date of first Gentamicin Rx']).dt.days).abs()
Gentamicin_counts = Gentamicin_gb['Gentamicin'].value_counts()
Gentamicin_counts = pd.DataFrame(Gentamicin_counts)
Gentamicin_counts = Gentamicin_counts.rename(columns={"Gentamicin": "# of Gentamicin Rx"})
Gentamicin_counts = Gentamicin_counts.reset_index()
Gentamicin_counts = Gentamicin_counts.set_index('Index')
Gentamicin_minmax['# of Gentamicin Rx'] = Gentamicin_counts["# of Gentamicin Rx"]
def function_Gentamicin(c):
    if c['Duration of Gentamicin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Gentamicin_minmax['Multiple Gentamicin Tx courses'] = Gentamicin_minmax.apply(function_Gentamicin, axis=1)
Gentamicin = Gentamicin.set_index('Index')
Gentamicin = Gentamicin.drop('Gentamicin', axis=1)
Gentamicin_ori = Gentamicin
Gentamicin = Gentamicin.join(Gentamicin_max, how='outer')
Gentamicin['Difference'] = ((Gentamicin['Date'] - Gentamicin['Date of last Gentamicin Rx']).dt.days).abs()
Gentamicin_recent = Gentamicin.loc[Gentamicin['Difference'] <= 274]
Gentamicin_recent = Gentamicin_recent.reset_index()
Gentamicin_recent_txcourse = Gentamicin_recent.loc[Gentamicin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Gentamicin_minmax['Most recent Gentamicin course start date'] = Gentamicin_recent_txcourse['Date']
Gentamicin = Gentamicin.drop('Date of last Gentamicin Rx', axis=1)
Gentamicin['Date of first Gentamicin Rx'] = Gentamicin_minmax['Date of first Gentamicin Rx']
Gentamicin['Difference'] = ((Gentamicin['Date'] - Gentamicin['Date of first Gentamicin Rx']).dt.days)
Gentamicin['Multiple Gentamicin Tx Courses'] = Gentamicin_minmax['Multiple Gentamicin Tx courses']
Gentamicin = Gentamicin.loc[Gentamicin['Multiple Gentamicin Tx Courses'] == 'Multiple Courses']
Gentamicin = Gentamicin.drop('Multiple Gentamicin Tx Courses', axis=1)
Gentamicin_previous = Gentamicin.loc[Gentamicin['Difference'] <= 274]
Gentamicin_previous = Gentamicin_previous.reset_index()
Gentamicin_previous_tx =  Gentamicin_previous.loc[Gentamicin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Gentamicin_minmax['Prior Gentamicin course end date'] = Gentamicin_previous_tx['Date']
Gentamicin_minmax_copy = Gentamicin_ori.join(Gentamicin_minmax)
def function_Gentamicin1(c):
    if c['Duration of Gentamicin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Gentamicin course end date'], c['Most recent Gentamicin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Gentamicin_minmax_copy['3rd course of Gentamicin?'] = Gentamicin_minmax_copy.apply(function_Gentamicin1, axis=1)
Gentamicin_minmax_copy = Gentamicin_minmax_copy['3rd course of Gentamicin?']
Gentamicin_minmax_copy = Gentamicin_minmax_copy.dropna().drop_duplicates()
Gentamicin_minmax = Gentamicin_minmax.join(Gentamicin_minmax_copy)
col = ['Date of first Gentamicin Rx', 'Prior Gentamicin course end date', 'Most recent Gentamicin course start date', 'Date of last Gentamicin Rx', 'Multiple Gentamicin Tx courses', '3rd course of Gentamicin?', 'Duration of Gentamicin Rx days', '# of Gentamicin Rx']
Gentamicin_minmax = Gentamicin_minmax[col]


Linezolid = pd.DataFrame({'Index':linezolid_EMPI, 'Date':linezolid_date, 'Linezolid':linezolid})
Linezolid['Date'] = pd.to_datetime(Linezolid['Date'])
Linezolid_gb = Linezolid.groupby('Index')
Linezolid_min = Linezolid_gb.agg({'Date':np.min})
Linezolid_max = Linezolid_gb.agg({'Date':np.max})
Linezolid_min = Linezolid_min.rename(columns={"Date": "Date of first Linezolid Rx"})
Linezolid_max = Linezolid_max.rename(columns={"Date": "Date of last Linezolid Rx"})
Linezolid_minmax = Linezolid_min.join(Linezolid_max, how='outer')
Linezolid_minmax['Duration of Linezolid Rx days'] = ((Linezolid_minmax['Date of last Linezolid Rx'] - Linezolid_minmax['Date of first Linezolid Rx']).dt.days).abs()
Linezolid_counts = Linezolid_gb['Linezolid'].value_counts()
Linezolid_counts = pd.DataFrame(Linezolid_counts)
Linezolid_counts = Linezolid_counts.rename(columns={"Linezolid": "# of Linezolid Rx"})
Linezolid_counts = Linezolid_counts.reset_index()
Linezolid_counts = Linezolid_counts.set_index('Index')
Linezolid_minmax['# of Linezolid Rx'] = Linezolid_counts["# of Linezolid Rx"]
def function_Linezolid(c):
    if c['Duration of Linezolid Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Linezolid_minmax['Multiple Linezolid Tx courses'] = Linezolid_minmax.apply(function_Linezolid, axis=1)
Linezolid = Linezolid.set_index('Index')
Linezolid = Linezolid.drop('Linezolid', axis=1)
Linezolid_ori = Linezolid
Linezolid = Linezolid.join(Linezolid_max, how='outer')
Linezolid['Difference'] = ((Linezolid['Date'] - Linezolid['Date of last Linezolid Rx']).dt.days).abs()
Linezolid_recent = Linezolid.loc[Linezolid['Difference'] <= 274]
Linezolid_recent = Linezolid_recent.reset_index()
Linezolid_recent_txcourse = Linezolid_recent.loc[Linezolid_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Linezolid_minmax['Most recent Linezolid course start date'] = Linezolid_recent_txcourse['Date']
Linezolid = Linezolid.drop('Date of last Linezolid Rx', axis=1)
Linezolid['Date of first Linezolid Rx'] = Linezolid_minmax['Date of first Linezolid Rx']
Linezolid['Difference'] = ((Linezolid['Date'] - Linezolid['Date of first Linezolid Rx']).dt.days)
Linezolid['Multiple Linezolid Tx Courses'] = Linezolid_minmax['Multiple Linezolid Tx courses']
Linezolid = Linezolid.loc[Linezolid['Multiple Linezolid Tx Courses'] == 'Multiple Courses']
Linezolid = Linezolid.drop('Multiple Linezolid Tx Courses', axis=1)
Linezolid_previous = Linezolid.loc[Linezolid['Difference'] <= 274]
Linezolid_previous = Linezolid_previous.reset_index()
Linezolid_previous_tx =  Linezolid_previous.loc[Linezolid_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Linezolid_minmax['Prior Linezolid course end date'] = Linezolid_previous_tx['Date']
Linezolid_minmax_copy = Linezolid_ori.join(Linezolid_minmax)
def function_Linezolid1(c):
    if c['Duration of Linezolid Rx days'] >= 1460:
        if c['Date'] in (c['Prior Linezolid course end date'], c['Most recent Linezolid course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Linezolid_minmax_copy['3rd course of Linezolid?'] = Linezolid_minmax_copy.apply(function_Linezolid1, axis=1)
Linezolid_minmax_copy = Linezolid_minmax_copy['3rd course of Linezolid?']
Linezolid_minmax_copy = Linezolid_minmax_copy.dropna().drop_duplicates()
Linezolid_minmax = Linezolid_minmax.join(Linezolid_minmax_copy)
col = ['Date of first Linezolid Rx', 'Prior Linezolid course end date', 'Most recent Linezolid course start date', 'Date of last Linezolid Rx', 'Multiple Linezolid Tx courses', '3rd course of Linezolid?', 'Duration of Linezolid Rx days', '# of Linezolid Rx']
Linezolid_minmax = Linezolid_minmax[col]


Cefoxitin = pd.DataFrame({'Index':cefoxitin_EMPI, 'Date':cefoxitin_date, 'Cefoxitin':cefoxitin})
Cefoxitin['Date'] = pd.to_datetime(Cefoxitin['Date'])
Cefoxitin_gb = Cefoxitin.groupby('Index')
Cefoxitin_min = Cefoxitin_gb.agg({'Date':np.min})
Cefoxitin_max = Cefoxitin_gb.agg({'Date':np.max})
Cefoxitin_min = Cefoxitin_min.rename(columns={"Date": "Date of first Cefoxitin Rx"})
Cefoxitin_max = Cefoxitin_max.rename(columns={"Date": "Date of last Cefoxitin Rx"})
Cefoxitin_minmax = Cefoxitin_min.join(Cefoxitin_max, how='outer')
Cefoxitin_minmax['Duration of Cefoxitin Rx days'] = ((Cefoxitin_minmax['Date of last Cefoxitin Rx'] - Cefoxitin_minmax['Date of first Cefoxitin Rx']).dt.days).abs()
Cefoxitin_counts = Cefoxitin_gb['Cefoxitin'].value_counts()
Cefoxitin_counts = pd.DataFrame(Cefoxitin_counts)
Cefoxitin_counts = Cefoxitin_counts.rename(columns={"Cefoxitin": "# of Cefoxitin Rx"})
Cefoxitin_counts = Cefoxitin_counts.reset_index()
Cefoxitin_counts = Cefoxitin_counts.set_index('Index')
Cefoxitin_minmax['# of Cefoxitin Rx'] = Cefoxitin_counts["# of Cefoxitin Rx"]
def function_Cefoxitin(c):
    if c['Duration of Cefoxitin Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Cefoxitin_minmax['Multiple Cefoxitin Tx courses'] = Cefoxitin_minmax.apply(function_Cefoxitin, axis=1)
Cefoxitin = Cefoxitin.set_index('Index')
Cefoxitin = Cefoxitin.drop('Cefoxitin', axis=1)
Cefoxitin_ori = Cefoxitin
Cefoxitin = Cefoxitin.join(Cefoxitin_max, how='outer')
Cefoxitin['Difference'] = ((Cefoxitin['Date'] - Cefoxitin['Date of last Cefoxitin Rx']).dt.days).abs()
Cefoxitin_recent = Cefoxitin.loc[Cefoxitin['Difference'] <= 274]
Cefoxitin_recent = Cefoxitin_recent.reset_index()
Cefoxitin_recent_txcourse = Cefoxitin_recent.loc[Cefoxitin_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Cefoxitin_minmax['Most recent Cefoxitin course start date'] = Cefoxitin_recent_txcourse['Date']
Cefoxitin = Cefoxitin.drop('Date of last Cefoxitin Rx', axis=1)
Cefoxitin['Date of first Cefoxitin Rx'] = Cefoxitin_minmax['Date of first Cefoxitin Rx']
Cefoxitin['Difference'] = ((Cefoxitin['Date'] - Cefoxitin['Date of first Cefoxitin Rx']).dt.days)
Cefoxitin['Multiple Cefoxitin Tx Courses'] = Cefoxitin_minmax['Multiple Cefoxitin Tx courses']
Cefoxitin = Cefoxitin.loc[Cefoxitin['Multiple Cefoxitin Tx Courses'] == 'Multiple Courses']
Cefoxitin = Cefoxitin.drop('Multiple Cefoxitin Tx Courses', axis=1)
Cefoxitin_previous = Cefoxitin.loc[Cefoxitin['Difference'] <= 274]
Cefoxitin_previous = Cefoxitin_previous.reset_index()
Cefoxitin_previous_tx =  Cefoxitin_previous.loc[Cefoxitin_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Cefoxitin_minmax['Prior Cefoxitin course end date'] = Cefoxitin_previous_tx['Date']
Cefoxitin_minmax_copy = Cefoxitin_ori.join(Cefoxitin_minmax)
def function_Cefoxitin1(c):
    if c['Duration of Cefoxitin Rx days'] >= 1460:
        if c['Date'] in (c['Prior Cefoxitin course end date'], c['Most recent Cefoxitin course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Cefoxitin_minmax_copy['3rd course of Cefoxitin?'] = Cefoxitin_minmax_copy.apply(function_Cefoxitin1, axis=1)
Cefoxitin_minmax_copy = Cefoxitin_minmax_copy['3rd course of Cefoxitin?']
Cefoxitin_minmax_copy = Cefoxitin_minmax_copy.dropna().drop_duplicates()
Cefoxitin_minmax = Cefoxitin_minmax.join(Cefoxitin_minmax_copy)
col = ['Date of first Cefoxitin Rx', 'Prior Cefoxitin course end date', 'Most recent Cefoxitin course start date', 'Date of last Cefoxitin Rx', 'Multiple Cefoxitin Tx courses', '3rd course of Cefoxitin?', 'Duration of Cefoxitin Rx days', '# of Cefoxitin Rx']
Cefoxitin_minmax = Cefoxitin_minmax[col]


Ceftaroline = pd.DataFrame({'Index':ceftaroline_EMPI, 'Date':ceftaroline_date, 'Ceftaroline':ceftaroline})
Ceftaroline['Date'] = pd.to_datetime(Ceftaroline['Date'])
Ceftaroline_gb = Ceftaroline.groupby('Index')
Ceftaroline_min = Ceftaroline_gb.agg({'Date':np.min})
Ceftaroline_max = Ceftaroline_gb.agg({'Date':np.max})
Ceftaroline_min = Ceftaroline_min.rename(columns={"Date": "Date of first Ceftaroline Rx"})
Ceftaroline_max = Ceftaroline_max.rename(columns={"Date": "Date of last Ceftaroline Rx"})
Ceftaroline_minmax = Ceftaroline_min.join(Ceftaroline_max, how='outer')
Ceftaroline_minmax['Duration of Ceftaroline Rx days'] = ((Ceftaroline_minmax['Date of last Ceftaroline Rx'] - Ceftaroline_minmax['Date of first Ceftaroline Rx']).dt.days).abs()
Ceftaroline_counts = Ceftaroline_gb['Ceftaroline'].value_counts()
Ceftaroline_counts = pd.DataFrame(Ceftaroline_counts)
Ceftaroline_counts = Ceftaroline_counts.rename(columns={"Ceftaroline": "# of Ceftaroline Rx"})
Ceftaroline_counts = Ceftaroline_counts.reset_index()
Ceftaroline_counts = Ceftaroline_counts.set_index('Index')
Ceftaroline_minmax['# of Ceftaroline Rx'] = Ceftaroline_counts["# of Ceftaroline Rx"]
Ceftaroline_minmax


Imipenem = pd.DataFrame({'Index':imipenem_EMPI, 'Date':imipenem_date, 'Imipenem':imipenem})
Imipenem['Date'] = pd.to_datetime(Imipenem['Date'])
Imipenem_gb = Imipenem.groupby('Index')
Imipenem_min = Imipenem_gb.agg({'Date':np.min})
Imipenem_max = Imipenem_gb.agg({'Date':np.max})
Imipenem_min = Imipenem_min.rename(columns={"Date": "Date of first Imipenem Rx"})
Imipenem_max = Imipenem_max.rename(columns={"Date": "Date of last Imipenem Rx"})
Imipenem_minmax = Imipenem_min.join(Imipenem_max, how='outer')
Imipenem_minmax['Duration of Imipenem Rx days'] = ((Imipenem_minmax['Date of last Imipenem Rx'] - Imipenem_minmax['Date of first Imipenem Rx']).dt.days).abs()
Imipenem_counts = Imipenem_gb['Imipenem'].value_counts()
Imipenem_counts = pd.DataFrame(Imipenem_counts)
Imipenem_counts = Imipenem_counts.rename(columns={"Imipenem": "# of Imipenem Rx"})
Imipenem_counts = Imipenem_counts.reset_index()
Imipenem_counts = Imipenem_counts.set_index('Index')
Imipenem_minmax['# of Imipenem Rx'] = Imipenem_counts["# of Imipenem Rx"]
def function_Imipenem(c):
    if c['Duration of Imipenem Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Imipenem_minmax['Multiple Imipenem Tx courses'] = Imipenem_minmax.apply(function_Imipenem, axis=1)
Imipenem = Imipenem.set_index('Index')
Imipenem = Imipenem.drop('Imipenem', axis=1)
Imipenem_ori = Imipenem
Imipenem = Imipenem.join(Imipenem_max, how='outer')
Imipenem['Difference'] = ((Imipenem['Date'] - Imipenem['Date of last Imipenem Rx']).dt.days).abs()
Imipenem_recent = Imipenem.loc[Imipenem['Difference'] <= 274]
Imipenem_recent = Imipenem_recent.reset_index()
Imipenem_recent_txcourse = Imipenem_recent.loc[Imipenem_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Imipenem_minmax['Most recent Imipenem course start date'] = Imipenem_recent_txcourse['Date']
Imipenem = Imipenem.drop('Date of last Imipenem Rx', axis=1)
Imipenem['Date of first Imipenem Rx'] = Imipenem_minmax['Date of first Imipenem Rx']
Imipenem['Difference'] = ((Imipenem['Date'] - Imipenem['Date of first Imipenem Rx']).dt.days)
Imipenem['Multiple Imipenem Tx Courses'] = Imipenem_minmax['Multiple Imipenem Tx courses']
Imipenem = Imipenem.loc[Imipenem['Multiple Imipenem Tx Courses'] == 'Multiple Courses']
Imipenem = Imipenem.drop('Multiple Imipenem Tx Courses', axis=1)
Imipenem_previous = Imipenem.loc[Imipenem['Difference'] <= 274]
Imipenem_previous = Imipenem_previous.reset_index()
Imipenem_previous_tx =  Imipenem_previous.loc[Imipenem_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Imipenem_minmax['Prior Imipenem course end date'] = Imipenem_previous_tx['Date']
Imipenem_minmax_copy = Imipenem_ori.join(Imipenem_minmax)
def function_Imipenem1(c):
    if c['Duration of Imipenem Rx days'] >= 1460:
        if c['Date'] in (c['Prior Imipenem course end date'], c['Most recent Imipenem course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Imipenem_minmax_copy['3rd course of Imipenem?'] = Imipenem_minmax_copy.apply(function_Imipenem1, axis=1)
Imipenem_minmax_copy = Imipenem_minmax_copy['3rd course of Imipenem?']
Imipenem_minmax_copy = Imipenem_minmax_copy.dropna().drop_duplicates()
Imipenem_minmax = Imipenem_minmax.join(Imipenem_minmax_copy)
col = ['Date of first Imipenem Rx', 'Prior Imipenem course end date', 'Most recent Imipenem course start date', 'Date of last Imipenem Rx', 'Multiple Imipenem Tx courses', '3rd course of Imipenem?', 'Duration of Imipenem Rx days', '# of Imipenem Rx']
Imipenem_minmax = Imipenem_minmax[col]


Meropenem = pd.DataFrame({'Index':meropenem_EMPI, 'Date':meropenem_date, 'Meropenem':meropenem})
Meropenem['Date'] = pd.to_datetime(Meropenem['Date'])
Meropenem_gb = Meropenem.groupby('Index')
Meropenem_min = Meropenem_gb.agg({'Date':np.min})
Meropenem_max = Meropenem_gb.agg({'Date':np.max})
Meropenem_min = Meropenem_min.rename(columns={"Date": "Date of first Meropenem Rx"})
Meropenem_max = Meropenem_max.rename(columns={"Date": "Date of last Meropenem Rx"})
Meropenem_minmax = Meropenem_min.join(Meropenem_max, how='outer')
Meropenem_minmax['Duration of Meropenem Rx days'] = ((Meropenem_minmax['Date of last Meropenem Rx'] - Meropenem_minmax['Date of first Meropenem Rx']).dt.days).abs()
Meropenem_counts = Meropenem_gb['Meropenem'].value_counts()
Meropenem_counts = pd.DataFrame(Meropenem_counts)
Meropenem_counts = Meropenem_counts.rename(columns={"Meropenem": "# of Meropenem Rx"})
Meropenem_counts = Meropenem_counts.reset_index()
Meropenem_counts = Meropenem_counts.set_index('Index')
Meropenem_minmax['# of Meropenem Rx'] = Meropenem_counts["# of Meropenem Rx"]
def function_Meropenem(c):
    if c['Duration of Meropenem Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Meropenem_minmax['Multiple Meropenem Tx courses'] = Meropenem_minmax.apply(function_Meropenem, axis=1)
Meropenem = Meropenem.set_index('Index')
Meropenem = Meropenem.drop('Meropenem', axis=1)
Meropenem_ori = Meropenem
Meropenem = Meropenem.join(Meropenem_max, how='outer')
Meropenem['Difference'] = ((Meropenem['Date'] - Meropenem['Date of last Meropenem Rx']).dt.days).abs()
Meropenem_recent = Meropenem.loc[Meropenem['Difference'] <= 274]
Meropenem_recent = Meropenem_recent.reset_index()
Meropenem_recent_txcourse = Meropenem_recent.loc[Meropenem_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Meropenem_minmax['Most recent Meropenem course start date'] = Meropenem_recent_txcourse['Date']
Meropenem = Meropenem.drop('Date of last Meropenem Rx', axis=1)
Meropenem['Date of first Meropenem Rx'] = Meropenem_minmax['Date of first Meropenem Rx']
Meropenem['Difference'] = ((Meropenem['Date'] - Meropenem['Date of first Meropenem Rx']).dt.days)
Meropenem['Multiple Meropenem Tx Courses'] = Meropenem_minmax['Multiple Meropenem Tx courses']
Meropenem = Meropenem.loc[Meropenem['Multiple Meropenem Tx Courses'] == 'Multiple Courses']
Meropenem = Meropenem.drop('Multiple Meropenem Tx Courses', axis=1)
Meropenem_previous = Meropenem.loc[Meropenem['Difference'] <= 274]
Meropenem_previous = Meropenem_previous.reset_index()
Meropenem_previous_tx =  Meropenem_previous.loc[Meropenem_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Meropenem_minmax['Prior Meropenem course end date'] = Meropenem_previous_tx['Date']
Meropenem_minmax_copy = Meropenem_ori.join(Meropenem_minmax)
def function_Meropenem1(c):
    if c['Duration of Meropenem Rx days'] >= 1460:
        if c['Date'] in (c['Prior Meropenem course end date'], c['Most recent Meropenem course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Meropenem_minmax_copy['3rd course of Meropenem?'] = Meropenem_minmax_copy.apply(function_Meropenem1, axis=1)
Meropenem_minmax_copy = Meropenem_minmax_copy['3rd course of Meropenem?']
Meropenem_minmax_copy = Meropenem_minmax_copy.dropna().drop_duplicates()
Meropenem_minmax = Meropenem_minmax.join(Meropenem_minmax_copy)
col = ['Date of first Meropenem Rx', 'Prior Meropenem course end date', 'Most recent Meropenem course start date', 'Date of last Meropenem Rx', 'Multiple Meropenem Tx courses', '3rd course of Meropenem?', 'Duration of Meropenem Rx days', '# of Meropenem Rx']
Meropenem_minmax = Meropenem_minmax[col]


Tigecycline = pd.DataFrame({'Index':tigecycline_EMPI, 'Date':tigecycline_date, 'Tigecycline':tigecycline})
Tigecycline['Date'] = pd.to_datetime(Tigecycline['Date'])
Tigecycline_gb = Tigecycline.groupby('Index')
Tigecycline_min = Tigecycline_gb.agg({'Date':np.min})
Tigecycline_max = Tigecycline_gb.agg({'Date':np.max})
Tigecycline_min = Tigecycline_min.rename(columns={"Date": "Date of first Tigecycline Rx"})
Tigecycline_max = Tigecycline_max.rename(columns={"Date": "Date of last Tigecycline Rx"})
Tigecycline_minmax = Tigecycline_min.join(Tigecycline_max, how='outer')
Tigecycline_minmax['Duration of Tigecycline Rx days'] = ((Tigecycline_minmax['Date of last Tigecycline Rx'] - Tigecycline_minmax['Date of first Tigecycline Rx']).dt.days).abs()
Tigecycline_counts = Tigecycline_gb['Tigecycline'].value_counts()
Tigecycline_counts = pd.DataFrame(Tigecycline_counts)
Tigecycline_counts = Tigecycline_counts.rename(columns={"Tigecycline": "# of Tigecycline Rx"})
Tigecycline_counts = Tigecycline_counts.reset_index()
Tigecycline_counts = Tigecycline_counts.set_index('Index')
Tigecycline_minmax['# of Tigecycline Rx'] = Tigecycline_counts["# of Tigecycline Rx"]
def function_Tigecycline(c):
    if c['Duration of Tigecycline Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Tigecycline_minmax['Multiple Tigecycline Tx courses'] = Tigecycline_minmax.apply(function_Tigecycline, axis=1)
Tigecycline = Tigecycline.set_index('Index')
Tigecycline = Tigecycline.drop('Tigecycline', axis=1)
Tigecycline_ori = Tigecycline
Tigecycline = Tigecycline.join(Tigecycline_max, how='outer')
Tigecycline['Difference'] = ((Tigecycline['Date'] - Tigecycline['Date of last Tigecycline Rx']).dt.days).abs()
Tigecycline_recent = Tigecycline.loc[Tigecycline['Difference'] <= 274]
Tigecycline_recent = Tigecycline_recent.reset_index()
Tigecycline_recent_txcourse = Tigecycline_recent.loc[Tigecycline_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Tigecycline_minmax['Most recent Tigecycline course start date'] = Tigecycline_recent_txcourse['Date']
Tigecycline = Tigecycline.drop('Date of last Tigecycline Rx', axis=1)
Tigecycline['Date of first Tigecycline Rx'] = Tigecycline_minmax['Date of first Tigecycline Rx']
Tigecycline['Difference'] = ((Tigecycline['Date'] - Tigecycline['Date of first Tigecycline Rx']).dt.days)
Tigecycline['Multiple Tigecycline Tx Courses'] = Tigecycline_minmax['Multiple Tigecycline Tx courses']
Tigecycline = Tigecycline.loc[Tigecycline['Multiple Tigecycline Tx Courses'] == 'Multiple Courses']
Tigecycline = Tigecycline.drop('Multiple Tigecycline Tx Courses', axis=1)
Tigecycline_previous = Tigecycline.loc[Tigecycline['Difference'] <= 274]
Tigecycline_previous = Tigecycline_previous.reset_index()
Tigecycline_previous_tx =  Tigecycline_previous.loc[Tigecycline_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Tigecycline_minmax['Prior Tigecycline course end date'] = Tigecycline_previous_tx['Date']
Tigecycline_minmax_copy = Tigecycline_ori.join(Tigecycline_minmax)
def function_Tigecycline1(c):
    if c['Duration of Tigecycline Rx days'] >= 1460:
        if c['Date'] in (c['Prior Tigecycline course end date'], c['Most recent Tigecycline course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Tigecycline_minmax_copy['3rd course of Tigecycline?'] = Tigecycline_minmax_copy.apply(function_Tigecycline1, axis=1)
Tigecycline_minmax_copy = Tigecycline_minmax_copy['3rd course of Tigecycline?']
Tigecycline_minmax_copy = Tigecycline_minmax_copy.dropna().drop_duplicates()
Tigecycline_minmax = Tigecycline_minmax.join(Tigecycline_minmax_copy)
col = ['Date of first Tigecycline Rx', 'Prior Tigecycline course end date', 'Most recent Tigecycline course start date', 'Date of last Tigecycline Rx', 'Multiple Tigecycline Tx courses', '3rd course of Tigecycline?', 'Duration of Tigecycline Rx days', '# of Tigecycline Rx']
Tigecycline_minmax = Tigecycline_minmax[col]


Bactrim = pd.DataFrame({'Index':bactrim_EMPI, 'Date':bactrim_date, 'Bactrim':bactrim})
Bactrim['Date'] = pd.to_datetime(Bactrim['Date'])
Bactrim_gb = Bactrim.groupby('Index')
Bactrim_min = Bactrim_gb.agg({'Date':np.min})
Bactrim_max = Bactrim_gb.agg({'Date':np.max})
Bactrim_min = Bactrim_min.rename(columns={"Date": "Date of first Bactrim Rx"})
Bactrim_max = Bactrim_max.rename(columns={"Date": "Date of last Bactrim Rx"})
Bactrim_minmax = Bactrim_min.join(Bactrim_max, how='outer')
Bactrim_minmax['Duration of Bactrim Rx days'] = ((Bactrim_minmax['Date of last Bactrim Rx'] - Bactrim_minmax['Date of first Bactrim Rx']).dt.days).abs()
Bactrim_counts = Bactrim_gb['Bactrim'].value_counts()
Bactrim_counts = pd.DataFrame(Bactrim_counts)
Bactrim_counts = Bactrim_counts.rename(columns={"Bactrim": "# of Bactrim Rx"})
Bactrim_counts = Bactrim_counts.reset_index()
Bactrim_counts = Bactrim_counts.set_index('Index')
Bactrim_minmax['# of Bactrim Rx'] = Bactrim_counts["# of Bactrim Rx"]
def function_Bactrim(c):
    if c['Duration of Bactrim Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Bactrim_minmax['Multiple Bactrim Tx courses'] = Bactrim_minmax.apply(function_Bactrim, axis=1)
Bactrim = Bactrim.set_index('Index')
Bactrim = Bactrim.drop('Bactrim', axis=1)
Bactrim_ori = Bactrim
Bactrim = Bactrim.join(Bactrim_max, how='outer')
Bactrim['Difference'] = ((Bactrim['Date'] - Bactrim['Date of last Bactrim Rx']).dt.days).abs()
Bactrim_recent = Bactrim.loc[Bactrim['Difference'] <= 274]
Bactrim_recent = Bactrim_recent.reset_index()
Bactrim_recent_txcourse = Bactrim_recent.loc[Bactrim_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Bactrim_minmax['Most recent Bactrim course start date'] = Bactrim_recent_txcourse['Date']
Bactrim = Bactrim.drop('Date of last Bactrim Rx', axis=1)
Bactrim['Date of first Bactrim Rx'] = Bactrim_minmax['Date of first Bactrim Rx']
Bactrim['Difference'] = ((Bactrim['Date'] - Bactrim['Date of first Bactrim Rx']).dt.days)
Bactrim['Multiple Bactrim Tx Courses'] = Bactrim_minmax['Multiple Bactrim Tx courses']
Bactrim = Bactrim.loc[Bactrim['Multiple Bactrim Tx Courses'] == 'Multiple Courses']
Bactrim = Bactrim.drop('Multiple Bactrim Tx Courses', axis=1)
Bactrim_previous = Bactrim.loc[Bactrim['Difference'] <= 274]
Bactrim_previous = Bactrim_previous.reset_index()
Bactrim_previous_tx =  Bactrim_previous.loc[Bactrim_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Bactrim_minmax['Prior Bactrim course end date'] = Bactrim_previous_tx['Date']
Bactrim_minmax_copy = Bactrim_ori.join(Bactrim_minmax)
def function_Bactrim1(c):
    if c['Duration of Bactrim Rx days'] >= 1460:
        if c['Date'] in (c['Prior Bactrim course end date'], c['Most recent Bactrim course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Bactrim_minmax_copy['3rd course of Bactrim?'] = Bactrim_minmax_copy.apply(function_Bactrim1, axis=1)
Bactrim_minmax_copy = Bactrim_minmax_copy['3rd course of Bactrim?']
Bactrim_minmax_copy = Bactrim_minmax_copy.dropna().drop_duplicates()
Bactrim_minmax = Bactrim_minmax.join(Bactrim_minmax_copy)
col = ['Date of first Bactrim Rx', 'Prior Bactrim course end date', 'Most recent Bactrim course start date', 'Date of last Bactrim Rx', 'Multiple Bactrim Tx courses', '3rd course of Bactrim?', 'Duration of Bactrim Rx days', '# of Bactrim Rx']
Bactrim_minmax = Bactrim_minmax[col]


Doxycycline = pd.DataFrame({'Index':doxycycline_EMPI, 'Date':doxycycline_date, 'Doxycycline':doxycycline})
Doxycycline['Date'] = pd.to_datetime(Doxycycline['Date'])
Doxycycline_gb = Doxycycline.groupby('Index')
Doxycycline_min = Doxycycline_gb.agg({'Date':np.min})
Doxycycline_max = Doxycycline_gb.agg({'Date':np.max})
Doxycycline_min = Doxycycline_min.rename(columns={"Date": "Date of first Doxycycline Rx"})
Doxycycline_max = Doxycycline_max.rename(columns={"Date": "Date of last Doxycycline Rx"})
Doxycycline_minmax = Doxycycline_min.join(Doxycycline_max, how='outer')
Doxycycline_minmax['Duration of Doxycycline Rx days'] = ((Doxycycline_minmax['Date of last Doxycycline Rx'] - Doxycycline_minmax['Date of first Doxycycline Rx']).dt.days).abs()
Doxycycline_counts = Doxycycline_gb['Doxycycline'].value_counts()
Doxycycline_counts = pd.DataFrame(Doxycycline_counts)
Doxycycline_counts = Doxycycline_counts.rename(columns={"Doxycycline": "# of Doxycycline Rx"})
Doxycycline_counts = Doxycycline_counts.reset_index()
Doxycycline_counts = Doxycycline_counts.set_index('Index')
Doxycycline_minmax['# of Doxycycline Rx'] = Doxycycline_counts["# of Doxycycline Rx"]
def function_Doxycycline(c):
    if c['Duration of Doxycycline Rx days'] >= 274:
        return 'Multiple Courses'
    else:
        return np.nan
Doxycycline_minmax['Multiple Doxycycline Tx courses'] = Doxycycline_minmax.apply(function_Doxycycline, axis=1)
Doxycycline = Doxycycline.set_index('Index')
Doxycycline = Doxycycline.drop('Doxycycline', axis=1)
Doxycycline_ori = Doxycycline
Doxycycline = Doxycycline.join(Doxycycline_max, how='outer')
Doxycycline['Difference'] = ((Doxycycline['Date'] - Doxycycline['Date of last Doxycycline Rx']).dt.days).abs()
Doxycycline_recent = Doxycycline.loc[Doxycycline['Difference'] <= 274]
Doxycycline_recent = Doxycycline_recent.reset_index()
Doxycycline_recent_txcourse = Doxycycline_recent.loc[Doxycycline_recent.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Doxycycline_minmax['Most recent Doxycycline course start date'] = Doxycycline_recent_txcourse['Date']
Doxycycline = Doxycycline.drop('Date of last Doxycycline Rx', axis=1)
Doxycycline['Date of first Doxycycline Rx'] = Doxycycline_minmax['Date of first Doxycycline Rx']
Doxycycline['Difference'] = ((Doxycycline['Date'] - Doxycycline['Date of first Doxycycline Rx']).dt.days)
Doxycycline['Multiple Doxycycline Tx Courses'] = Doxycycline_minmax['Multiple Doxycycline Tx courses']
Doxycycline = Doxycycline.loc[Doxycycline['Multiple Doxycycline Tx Courses'] == 'Multiple Courses']
Doxycycline = Doxycycline.drop('Multiple Doxycycline Tx Courses', axis=1)
Doxycycline_previous = Doxycycline.loc[Doxycycline['Difference'] <= 274 ]
Doxycycline_previous = Doxycycline_previous.reset_index()
Doxycycline_previous_tx =  Doxycycline_previous.loc[Doxycycline_previous.groupby(['Index'])['Difference'].idxmax()].set_index('Index')
Doxycycline_minmax['Prior Doxycycline course end date'] = Doxycycline_previous_tx['Date']
Doxycycline_minmax_copy = Doxycycline_ori.join(Doxycycline_minmax)
def function_Doxycycline1(c):
    if c['Duration of Doxycycline Rx days'] >= 1460:
        if c['Date'] in (c['Prior Doxycycline course end date'], c['Most recent Doxycycline course start date']):
            return '3rd course recieved'
        else:
            return np.nan
Doxycycline_minmax_copy['3rd course of Doxycycline?'] = Doxycycline_minmax_copy.apply(function_Doxycycline1, axis=1)
Doxycycline_minmax_copy = Doxycycline_minmax_copy['3rd course of Doxycycline?']
Doxycycline_minmax_copy = Doxycycline_minmax_copy.dropna().drop_duplicates()
Doxycycline_minmax = Doxycycline_minmax.join(Doxycycline_minmax_copy)
col = ['Date of first Doxycycline Rx', 'Prior Doxycycline course end date', 'Most recent Doxycycline course start date', 'Date of last Doxycycline Rx', 'Multiple Doxycycline Tx courses', '3rd course of Doxycycline?', 'Duration of Doxycycline Rx days', '# of Doxycycline Rx']
Doxycycline_minmax = Doxycycline_minmax[col]

Clarithromycin_minmax['Clarithromycin'] = Clarithromycin_minmax.apply(lambda _: 'Clarithromycin', axis=1)
Ethambutol_minmax['Ethambutol'] = Ethambutol_minmax.apply(lambda _: 'Ethambutol', axis=1)
Rifampicin_minmax['Rifampicin'] = Rifampicin_minmax.apply(lambda _: 'Rifampicin', axis=1)
#Rifabutin_minmax['Rifabutin'] = Rifabutin_minmax.apply(lambda _: 'Rifabutin', axis=1)
Bedaqualine_minmax['Bedaqualine'] = Bedaqualine_minmax.apply(lambda _: 'Bedaqualine', axis=1)
Isoniazid_minmax['Isoniazid'] = Isoniazid_minmax.apply(lambda _: 'Isoniazid', axis=1)
Clofazimine_minmax['Clofazimine'] = Clofazimine_minmax.apply(lambda _: 'Clofazimine', axis=1)
Amikacin_minmax['Amikacin'] = Amikacin_minmax.apply(lambda _: 'Amikacin', axis=1)
Azithromycin_minmax['Azithromycin'] = Azithromycin_minmax.apply(lambda _: 'Azithromycin', axis=1)
Moxifloxacin_minmax['Moxifloxacin'] = Moxifloxacin_minmax.apply(lambda _: 'Moxifloxacin', axis=1)
Levofloxacin_minmax['Levofloxacin'] = Levofloxacin_minmax.apply(lambda _: 'Levofloxacin', axis=1)
Tobramycin_minmax['Tobramycin'] = Tobramycin_minmax.apply(lambda _: 'Tobramycin', axis=1)
Gentamicin_minmax['Gentamicin'] = Gentamicin_minmax.apply(lambda _: 'Gentamicin', axis=1)
Linezolid_minmax['Linezolid'] = Linezolid_minmax.apply(lambda _: 'Linezolid', axis=1)
Cefoxitin_minmax['Cefoxitin'] = Cefoxitin_minmax.apply(lambda _: 'Cefoxitin', axis=1)
Ceftaroline_minmax['Ceftaroline'] = Ceftaroline_minmax.apply(lambda _: 'Ceftaroline', axis=1)
Imipenem_minmax['Imipenem'] = Imipenem_minmax.apply(lambda _: 'Imipenem', axis=1)
Meropenem_minmax['Meropenem'] = Meropenem_minmax.apply(lambda _: 'Meropenem', axis=1)
Tigecycline_minmax['Tigecycline'] = Tigecycline_minmax.apply(lambda _: 'Tigecycline', axis=1)
Bactrim_minmax['Bactrim'] = Bactrim_minmax.apply(lambda _: 'Bactrim', axis=1)
Doxycycline_minmax['Doxycycline'] = Doxycycline_minmax.apply(lambda _: 'Doxycycline', axis=1)

Medications = Clarithromycin_minmax.join(Ethambutol_minmax, how='outer')
Medications = Medications.join(Rifampicin_minmax, how='outer')
#Medications = Medications.join(Rifabutin_minmax, how='outer')
Medications = Medications.join(Bedaqualine_minmax, how='outer')
Medications = Medications.join(Isoniazid_minmax, how='outer')
Medications = Medications.join(Clofazimine_minmax, how='outer')
Medications = Medications.join(Amikacin_minmax, how='outer')
Medications = Medications.join(Azithromycin_minmax, how= 'outer')
Medications = Medications.join(Moxifloxacin_minmax, how= 'outer')
Medications = Medications.join(Levofloxacin_minmax, how= 'outer')
Medications = Medications.join(Tobramycin_minmax, how= 'outer')
Medications = Medications.join(Gentamicin_minmax, how= 'outer')
Medications = Medications.join(Linezolid_minmax, how= 'outer')
Medications = Medications.join(Cefoxitin_minmax, how= 'outer')
Medications = Medications.join(Ceftaroline_minmax, how= 'outer')
Medications = Medications.join(Imipenem_minmax, how= 'outer')
Medications = Medications.join(Meropenem_minmax, how= 'outer')
Medications = Medications.join(Tigecycline_minmax, how= 'outer')
Medications = Medications.join(Bactrim_minmax, how= 'outer')
Medications = Medications.join(Doxycycline_minmax, how= 'outer')
Medications['Treatment Date'] = Medications[['Date of last Clarithromycin Rx', 'Date of last Ethambutol Rx','Date of last Rifampicin Rx', 'Date of last Clofazimine Rx', 'Date of last Bedaqualine Rx', 'Date of last Isoniazid Rx', 'Date of last Isoniazid Rx', 'Date of last Amikacin Rx']].max(axis=1)
#'Date of last Rifabutin Rx',
Medications['Treatment Start Date'] = Medications[['Date of first Clarithromycin Rx', 'Date of first Ethambutol Rx','Date of first Rifampicin Rx', 'Date of first Clofazimine Rx', 'Date of first Bedaqualine Rx', 'Date of first Isoniazid Rx', 'Date of first Isoniazid Rx', 'Date of first Amikacin Rx']].min(axis=1)

Medications['All Treatments'] = Medications['Clarithromycin'].map(str) + ", " + Medications['Rifampicin'].map(str) + ", "  + Medications['Bedaqualine'].map(str)+ ", " + Medications['Isoniazid'].map(str)+ ", " + Medications['Clofazimine'].map(str)+ ", " + Medications['Amikacin'].map(str)+ ", " + Medications['Azithromycin'].map(str)+ ", " + Medications['Moxifloxacin'].map(str)+ ", " + Medications['Levofloxacin'].map(str)+ ", "+Medications['Tobramycin'].map(str)+ ", " + Medications['Gentamicin'].map(str)+ ", " + Medications['Linezolid'].map(str)+ ", " + Medications['Cefoxitin'].map(str)+ ", " + Medications['Ceftaroline'].map(str)+ Medications['Imipenem'].map(str)+ ", " + Medications['Meropenem'].map(str)+ ", " + Medications['Tigecycline'].map(str)+ ", " + Medications['Bactrim'].map(str)+ ", " + Medications['Doxycycline'].map(str) +", " + Medications['Ethambutol'].map(str)
#+ Medications['Rifabutin'].map(str)+ ", "
Medications['All Treatments'] = Medications['All Treatments'].str.replace('nan,', '')
Medications['All Treatments'] = Medications['All Treatments'].str.replace('nan', '')
Medications['All Treatments'] = Medications['All Treatments'].str.replace('\s+', ' ')

#----------------------------
#Manually Extracted surgical patient data
Surgery_Cohort = pd.DataFrame.from_csv('/Volumes/homedir$/MAC Project/Complete Project/Mac Surgeries.csv', header=0, index_col=0)


#Surgery_Cohort['Date of Surgery'] = pd.to_datetime(Surgery_Cohort['Date of Surgery'])
Surgery_Cohort.index = Surgery_Cohort.index.astype(str)
Date_surgery = Surgery_Cohort[['Date of Surgery', 'Surgery for MAC?']]
Medications = Medications.join(Date_surgery, how= 'outer')
NTB_diagnosis_maxdate_pickle_in = open('NTB_diagnosis_maxdate.pickle','rb')
NTB_diagnosis_maxdate = pickle.load(NTB_diagnosis_maxdate_pickle_in)
Medications = NTB_diagnosis_maxdate.join(Medications, how='outer')
Medications['Surgery for MAC?'] = Medications['Surgery for MAC?'].fillna('No')
#Medications['Treatment Date'] = pd.to_datetime(Medications['Treatment Date'])
#Medications['Date of Surgery'] = pd.to_datetime(Medications['Date of Surgery'])
#Medications['Last appearance of NTB ICD'] = pd.to_datetime(Medications['Last appearance of NTB ICD'])
# Medications['Surgery for MAC?'] = Medications['Surgery for MAC?'].astype(str)
Medications['Treatment Date'] = Medications['Treatment Date'].fillna('NaT')
def medicaltx(c):
    if c['Treatment Date'] is 'NaT':
        return 'No'
    else:
        return 'Yes'
Medications['Medical Treatment?'] = Medications.apply(medicaltx, axis=1)

def func(c):
    if c['Treatment Date'] is 'NaT':
        return c['Last appearance of NTB ICD']
    else:
        return c['Treatment Date']
Medications['Follow-up Date'] = Medications.apply(func, axis=1)

def func1(c):
    if c['Date of Surgery'] is not np.nan:
        return c['Date of Surgery']
    else:
        return c['Follow-up Date']
Medications['Follow-up Date'] = Medications.apply(func1, axis=1)


#Date at which treatment was sent

NTB_diagnosis_mindate_pickle_in = open('NTB_diagnosis_mindate.pickle','rb')
NTB_diagnosis_mindate = pickle.load(NTB_diagnosis_mindate_pickle_in)
NTB_diagnosis_mindate = pd.DataFrame(NTB_diagnosis_mindate)
Medications = NTB_diagnosis_mindate.join(Medications, how='outer')


def func(c):
    if c['Treatment Start Date'] is 'NaT':
        return c['Date of first Dx']
    else:
        return c['Treatment Start Date']
Medications['Treatment Initiation'] = Medications.apply(func, axis=1)

def func1(c):
    if c['Date of Surgery'] is not np.nan:
        return c['Date of Surgery']
    else:
        return c['Treatment Initiation']
Medications['Treatment Initiation'] = Medications.apply(func1, axis=1)

Medications['Treatment Initiation']
Medications = Medications.drop('Date of first Dx', axis=1)

#-----------------Diagnosis for PMH-------------#Diag = 'Diagnosis.txt'
Diagnosis = open('Diagnosis.txt', 'r', encoding = 'utf8')
Diagnosis_text = Diagnosis.read()
Diagnosis_text = Diagnosis_text.encode('ascii', 'ignore').decode('ascii')

diagdict_gerd = defaultdict(list)
diagdict_ABPA = defaultdict(list)
diagdict_COPD = defaultdict(list)
diagdict_CF = defaultdict(list)
diagdict_BC = defaultdict(list)
diagdict_IBD = defaultdict(list)
diagdict_HIV = defaultdict(list)
diagdict_RA = defaultdict(list)
diadict_scoliosis = defaultdict(list)
diadict_pectus = defaultdict(list)
pattern_GERD = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((530.81|530.11|K21)(?:(?!\|).)*)')
pattern_ABPA = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((518.6|B44.81)(?:(?!\|).)*)')
pattern_COPD = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((492|496|J43|J44)(?:(?!\|).)*)')
pattern_CF = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((277.0|E84.0)(?:(?!\|).)*)')
pattern_BC = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((174|C50)(?:(?!\|).)*)')
pattern_IBD = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((555|556|K50|K51)(?:(?!\|).)*)')
pattern_HIV = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((042|B20)(?:(?!\|).)*)')
pattern_RA = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((714|M05|M06)(?:(?!\|).)*)')
pattern_scoliosis = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((737.30|M41)(?:(?!\|).)*)')
pattern_pectus = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((754.81|Q67.6)(?:(?!\|).)*)')
pattern_NTB = re.compile(r'(\S+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)\|((?:(?!\|).)*)\|(ICD9|ICD10)\|((A31\.2|A31\.0|a31\.2|a31\.0|031\.0|031\.2|31\.0|31\.2|03120|03122|310|312)(?:(?!\|).)*)')
ICD_values = []
ICD_date = []
ICD_EMPI = []
ICD_Index = []
NTB  = pattern_NTB.findall(Diagnosis_text)
GERD = pattern_GERD.findall(Diagnosis_text)
ABPA = pattern_ABPA.findall(Diagnosis_text)
COPD = pattern_COPD.findall(Diagnosis_text)
CF = pattern_CF.findall(Diagnosis_text)
BC = pattern_BC.findall(Diagnosis_text)
IBD = pattern_IBD.findall(Diagnosis_text)
HIV = pattern_HIV.findall(Diagnosis_text)
RA = pattern_RA.findall(Diagnosis_text)
Scoliosis = pattern_scoliosis.findall(Diagnosis_text)
Pectus = pattern_pectus.findall(Diagnosis_text)
for Pectus_match in Pectus:
    diadict_pectus[Pectus_match[0]] = Pectus_match[4]
for Scoliosis_match in Scoliosis:
    diadict_scoliosis[Scoliosis_match[0]] = Scoliosis_match[4]
for GERD_match in GERD:
    diagdict_gerd[GERD_match[0]] = GERD_match[4]
for ABPA_match in ABPA:
    diagdict_ABPA[ABPA_match[0]] = ABPA_match[4]
for COPD_match in COPD:
    diagdict_COPD[COPD_match[0]] = COPD_match[4]
for CF_match in CF:
    diagdict_CF[CF_match[0]] = CF_match[4]
for BC_match in BC:
    diagdict_BC[BC_match[0]] = BC_match[4]
for IBD_match in IBD:
    diagdict_IBD[IBD_match[0]] = IBD_match[4]
for HIV_match in HIV:
    diagdict_HIV[HIV_match[0]] = HIV_match[4]
for RA_match in RA:
    diagdict_RA[RA_match[0]] = RA_match[4]
for BC_match in BC:
    diagdict_BC[BC_match[0]] = BC_match[4]
for NTB_match in NTB:
    ICD_EMPI.append(NTB_match[0])
    ICD_date.append(NTB_match[3])
    ICD_values.append(NTB_match[6])
    ICD_Index.append(NTB_match[0])

#
# NTB_diagnosis = pd.DataFrame({'Date of first Dx':ICD_date, 'ICD Code':ICD_values, 'Index':ICD_Index}, index=[ICD_EMPI])
# NTB_diagnosis.index.name = 'EMPI'
# NTB_diagnosis['Date of first Dx'] = pd.to_datetime(NTB_diagnosis['Date of first Dx'])
# NTB_diagnosis_gb = NTB_diagnosis.groupby(['Index'])
# NTB_diagnosis_mindate = NTB_diagnosis_gb.agg({'Date of first Dx':np.min})


#####Making .pickle file for date of first diagnosis
# NTB_diagnosis_mindate_pickle = open('NTB_diagnosis_mindate.pickle', 'wb')
# pickle.dump(NTB_diagnosis_mindate, NTB_diagnosis_mindate_pickle)
# NTB_diagnosis_mindate_pickle.close()
# NTB_diagnosis_mindate_pickle_in = open('NTB_diagnosis_mindate.pickle','rb')
# NTB_diagnosis_mindate = pickle.load(NTB_diagnosis_mindate_pickle_in)
# Merged['Date of first Dx'] = Merged['Date of first Dx'].fillna(0)
#
# def func(c):
#     if c['Date of first Dx'] ==0:
#         return c['Date of First Pos Cx']
#     else:
#         return c['Date of first Dx']
# Merged['Date of first Dx'] = Merged.apply(func, axis=1)
# NTB_diagnosis_mindate = Merged['Date of first Dx']
#

Pectus = pd.Series(diadict_pectus)
Pectus = pd.DataFrame(Pectus, columns = ['Pectus Excavatum'])
Scoliosis = pd.Series(diadict_scoliosis)
Scoliosis = pd.DataFrame(Scoliosis, columns = ['Scoliosis'])
GERD = pd.Series(diagdict_gerd)
GERD = pd.DataFrame(GERD, columns = ['GERD'])
ABPA = pd.Series(diagdict_ABPA)
ABPA = pd.DataFrame(ABPA, columns = ['Allergic Bronchopulmonary Aspergillosis'])
COPD = pd.Series(diagdict_COPD)
COPD = pd.DataFrame(COPD, columns = ['COPD'])
CF = pd.Series(diagdict_CF)
CF = pd.DataFrame(CF, columns = ['Cystic Fibrosis'])
HIV = pd.Series(diagdict_HIV)
HIV = pd.DataFrame(HIV, columns = ['HIV'])
RA = pd.Series(diagdict_RA)
RA = pd.DataFrame(RA, columns = ['Rheumatoid arthritis'])
BC = pd.Series(diagdict_BC)
BC = pd.DataFrame(BC, columns = ['Breast Cancer'])
IBD = pd.Series(diagdict_IBD)
IBD = pd.DataFrame(IBD, columns = ['IBD'])
Diagnosis = GERD.join(ABPA, how='outer')
Diagnosis = Diagnosis.join(COPD, how='outer')
Diagnosis = Diagnosis.join(CF, how='outer')
Diagnosis = Diagnosis.join(HIV, how='outer')
Diagnosis = Diagnosis.join(RA, how='outer')
Diagnosis = Diagnosis.join(BC, how='outer')
Diagnosis = Diagnosis.join(IBD, how='outer')
Diagnosis = Diagnosis.join(Scoliosis, how='outer')
Diagnosis = Diagnosis.join(Pectus, how='outer')
#Recode PMH specific with history present
Present = re.compile(r'^(?!NaN).*$')
Diagnosis = Diagnosis.replace(Present, 'Present')


#######Making .pickle file for date of diagnosis dataframes
#Pickling Diagnosis table
# Diagnosis_pickle = open('Diagnosis.pickle', 'wb')
# pickle.dump(Diagnosis, Diagnosis_pickle)
# Diagnosis_pickle.close()
Diagnosis_pickle_in = open('Diagnosis.pickle','rb')
Diagnosis = pickle.load(Diagnosis_pickle_in)

# Diagnosis = Diagnosis.join(MVP, how='outer')
Diagnosis = open('Diagnosis.txt', 'r', encoding = 'utf8')
Diagnosis_text = Diagnosis.read()
Diagnosis_text = Diagnosis_text.encode('ascii', 'ignore').decode('ascii')



#------------Last date of follow---#
index = []
date = []
date_all = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|(\d+\/\d+\/\d+)')
match = date_all.findall(Diagnosis_text)

for matches in match:
    index.append(matches[0])
    date.append(matches[3])
Follow = pd.DataFrame({'Last Date':date, 'Index':index})
Follow = Follow.groupby('Index')
Follow = Follow['Last Date'].max()
Follow = pd.DataFrame(Follow)
Follow['Last Date'] = pd.to_datetime(Follow['Last Date'])
Diagnosis_pickle_in = open('Diagnosis.pickle','rb')
Diagnosis = pickle.load(Diagnosis_pickle_in)
#-------------------BMI, Weight, Smoking Status---------------#
HH = 'Health History.txt'
Health_hist = open(HH, 'r')
Health_hist_text = Health_hist.read()


pattern_bmi = re.compile(r'(\d+)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|(\d+\/\d+\/\d+)\|(BMI)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|')
pattern_smoking = re.compile(r'(\d+)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|(\d+\/\d+\/\d+)\|((Smok|Tob)((?:(?!\|).)*))\|(?!LMR\|4082)')
pattern_smoking1 = re.compile(r'(\d+)\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|(\d+\/\d+\/\d+)\|((Smok|Tob)((?:(?!\|).)*))\|LMR\|4082\|((?:(?!\|).)*)')
pattern_weight = re.compile(r'(\d+)\|(MGH|BWH|((?:(?!\|).)*))\|(\d+|((?:(?!\|).)*))\|(\d+\/\d+\/\d+)\|(Weight)\|\w+\|\w+\|((\d+\.\d+)|(\d+))\|(\w+)')

BMI_matches = pattern_bmi.findall(Health_hist_text)
Smoking_matches = pattern_smoking.findall(Health_hist_text)
Smoking_matches1 = pattern_smoking1.findall(Health_hist_text)
weight_matches = pattern_weight.findall(Health_hist_text)

weight_values = []
date_weight = []
EMPI_weight = []
BMI_values = []
date_BMI = []
EMPI_BMI = []
Smoking_values = []
date_smoking = []
EMPI_smoking = []

for match_weight in weight_matches:
    EMPI_weight.append(match_weight[0])
    date_weight.append(match_weight[5])
    weight_values.append(match_weight[7])
Weight = pd.DataFrame({'Date':date_weight, 'Weight':weight_values, 'Index':EMPI_weight})
Weight = Weight.set_index('Index')
Weight['Date'] = pd.to_datetime(Weight['Date'])
Weight = Weight.join(NTB_diagnosis_mindate, how='outer')
Weight = Weight.dropna(subset=['Date of first Dx', 'Weight'])
Weight['Difference Baseline'] = ((Weight['Date'] - Weight['Date of first Dx']).dt.days)
Weight = Weight.reset_index()
Weight = Weight.loc[Weight['Weight'] != '']
Weight_baseline = Weight.loc[(Weight['Difference Baseline'] <= 365) & (Weight['Difference Baseline'] >=-730)]
Weight_baseline = Weight_baseline.loc[Weight_baseline.groupby(['Index'])['Difference Baseline'].idxmin()].set_index(['Index'])
Weight_baseline = Weight_baseline['Weight']
Weight_baseline = pd.DataFrame(Weight_baseline)
Weight_baseline.columns = ['Weight Baseline']


Weight = Weight.set_index('Index')
Weight['Follow-up Date'] = Medications['Follow-up Date']
Weight = Weight.reset_index()
Weight['Difference Follow-up'] = ((Weight['Date'] - Weight['Follow-up Date']).dt.days)
Weight_follow_up = Weight.loc[(Weight['Difference Follow-up'] >= 730)]
Weight_follow_up = Weight_follow_up.loc[Weight_follow_up.groupby(['Index'])['Difference Follow-up'].idxmin()].set_index(['Index'])
Weight_follow_up = Weight_follow_up['Weight']
Weight_follow_up = pd.DataFrame(Weight_follow_up)
Weight_follow_up.columns = ['Weight Follow-up']
Weight_follow_up
for match_smoke in Smoking_matches:
    EMPI_smoking.append(match_smoke[0])
    date_smoking.append(match_smoke[3])
    Smoking_values.append(match_smoke[4])
for match_smoke1 in Smoking_matches1:
    EMPI_smoking.append(match_smoke1[0])
    date_smoking.append(match_smoke1[3])
    Smoking_values.append(match_smoke1[7])

Smoking_df = pd.DataFrame({'Date':date_smoking, 'Smoking Status':Smoking_values, 'Index':EMPI_smoking})
Smoking_df['Date'] = pd.to_datetime(Smoking_df['Date'])
Smoking_recent = Smoking_df.loc[Smoking_df.groupby(['Index'])['Date'].idxmax()].set_index(['Index'])
Smoking_recent['Smoking Status'] = Smoking_recent['Smoking Status'].str.replace(r'(?i)^.*(never|no).*$', 'Never smoker')
Smoking_recent['Smoking Status'] = Smoking_recent['Smoking Status'].str.replace(r'(?i)^.*(Unknown).*$', 'Unknown')
Smoking_recent['Smoking Status'] = Smoking_recent['Smoking Status'].str.replace(r'(?i)^.*(former|quit|current|previous|ppd|current|pk|\d+|ppd|toba|history|cigar|start).*$', 'History of Smoking')
Smoking_recent['Smoking Status'] = Smoking_recent['Smoking Status'].str.replace(r'^.*(Smoker).*$', 'History of Smoking')
#Smoking_recent.to_csv('/Volumes/homedir$/MAC Project/Complete Project//smoking.csv')

for match_bmi in BMI_matches:
    EMPI_BMI.append(match_bmi[0])
    date_BMI.append(match_bmi[3])
    BMI_values.append(match_bmi[7])

BMI = pd.DataFrame({'Date':date_BMI, 'BMI':BMI_values, 'Index': EMPI_BMI})
BMI['Date'] = pd.to_datetime(BMI['Date'])
BMI = BMI.set_index('Index')
BMI = BMI.join(NTB_diagnosis_mindate, how='outer')
BMI = BMI.dropna(subset=['Date of first Dx', 'BMI'])
BMI['Difference Baseline'] = ((BMI['Date'] - BMI['Date of first Dx']).dt.days)
BMI = BMI.reset_index()
BMI = BMI.loc[BMI['BMI'] != '']
BMI_baseline = BMI.loc[(BMI['Difference Baseline'] <= 365) & (BMI['Difference Baseline'] >=-730)]
BMI_baseline = BMI_baseline.loc[BMI_baseline.groupby(['Index'])['Difference Baseline'].idxmin()].set_index(['Index'])

BMI = BMI.set_index('Index')
BMI['Follow-up Date'] = Medications['Follow-up Date']
BMI = BMI.reset_index()
BMI['Difference Follow-up'] = ((BMI['Date'] - BMI['Follow-up Date']).dt.days)
BMI_followup = BMI.loc[(BMI['Difference Follow-up'] >= 730)]
BMI_followup = BMI_followup.loc[BMI_followup.groupby(['Index'])['Difference Follow-up'].idxmin()].set_index(['Index'])
BMI_followup
#BMI.to_csv('/Volumes/homedir$/MAC Project/Complete Project//temp.csv')
#-------------------Pulmonary Extract---------------#


pattern_MGH1 = re.compile(r'FEV1\s+\S+\s+\d+.\d+\s+\d+\.\d+\s+(\d+).+(?:\n|\r\n?)FVC\s+\S+\s+\d.\d+\s+\d+\.\d+\s+(\d+).+(?:\n|\r\n?)FEV1/FVC\s+\S+\s+\d+\s+\d+\s+(\S+).+[\s\S]+')
pattern_MGH2 = re.compile(r'FEV!\s+\S+\s+\d+\.\d+\s+\d+\.\d+\s+\S+\s+\S+\s+(\d+).+(?:\n|\r\n?)FVC\s+\S+\s+\d+\.\d+\s+\d+\.\d+\s+\S+\s+\S+\s+(\d+).+(?:\n|\r\n?)FEV!\s+\/\s+FVC\s+\S+\s+\d+\s+\d+\s\S+\s+\S+\s+(\S+)[\s\S]+')
pattern_MGH3 = re.compile(r'First\sSec\sVC\s\S+\s+\S+\s+\S+\s+(\d+).+(?:\n|\r\n?)Vital\sCapacity\s\S+\s+\S+\s+\S+\s+(\S+).+(?:\n|\r\n?)FEV1\/VC\s+%\s+\d+\s+\d+\s+(\S+)')
pattern_MGH4 = re.compile(r'')
pattern_MGH5 = re.compile(r'FVC\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+).+(?:\n|\r\n?)FEV1\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+).+(?:\n|\r\n?)FEV1\/FVC\s+%\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+).+')
pattern_BWH1 = re.compile(r'FEV!\s+\S+\s+\d+\.\S+\s+\S+\.\S+\s+\d+\.\d+\s+\S+\s+(\d+).+(?:\n|\r\n?)FVC\s+\S+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\S+\s+(\d+).+(?:\n|\r\n?)FEV!\s+\/\s+FVC\s+\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)[\s\S]+')
pattern_BWH2 = re.compile(r'FEV1\s+\S+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+(\d+).+(?:\n|\r\n?)FVC\s+\S+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+(\d+).+(?:\n|\r\n?)FEV1\/FVC\s+\S+\s+\d+\s+\d+\s+\d+\s+(\d+)[\s\S+]')


EMPI = []
Date = []
FEV1 = []
FVC = []
FEV1FVC = []


for report_pulm in MedicalReport('Pulmonary.txt', end='[report_end]'):
    if report_pulm['MRN_Type'] == 'MGH':
        if re.search(pattern_MGH1, report_pulm['Report_Text']):
            for match in pattern_MGH1.findall(report_pulm['Report_Text']):
                FEV1.append(match[0])
                FVC.append(match[1])
                FEV1FVC.append(match[2])
            Date.append(report_pulm['Report_Date_Time'])
            EMPI.append(report_pulm['EMPI'])
        elif re.search(pattern_MGH2,report_pulm['Report_Text']):
            for match in pattern_MGH2.findall(report_pulm['Report_Text']):
                FEV1.append(match[0])
                FVC.append(match[1])
                FEV1FVC.append(match[2])
            Date.append(report_pulm['Report_Date_Time'])
            EMPI.append(report_pulm['EMPI'])
        elif re.search(pattern_MGH3,report_pulm['Report_Text']):
            for match in pattern_MGH3.findall(report_pulm['Report_Text']):
                FEV1.append(match[0])
                FVC.append(match[1])
                FEV1FVC.append(match[2])
            Date.append(report_pulm['Report_Date_Time'])
            EMPI.append(report_pulm['EMPI'])
        # elif re.search(pattern_MGH4,report_pulm['Report_Text']):
        #     for match in pattern_MGH4.findall(report_pulm['Report_Text']):
        #         FEV1.append(match[0])
        #         FVC.append(match[1])
        #         FEV1FVC.append(match[2])
        #     Date.append(report_pulm['Report_Date_Time'])
        #     EMPI.append(report_pulm['EMPI'])
        elif re.search(pattern_MGH5,report_pulm['Report_Text']):
            for match in pattern_MGH5.findall(report_pulm['Report_Text']):
                FEV1.append(match[1])
                FVC.append(match[0])
                FEV1FVC.append(match[2])
            Date.append(report_pulm['Report_Date_Time'])
            EMPI.append(report_pulm['EMPI'])
        else:
            print(report_pulm['Report_Text'])
            print('huh?')
    elif report_pulm['MRN_Type'] == 'BWH':
        if re.search(pattern_BWH1, report_pulm['Report_Text']):
            for match in pattern_BWH1.findall(report_pulm['Report_Text']):
                FEV1.append(match[0])
                FVC.append(match[1])
                FEV1FVC.append(match[2])
            Date.append(report_pulm['Report_Date_Time'])
            EMPI.append(report_pulm['EMPI'])
        elif re.search(pattern_BWH2,report_pulm['Report_Text']):
            for match in pattern_BWH2.findall(report_pulm['Report_Text']):
                FEV1.append(match[0])
                FVC.append(match[1])
                FEV1FVC.append(match[2])
            Date.append(report_pulm['Report_Date_Time'])
            EMPI.append(report_pulm['EMPI'])


PFTs_combined = pd.DataFrame({'Date':Date, '% Predicted FEV1':FEV1, '% Predicted FVC':FVC, '% Predicted FEV1/FVC':FEV1FVC, 'Index':EMPI})
PFTs_combined['Date'] = pd.to_datetime(PFTs_combined['Date'])
PFTs_combined['Index'] = PFTs_combined['Index'].str.extract(r'(\d+)', expand=True)
PFTs_combined = PFTs_combined.drop_duplicates(subset=['Date', 'Index'], keep = 'first')
PFTs_combined = PFTs_combined.set_index('Index')
PFTs_combined['% Predicted FEV1/FVC'] = PFTs_combined['% Predicted FEV1/FVC'].str.replace(r'\-+', '')
PFTs_combined[['% Predicted FEV1', '% Predicted FVC']] = PFTs_combined[['% Predicted FEV1', '% Predicted FVC']].astype(float).fillna(0.0)
def func(c):
    if c['% Predicted FEV1/FVC'] is '':
        return ((c['% Predicted FEV1']/c['% Predicted FVC'])*100)
    else:
        return c['% Predicted FEV1/FVC']
PFTs_combined['% Predicted FEV1/FVC'] = PFTs_combined.apply(func, axis=1)
PFTs_combined[['% Predicted FEV1/FVC', '% Predicted FEV1', '% Predicted FVC']] = PFTs_combined[['% Predicted FEV1/FVC', '% Predicted FEV1', '% Predicted FVC']].astype(int)
PFTs_combined
#Baseline PFTs
PFTsDxDate = NTB_diagnosis_mindate.join(PFTs_combined, how='outer')
PFTsDxDate['Difference'] = ((PFTsDxDate['Date'] - PFTsDxDate['Date of first Dx']).dt.days)
PFTs_baseline_temp = PFTsDxDate.loc[(PFTsDxDate['Difference'] <= 365) & (PFTsDxDate['Difference'] >= -730)]
PFTs_baseline_temp = PFTs_baseline_temp.reset_index()
PFTs_baseline = PFTs_baseline_temp.loc[PFTs_baseline_temp.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
PFTs_baseline = PFTs_baseline.drop(['Date of first Dx','Difference'], axis=1)


#Follow-up PFTs
PFTsDxDate1 = PFTs_combined
PFTsDxDate1['Follow-up Date'] = Medications['Follow-up Date']
PFTsDxDate1['Difference'] = ((PFTsDxDate1['Date'] - PFTsDxDate1['Follow-up Date']).dt.days)
PFTs_followup_temp = PFTsDxDate1.loc[(PFTsDxDate1['Difference'] >= 730)]
PFTs_followup_temp = PFTs_followup_temp.reset_index()
PFTs_followup = PFTs_followup_temp.loc[PFTs_followup_temp.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
PFTs_followup = PFTs_followup.drop(['Follow-up Date','Difference'], axis=1)
PFTs_baseline.rename(columns={'Date': 'Baseline PFTs Date', '% Predicted FEV1':'Baseline % Predicted FEV1', '% Predicted FVC':'Baseline % Predicted FVC', '% Predicted FEV1/FVC':'Baseline% Predicted FEV1/FVC'}, inplace=True)
PFTs_followup.rename(columns={'Date': 'Follow-up PFTs Date','% Predicted FEV1':'Follow-up % Predicted FEV1', '% Predicted FVC':'Follow-up % Predicted FVC', '% Predicted FEV1/FVC':'Follow-up % Predicted FEV1/FVC'}, inplace=True)

PFTs_combined = PFTs_baseline.join(PFTs_followup, how='outer')
PFTs_combined
# PFTs_combined.to_csv('/Volumes/homedir$/MAC Project/Complete Project//PFTs_combined.csv')
# PFTs_followup.to_csv('/Volumes/homedir$/MAC Project/Complete Project//PFTs_followup.csv')

EMPI = []
Height = []

pattern_height = re.compile(r'(?i)height.*?(\d\d|weight)')
pattern_height1 = re.compile(r'(?i)(\d\d)\sin')
for report_pulm in MedicalReport('Pulmonary.txt', end='[report_end]'):
    if re.search(pattern_height, report_pulm['Report_Text']):
        for match in pattern_height.findall(report_pulm['Report_Text']):
            Height.append(match)
            EMPI.append(report_pulm['EMPI'])
    elif re.search(pattern_height1, report_pulm['Report_Text']):
        for match in pattern_height1.findall(report_pulm['Report_Text']):
            Height.append(match)
            EMPI.append(report_pulm['EMPI'])


Height_df = pd.DataFrame({'Index': EMPI, 'Height': Height})
Height_df['Index'] = Height_df['Index'].str.extract(r'(\d+)')
Height_df['Height'] = Height_df['Height'].str.extract(r'(\d+)')
Height_df = Height_df.drop_duplicates(subset = 'Index', keep='first').set_index('Index')
Height_df = pd.DataFrame(Height_df)
Height_df = Height_df.join(Weight_follow_up, how='outer')
Height_df = Height_df.join(Weight_baseline, how='outer')
Height_df = Height_df[['Weight Baseline', 'Weight Follow-up', 'Height']].astype(float)
# Height_df = Height_df.fillna(0)

Height_df['Calulated BMI Baseline'] = Height_df['Weight Baseline']/(Height_df['Height'] *Height_df['Height']) * 703.00
Height_df['Calulated BMI Follow-up'] = Height_df['Weight Follow-up']/(Height_df['Height'] *Height_df['Height']) * 703.00
Height_df
#----------------Microbiologic Data Extraction--------#
#EMPI|MRN_Type|MRN|Microbiology_Number|Microbiology_Date_Time|Specimen_Type|Specimen_Comments|Test_Name|Test_Code|Test_Comments|Test_Status|Organism_Name|Organism_Code|Organism_Comment|Organism_Text
# for report_micro in MedicalReport('Micro.txt', end='[report_end]'):
#     if re.search(r'3682\sM',report_micro['Organism_Text']):
#         if re.search(r'', report_micro['Organism_Name'])
#         Micro_EPMI
#         Micro_Date_pos = []
#         Micro_species = []
#         Micro_sens = []
#         Micro_cx_source = []
#         Micro_comments = []

mic = 'Micro.txt'
micro = open(mic, 'r')
micro_text = micro.read()
micro.close()

#Positive Cultures
pattern_micro_pos = re.compile(r'(\d+)\|(?:(?!\|).)*\|(?:(?!\|).)*\|(?:(?!\|).)*\|(?:(?!\|).)*\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|.*(?:\n|\r\n?).*(?:\n|\r\n?).*(?:\n|\r\n?).*Date:\s(\d+\/\d+\/\d+)\s(\d+:\d+:\d+)(?:\n|\r\n?)Patient:\s(MGH|BWH):(\d+)(?:\n|\r\n?)Specimen\sType:\s+(BRONCHIAL.*|SPUTUM.*|.*)(?:\n|\r\n?).*(?:\n|\r\n?)Reported.*(?:\n|\r\n?)Test Name.*(?:\n|\r\n?)Organism Name:\s(My\S+\s+[^Tt].*|MY\S+\s+[^Tt].*)(?:\n|\r\n?)Organism Comment.*(?:\n|\r\n?)Susceptibility:([\s\S]+?)Others')
matches_micro_pos = pattern_micro_pos.findall(micro_text)

Micro_EPMI_pos = []
Micro_Date_pos = []
Micro_species = []
Micro_sens = []
Micro_cx_source = []
Micro_comments = []

for match_micro_pos in matches_micro_pos:
    Micro_EPMI_pos.append(match_micro_pos[0])
    Micro_Date_pos.append(match_micro_pos[3])
    Micro_species.append(match_micro_pos[8])
    Micro_sens.append(match_micro_pos[9])
    Micro_cx_source.append(match_micro_pos[1])
    Micro_comments.append(match_micro_pos[2])

Micro_pos_inclusion = pd.DataFrame({'Cx Date':Micro_Date_pos, 'Species':Micro_species, 'Culture Source':Micro_cx_source, 'Index':Micro_EPMI_pos})
Micro_all_pos = Micro_pos_inclusion
Micro_all_pos['Culture'] = 'Culture'
Micro_pos_inclusion['Cx Date'] = pd.to_datetime(Micro_pos_inclusion['Cx Date'])
Micro_pos_inclusion['Species'] =  Micro_pos_inclusion['Species'].str.replace(r'(My\S+\s+[^Tt].*|MY\S+\s+[^Tt].*)', 'Positive Mycobacterial Cx')
Micro_pos_inclusion['Culture Source'] =  Micro_pos_inclusion['Culture Source'].str.replace(r'(^.*SPUTUM.*)', 'SPUTUM')
Micro_pos_inclusion['Culture Source'] =  Micro_pos_inclusion['Culture Source'].str.replace(r'(^.*BRONCHIAL.*|^.*WASH.*)', 'BAL')
def func(c):
    if c['Culture Source'] is 'SPUTUM':
        return c['Culture Source']
    elif c['Culture Source'] is 'BAL':
        return c['Culture Source']
    else:
        return 'Tissue Source'
Micro_pos_inclusion['Culture Source'] = Micro_pos_inclusion.apply(func, axis=1)
Micro_pos_inclusion = Micro_pos_inclusion.astype({'Culture Source':'category', 'Species':'category'})
Micro_pos_inclusion['Cx Date'] = pd.to_datetime(Micro_pos_inclusion['Cx Date'])
Micro_pos_inclusion = Micro_pos_inclusion.groupby(['Index'])
Micro_pos_inclusion = Micro_pos_inclusion['Culture Source'].value_counts()
Micro_pos_inclusion = pd.DataFrame(Micro_pos_inclusion)
Micro_pos_inclusion = Micro_pos_inclusion.unstack()
Micro_pos_inclusion = Micro_pos_inclusion.rename(columns= {'Culture Source' : 'Counts'})
Micro_pos_inclusion.columns = [' '.join(col).strip() for col in Micro_pos_inclusion.columns.values]


##All cultures for macrolide

Micro_all_pos['Cx Date'] = pd.to_datetime(Micro_all_pos['Cx Date'])
Micro_all_pos['Cx Date'] = Micro_all_pos['Cx Date'].dt.year
Micro_all_pos =  Micro_all_pos.drop_duplicates(['Index', 'Cx Date', 'Culture'], keep='first')
def func(c):
    if 'Abscessus'  in c['Species'] or 'abscessus' in c['Species'] or 'ABSCESSUS' in c['Species']:
        return 'M. Abscessus'
    elif 'Avium'  in c['Species'] or 'avium' in c['Species'] or 'AVIUM' in c['Species']:
        return 'MAC'
    else:
        return 'Other Species'
Micro_all_pos['Species']= Micro_all_pos.apply(func,axis=1)


#Micro_all_pos = Micro_all_pos.loc[Micro_all_pos['Species'] == 'M. Abscessus']
Micro_all_pos = Micro_all_pos.drop('Species', axis=1)
Micro_all_pos = Micro_all_pos.groupby(['Cx Date','Index', 'Culture'])
Micro_all_pos_gb = pd.DataFrame(Micro_all_pos.size())
Micro_all_pos_gb = Micro_all_pos_gb.groupby(['Cx Date','Culture'])
Micro_all_pos_gb = pd.DataFrame(Micro_all_pos_gb.size())
Micro_all_pos_gb = Micro_all_pos_gb.unstack()
Micro_all_pos_gb = Micro_all_pos_gb.rename(columns= {0 : '# Patients with culture in given year'})
Micro_all_pos_gb.columns = [' '.join(col).strip() for col in Micro_all_pos_gb.columns.values]
Micro_all_pos_gb = Micro_all_pos_gb.reset_index()
Micro_all_pos_gb = pd.DataFrame(Micro_all_pos_gb)
Micro_all_pos_gb = Micro_all_pos_gb.rename(columns= {'# Patients with culture in given year Culture' : '# Patients with culture in given year'})
Micro_all_pos_gb = Micro_all_pos_gb.rename(columns= {'Cx Date': 'year'})
Micro_all_pos_gb = Micro_all_pos_gb.set_index('year')
Micro_all_pos_gb
#Most Recent Positive
Micro_pos_recent = pd.DataFrame({'Cx Date':Micro_Date_pos, 'Species':Micro_species, 'Culture Source':Micro_cx_source, 'Index':Micro_EPMI_pos})
Micro_pos_recent['Cx Date'] = pd.to_datetime(Micro_pos_recent['Cx Date'])
Micro_pos_recent = Micro_pos_recent.set_index('Index')
Micro_pos_recent['Treatment Initiation']= Medications['Treatment Initiation']
Micro_pos_recent['Treatment Initiation'] = pd.to_datetime(Micro_pos_recent['Treatment Initiation'])
Micro_pos_recent['Treatment Initiation'] =Micro_pos_recent['Treatment Initiation'].astype(str)
Micro_pos_recent = Micro_pos_recent.loc[(Micro_pos_recent['Treatment Initiation'] != 'NaT')]
Micro_pos_recent['Treatment Initiation'] = pd.to_datetime(Micro_pos_recent['Treatment Initiation'])
Micro_pos_recent['Difference'] = Micro_pos_recent['Treatment Initiation'] - Micro_pos_recent['Cx Date']
Micro_pos_recent['Difference'] = Micro_pos_recent['Difference'].astype(str)
Micro_pos_recent['Difference'] = Micro_pos_recent['Difference'].str.extract(r'(\-\d+|\d+)')
Micro_pos_recent['Difference'] = Micro_pos_recent['Difference'].astype(int)
Micro_pos_recent = Micro_pos_recent.loc[(Micro_pos_recent['Difference'] <= 0)&(Micro_pos_recent['Difference'] >= -730)]
Micro_pos_recent_gb = Micro_pos_recent.groupby('Index')
Micro_recent_pos_cx = Micro_pos_recent_gb.agg({'Cx Date':np.max})
Micro_recent_pos_cx = Micro_recent_pos_cx.rename(columns= {'Cx Date': 'Date of Most Recent Pos Cx'})

#Date of first Positive Cultures
Micro_first_pos_cx = Micro_pos_recent_gb.agg({'Cx Date':np.min})

#All SPUTUM and BAL Cutlures test done
pattern_allcx = re.compile(r'Date:\s(\d+\/\d+\/\d+)\s(\d+:\d+:\d+)(?:\n|\r\n?)Patient:\s(MGH|BWH):(\d+)(?:\n|\r\n?)Specimen\sType:\s+(BRONCHIAL.*|SPUTUM.*)(?:\n|\r\n?).*(?:\n|\r\n?)Reported.*(?:\n|\r\n?)Test Name.*(?:\n|\r\n?)Organism Name:\s+.*(?:\n|\r\n?)Organism Comment.*(?:\n|\r\n?)Susceptibility:([\s\S]+?)Others.*(?:\n|\r\n?).*(?:\n|\r\n?).*(?:\n|\r\n?).*(3682.*)')

Microall_EPMI = []
Microall_Date = []
Microall_cx = []


for report_micro in MedicalReport('Micro.txt', end='[report_end]'):
    for match_microall in pattern_allcx.findall(report_micro['Organism_Text']):
        Microall_EPMI.append(report_micro['EMPI'])
        Microall_Date.append(match_microall[0])
        Microall_cx.append(match_microall[6])


micro_total_cx = pd.DataFrame({'Index':Microall_EPMI, 'Culture':Microall_cx})
micro_total_cx['Index'] = micro_total_cx['Index'].str.extract(r'(\d+)')
micro_total_cx = micro_total_cx.groupby(micro_total_cx['Index'])
micro_total_cx = micro_total_cx['Culture'].value_counts()
micro_total_cx = pd.DataFrame(micro_total_cx)
micro_total_cx = micro_total_cx.unstack()
micro_total_cx.columns = [' '.join(col).strip() for col in micro_total_cx.columns.values]
micro_total_cx.rename(columns = {micro_total_cx.columns[0]: '# of Cxs sent'}, inplace = True)


#All cultures of any type
pattern_allcx = re.compile(r'Date:\s(\d+\/\d+\/\d+)\s(\d+:\d+:\d+)(?:\n|\r\n?)Patient:\s(MGH|BWH):(\d+)(?:\n|\r\n?)Specimen\sType:\s+(.*)(?:\n|\r\n?).*(?:\n|\r\n?)Reported.*(?:\n|\r\n?)Test Name.*(?:\n|\r\n?)Organism Name:\s+.*(?:\n|\r\n?)Organism Comment.*(?:\n|\r\n?)Susceptibility:([\s\S]+?)Others.*(?:\n|\r\n?).*(?:\n|\r\n?).*(?:\n|\r\n?).*(3682.*)')

Microall_EPMI = []
Microall_Date = []
Microall_cx = []
Microall_EPMI

for report_micro in MedicalReport('Micro.txt', end='[report_end]'):
    for match_microall in pattern_allcx.findall(report_micro['Organism_Text']):
        Microall_EPMI.append(report_micro['EMPI'])
        Microall_Date.append(match_microall[0])
        Microall_cx.append(match_microall[6])

micro_total_cx_full = pd.DataFrame({'Index':Microall_EPMI, 'Culture':Microall_cx})
micro_total_cx_full['Index'] = micro_total_cx_full['Index'].str.extract(r'(\d+)')
micro_total_cx_full = micro_total_cx_full.groupby(micro_total_cx_full['Index'])
micro_total_cx_full = micro_total_cx_full['Culture'].value_counts()
micro_total_cx_full = pd.DataFrame(micro_total_cx_full)
micro_total_cx_full = micro_total_cx_full.unstack()
micro_total_cx_full.columns = [' '.join(col).strip() for col in micro_total_cx_full.columns.values]
micro_total_cx_full.rename(columns = {micro_total_cx_full.columns[0]: '# of Cxs sent'}, inplace = True)
micro_total_cx_full

#Number of negative cultures after most recent positive Cxs within 2 years

micro_all_df = pd.DataFrame({'Index':Microall_EPMI, 'Date':Microall_Date, 'Culture':Microall_cx})
micro_all_df['Date'] = pd.to_datetime(micro_all_df['Date'])
micro_all_df['Index'] = micro_all_df['Index'].str.extract(r'(\d+)')
micro_all_df = micro_all_df.set_index('Index')
micro_all_df['Treatment Initiation'] = Medications['Treatment Initiation']
micro_all_df = micro_all_df.join(Micro_recent_pos_cx, how='outer')
micro_all_df['Treatment Initiation'] = micro_all_df['Treatment Initiation'].astype(str)
micro_all_df = micro_all_df.loc[(micro_all_df['Treatment Initiation'] != 'NaT')]
micro_all_df['Treatment Initiation'] = pd.to_datetime(micro_all_df['Treatment Initiation'])
micro_all_df['Treatment Initiation'] = micro_all_df['Treatment Initiation'].dropna()
micro_all_df['Date of Most Recent Pos Cx'] = pd.to_datetime(micro_all_df['Date of Most Recent Pos Cx'] )
micro_all_df['Date of Most Recent Pos Cx'] = micro_all_df['Date of Most Recent Pos Cx'].fillna(datetime(1972,1,1))

def func(c):
    if c['Date of Most Recent Pos Cx'] == '1972-01-01':
        return c['Treatment Initiation']
    else:
        if c['Treatment Initiation'] > c['Date of Most Recent Pos Cx']:
            return c['Treatment Initiation']
        else:
            return c['Date of Most Recent Pos Cx']


micro_all_df['Reference Date'] = micro_all_df.apply(func, axis=1)


def func(c):
    if c['Date of Most Recent Pos Cx'] =='1972-01-01':
        return 'No Positive'
    else:
        if c['Treatment Initiation'] > c['Date of Most Recent Pos Cx']:
            return 'All Negative'
        elif c['Treatment Initiation'] < c['Date of Most Recent Pos Cx']:
            return 'At least 1 Positive'

micro_all_df['Cultures after Tx Initiation'] = micro_all_df.apply(func, axis=1)
micro_denominator = micro_all_df
Micro = micro_all_df['Cultures after Tx Initiation']
Micro = pd.DataFrame(Micro)
micro_all_df['Date of Most Recent Pos Cx'] = micro_all_df['Date of Most Recent Pos Cx'].replace(datetime(1972,1,1), np.nan)

micro_all_df['Difference'] = micro_all_df['Treatment Initiation'] -  micro_all_df['Date']
micro_all_df['Difference'] = micro_all_df['Difference'].astype(str)
micro_all_df['Difference'] = micro_all_df['Difference'].str.extract(r'(\-\d+|\d+)')
micro_all_df['Difference'] = micro_all_df['Difference'].astype(int)
micro_all_df = micro_all_df.loc[(micro_all_df['Difference'] <0)&(micro_all_df['Difference'] >= -730)]

#micro_all_df.to_csv('/Volumes/homedir$/MAC Project/Complete Project/temp.csv')
micro_denominator = micro_all_df


micro_all_df = micro_all_df.loc[(micro_all_df['Date'] > micro_all_df['Reference Date']) ]
micro_all_df  = micro_all_df.reset_index()
micro_all_df_gb = micro_all_df.groupby('Index')
micro_all_df_gb = micro_all_df_gb['Culture'].value_counts()
micro_all_df_gb = pd.DataFrame(micro_all_df_gb)
micro_all_df_gb = micro_all_df_gb.unstack()
micro_all_df_gb.columns = [' '.join(col).strip() for col in micro_all_df_gb.columns.values]
micro_all_df_gb.rename(columns = {micro_all_df_gb.columns[0]: 'Negative Cultures since Reference Date'}, inplace = True)


micro_denominator  = micro_denominator.reset_index()
micro_denominator_gb = micro_denominator.groupby('Index')
micro_denominator_gb = micro_denominator_gb['Culture'].value_counts()
micro_denominator_gb = pd.DataFrame(micro_denominator_gb)
micro_denominator_gb = micro_denominator_gb.unstack()
micro_denominator_gb.columns = [' '.join(col).strip() for col in micro_denominator_gb.columns.values]
micro_denominator_gb.rename(columns = {micro_denominator_gb.columns[0]: 'Number of cultures since treatment initiation'}, inplace = True)
Micro = Micro.reset_index().drop_duplicates('Index', keep='first').set_index('Index')

#Species of infection
species_list = []
species_empi = []
for match_micro_pos in matches_micro_pos:
    species_list.append(match_micro_pos[8])
    species_empi.append(match_micro_pos[0])
species = pd.DataFrame({'Species':species_list, 'Index':species_empi})
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+avi.*)', 'MAC')
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+ab.*)', 'M. Abscessus')
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+ka.*)', 'M. Kansasii')
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+intra.*)', 'MAC')
species['Species'] = species['Species'].str.replace(r'(?i)(^myco\S+\s+[^ak].*)', 'Other Species')

species_gb = species.groupby('Index')
species_gb = species_gb['Species'].value_counts()
species_gb = pd.DataFrame(species_gb)
species_gb.columns = [' '.join(col).strip() for col in species_gb.columns.values]
species_gb = species_gb.reset_index()
species_gb = species_gb.drop(['S p e c i e s'], axis=1)
species_gb = species_gb.groupby(['Index'])['Species'].apply(lambda x: ','.join(x.astype(str))).reset_index()
species_gb = species_gb.set_index('Index')
species_coinfection = species_gb
species_coinfection['Species'] = species_coinfection['Species'].astype(str)
species_coinfection = pd.DataFrame(species_coinfection)
species_gb['Species'] = species_gb['Species'].str.replace('(Other Species.{1})','')
species_gb['Species'] = species_gb['Species'].str.replace('(,Other Species)','')
species_gb['Species'] =  species_gb['Species'].fillna(0)
species_coinfection
def func(c):
    if 'MAC' in c['Species']:
        if 'Abscessus' in c['Species']:
            if 'Kansasii' in c['Species']:
                return 'M. Abscessus'
            else:
                return 'M. Abscessus'
        elif 'Kansasii' in c['Species']:
            return 'MAC'
        else:
            return 'MAC'
    elif 'Abscessus' in c['Species']:
        if 'Kansasii' in c['Species']:
            return 'M. Abscessus'
        else:
            return 'M. Abscessus'
    elif 'Kansasii' in c['Species']:
        return 'M. Kansasii'
    elif c['Species'] ==0:
        return 'Other Species'
    else:
        return 'Other Species'

species_gb['Species'] = species_gb.apply(func, axis=1)

####Coinfection
#Species of infection
species_list = []
species_empi = []
for match_micro_pos in matches_micro_pos:
    species_list.append(match_micro_pos[8])
    species_empi.append(match_micro_pos[0])
species = pd.DataFrame({'Species':species_list, 'Index':species_empi})
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+avi.*)', 'MAC')
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+ab.*)', 'M. Abscessus')
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+ka.*)', 'M. Kansasii')
species['Species'] = species['Species'].str.replace(r'(?i)(^mycobacter\S+\s+intra.*)', 'MAC')
species['Species'] = species['Species'].str.replace(r'(?i)(^myco\S+\s+[^ak].*)', 'Other Species')

Coinfection = species.groupby('Index')
Coinfection = Coinfection['Species'].value_counts()
Coinfection = pd.DataFrame(Coinfection)
Coinfection.columns = [' '.join(col).strip() for col in Coinfection.columns.values]
Coinfection = Coinfection.reset_index()
Coinfection = Coinfection.drop(['S p e c i e s'], axis=1)
Coinfection= Coinfection.groupby(['Index'])['Species'].apply(lambda x: ','.join(x.astype(str))).reset_index()
Coinfection = Coinfection.set_index('Index')

def func(c):
    if 'Other Species' in c['Species']:
        if 'Abscessus' in c['Species']:
            return 'Coinfection'
        elif 'Kansasii' in c['Species']:
            return 'Coinfection'
        elif 'MAC' in c['Species']:
            return 'Coinfection'
    elif 'MAC' in c['Species']:
        if 'Abscessus' in c['Species']:
            if 'Kansasii' in c['Species']:
                return 'Coinfection'
            else:
                return 'Coinfection'
        elif 'Kansasii' in c['Species']:
            return 'Coinfection'
        #else:
        #    return 'MAC'
    elif 'Abscessus' in c['Species']:
     if 'Kansasii' in c['Species']:
            return 'Coinfection'
        #else:
            #return 'M. Abscessus'
    #elif 'Kansasii' in c['Species']:
        #return 'Coinfection'
    #else:
        #return 'Other Species'
Coinfection['Coinfection'] = Coinfection.apply(func, axis=1)
Coinfection['Coinfection']
#Smears
pattern_micro_smear = re.compile(r'(\d+)\|(MGH|BWH)\|(\d+)\|((?:(?!\|).)*)\|(\d+\/\d+\/\d+)((?:(?!\|).)*)\|(BRONCHIAL(?:(?!\|).)*|SPUTUM(?:(?!\|).)*)\|((?:(?!\|).)*)\|Acid\sFast\sSmear\|((?:(?!\|).)*)\|((?:(?!\|).)*)\|')
matches_micro_smear = pattern_micro_smear.findall(micro_text)

Micro_EPMI_smear = []
Micro_Date_smear = []
Micro_smear_result = []
Micro_smear_source = []
Micro_smear_total = []
for match_smear in matches_micro_smear:
    Micro_EPMI_smear.append(match_smear[0])
    Micro_Date_smear .append(match_smear[4])
    Micro_smear_result.append(match_smear[9])
    Micro_smear_source.append(match_smear[6])
    Micro_smear_total.append(match_smear[8])
Micro_smear = pd.DataFrame({'Smear Date':Micro_Date_smear, 'Acid Fast Smear':Micro_smear_result, 'Smear Source':Micro_smear_source, }, index=[Micro_EPMI_smear])
Micro_smear.index.names = ['EMPI']
Micro_smear['Acid Fast Smear'] = Micro_smear['Acid Fast Smear'].str.extract(r'(1\+|2\+|3\sto\s4\+)', expand=True)
Micro_smear = Micro_smear.astype({'Smear Source':'category', 'Acid Fast Smear':'category'})
Micro_smear['Smear Date'] = pd.to_datetime(Micro_smear['Smear Date'])
Micro_gb_empi = Micro_smear.groupby(['EMPI'])
Micro_smear_counts = Micro_gb_empi['Acid Fast Smear'].value_counts()
Micro_smear_counts = pd.DataFrame(Micro_smear_counts)
Micro_smear_counts = Micro_smear_counts.unstack()
Micro_smear_counts = Micro_smear_counts.rename(columns= {0 : 'Counts'})
Micro_smear_counts.columns = [' '.join(col).strip() for col in Micro_smear_counts.columns.values]
Micro_smear_counts = Micro_smear_counts.rename(columns= {'Acid Fast Smear 1+': '1+ Count', 'Acid Fast Smear 2+':'2+ Count', 'Acid Fast Smear 3 to 4+':'3 to 4+ Count', 'Acid Fast Smear Positive': 'Postive, not specified'})
Micro_smear_counts = Micro_smear_counts.fillna(value=0)
Micro_smear_counts['Total Positive Smears'] = Micro_smear_counts['1+ Count'] + Micro_smear_counts['2+ Count'] + Micro_smear_counts['3 to 4+ Count']
Micro_smear_total = pd.DataFrame({'Smear':Micro_smear_total}, index=[Micro_EPMI_smear])
Micro_smear_total.index.names = ['EMPI']
Micro_smear_total['Smear'] = Micro_smear_total['Smear'].str.extract(r'(TAFSM)', expand=True)
Micro_smear_total_gb = Micro_smear_total.groupby('EMPI')
Micro_smear_total_gb = Micro_smear_total_gb['Smear'].value_counts()
Total_smears = pd.DataFrame(Micro_smear_total_gb)
Total_smears = Total_smears.rename(columns= {'Smear' : 'Total # of Smears'})
Total_smears = Total_smears.reset_index()
Total_smears = Total_smears.drop('Smear', axis=1)
Total_smears = Total_smears.set_index('EMPI')
Micro_smear_df = Total_smears.join(Micro_smear_counts, how='outer')
Micro_smear_df = Micro_smear_df.fillna(value=0)


pattern_allsmear = re.compile(r'Date:\s(\d+\/\d+\/\d+)\s(\d+:\d+:\d+)(?:\n|\r\n?)Patient:(.*):(\d+)(?:\n|\r\n?)Specimen\sType:(.*)(?:\n|\r\n?).*(?:\n|\r\n?)Reported.*(?:\n|\r\n?)Test Name:\s(Acid\sFast\sSmear)')

allsmear_EPMI = []
allsmear_Date = []
allsmear = []
allsmear

for report_micro in MedicalReport('Micro.txt', end='[report_end]'):
    for match_microall in pattern_allsmear.findall(report_micro['Organism_Text']):
        allsmear_EPMI.append(report_micro['EMPI'])
        allsmear_Date.append(match_microall[0])
        allsmear.append(match_microall[5])

Micro_smear_total = pd.DataFrame({'Index':allsmear_EPMI, 'Total Smears':allsmear})
Micro_smear_total['Index'] = Micro_smear_total['Index'].str.extract(r'(\d+)')
Micro_smear_total = Micro_smear_total.groupby(Micro_smear_total['Index'])
Micro_smear_total = Micro_smear_total['Total Smears'].value_counts()
Micro_smear_total = pd.DataFrame(Micro_smear_total)
Micro_smear_total = Micro_smear_total.unstack()
Micro_smear_total.columns = [' '.join(col).strip() for col in Micro_smear_total.columns.values]
Micro_smear_total.rename(columns = {Micro_smear_total.columns[0]: 'Total Smears'}, inplace = True)


#Most Recent Pos smear
Micro_smear_temp = Micro_smear.dropna()
Micro_smear_recent_pos = Micro_smear_temp.groupby(['EMPI']).agg({'Smear Date':np.max})
Micro_smear_recent_pos = Micro_smear_recent_pos.rename(columns= {'Smear Date': 'Date of Most Recent Pos Smear'})
#First Positive Smears
Micro_first_pos_smear = Micro_smear_temp.groupby(['EMPI']).agg({'Smear Date':np.min})
Micro_first_pos_smear


# Micro_smear_counts.to_csv('/Volumes/homedir$/MAC Project/Complete Project//Smear.csv')

# 1-	Adults ≥18 years of age
# 2-	Have at least 1 respiratory sample positive for MAC
# 3-	American Thoracic Society diagnostic criteria for NTM pulmonary disease1 i.e. have one of the following (1) pulmonary symptoms, (2) nodular or cavitary opacities on chest radiograph or high resolution chest CT with multifocal bronchiectasis and multiple small nodules and appropriate exclusion of alternate diagnosis, (3) ≥2 sputum cultures, 1 bronchoalveolar lavage culture or 1 lung biopsy culture positive for MAC.

#---------------------------Clarithromycin Sensitivys--------------------#
#Micro with Susceptibility


Micro_pos = pd.DataFrame({'Date':Micro_Date_pos, 'Species':Micro_species, 'Antibiotic Susceptibility':Micro_sens, 'Culture Source':Micro_cx_source, 'Index':Micro_EPMI_pos})
Micro_pos = Micro_pos.set_index('Index')
Micro_ABX = Micro_pos['Antibiotic Susceptibility'].replace('\n \n', np.nan)
Micro_ABX = pd.DataFrame(Micro_ABX)
Micro_pos = Micro_pos.drop('Antibiotic Susceptibility', axis=1)
Micro_pos['Antibiotic Susceptibility'] = Micro_ABX['Antibiotic Susceptibility']
Micro_pos = Micro_pos.dropna()



Micro_pos['Amikacin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)amikacin.+?([R|S|I|N])', expand=True)
Micro_pos['Ciprofloxacin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)ciprofloxacin.+?([R|S|I|N])', expand=True)
Micro_pos['Clarithromycin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)clarithromycin.+?([R|S|I|N])', expand=True)
Micro_pos['Doxycycline Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)doxycycline.+?([R|S|I|N])', expand=True)
Micro_pos['Ethambutol Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)ethambutol.+?([R|S|I|N])', expand=True)
Micro_pos['Linezolid Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)linezolid.+?([R|S|I|N])', expand=True)
Micro_pos['Moxifloxacin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)moxifloxacin.+?([R|S|I|N])', expand=True)
Micro_pos['Rifabutin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)rifabutin.+?([R|S|I|N])', expand=True)
Micro_pos['Rifampin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)rifampin.+?([R|S|I|N])', expand=True)
Micro_pos['Trimethoprim/Sulfamethoxazole Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)trimethoprim/sulfamethoxazole.+?([R|S|I|N])', expand=True)
Micro_pos['Kanamycin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)kanamycin.+?([R|S|I|N])', expand=True)
Micro_pos['Levofloxacin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)levofloxacin.+?([R|S|I|N])', expand=True)
Micro_pos['Minocycline Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)minocycline.+?([R|S|I|N])', expand=True)
Micro_pos['Sulfisoxazole Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)sulfisoxazole.+?([R|S|I|N])', expand=True)
Micro_pos['Tobramycin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)tobramycin.+?([R|S|I|N])', expand=True)
Micro_pos['Cefoxitin Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)cefoxitin.+?([R|S|I|N])', expand=True)
Micro_pos['Ertapenem Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)ertapenem.+?([R|S|I|N])', expand=True)
Micro_pos['Meropenem Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)meropenem.+?([R|S|I|N])', expand=True)
Micro_pos['Imipenem Susceptibility'] = Micro_pos['Antibiotic Susceptibility'].str.extract(r'(?i)imipenem.+?([R|S|I|N])', expand=True)
Micro_pos['Date'] =  pd.to_datetime(Micro_pos['Date'])
Micro_pos = Micro_pos.reset_index()
#Species for Susceptibility
Macrolide_species = Micro_pos[['Clarithromycin Susceptibility', 'Index', 'Date', 'Species']]
Macrolide_species1 = Macrolide_species

# ###Susceptibility adjust
# Macrolide_sens = Micro_pos[['Clarithromycin Susceptibility', 'Index', 'Date']]
# Macrolide_sens['Clarithromycin Susceptibility'] = Macrolide_sens['Clarithromycin Susceptibility'].replace('R', 1)
# Macrolide_sens['Clarithromycin Susceptibility'] = Macrolide_sens['Clarithromycin Susceptibility'].replace('S', 0)
# Macrolide_sens['Clarithromycin Susceptibility'] = Macrolide_sens['Clarithromycin Susceptibility'].replace('I', np.nan)
# Macrolide_sens
# Macrolide_sens = Macrolide_sens.dropna()
# dst_count = Macrolide_sens
# dst_count['# of DST Test'] = 1
# dst_count = dst_count.groupby('Index')
# dst_count = dst_count['# of DST Test'].value_counts()
# dst_count = pd.DataFrame(dst_count)
# #dst_count.columns = [' '.join(col).strip() for col in dst_count.columns.values]
# dst_count = dst_count.rename(columns= {'# of DST Test' : 'DST Count'})
# dst_count = dst_count.reset_index().set_index('Index')
# dst_count = dst_count['DST Count']
# dst_count = pd.DataFrame(dst_count)
#Macrolide_sens = Macrolide_sens.drop_duplicates(['Index'], keep='last')


#Back to Suscept
# Macrolide_sens = Macrolide_sens.astype({'Clarithromycin Susceptibility':'category'})
# Macrolide_sens['year'] = Macrolide_sens['Date'].dt.year
# Macrolide_sens_gb = Macrolide_sens.groupby(['year', 'Clarithromycin Susceptibility', 'Index'])
# Macrolide_sens_gb = pd.DataFrame(Macrolide_sens_gb.size())
# Macrolide_sens_gb = Macrolide_sens_gb.groupby(['year','Clarithromycin Susceptibility'])
# Macrolide_sens_gb = pd.DataFrame(Macrolide_sens_gb.size())
# Macrolide_sens_gb = Macrolide_sens_gb.unstack()
# Macrolide_sens_gb = Macrolide_sens_gb.rename(columns= {0 : 'Sensitive', 1: 'Resistant'})
# Macrolide_sens_gb.columns = [' '.join(col).strip() for col in Macrolide_sens_gb.columns.values]
# Macrolide_sens_gb = Macrolide_sens_gb .rename(columns= {'Sensitive Sensitive' : 'Sensitive', 'Sensitive Resistant': 'Resistant'})
# Macrolide_sens_gb = Macrolide_sens_gb.fillna(value=0)
# Macrolide_sens_gb["Number of Susceptibility Test"] = Macrolide_sens_gb['Resistant'] + Macrolide_sens_gb['Sensitive']
#
# def proportion(c):
#     return c['Resistant']/(c['Sensitive'] + c ['Resistant'])
# Macrolide_sens_gb['Yearly Proportion of Macrolide Resistance'] = Macrolide_sens_gb.apply(proportion, axis=1)


# Macrolide_sens =  Macrolide_sens.drop_duplicates(['Index', 'year', 'Clarithromycin Susceptibility'], keep='first')
# Macrolide_sens =  Macrolide_sens.sort_values(by='Clarithromycin Susceptibility', ascending=False)
# Macrolide_sens =  Macrolide_sens.drop_duplicates(['Index', 'year',], keep='first')
#
# #Conversion of Susceptibility
# Macrolide_conv = Macrolide_sens[['Clarithromycin Susceptibility', 'Index', 'Date']]
# Micro_sens_baseline = Macrolide_conv.loc[Macrolide_conv.groupby(['Index'])['Date'].idxmin()].set_index(['Index'])
# Micro_sens_followup = Macrolide_conv.loc[Macrolide_conv.groupby(['Index'])['Date'].idxmax()].set_index(['Index'])
# Micro_sens_baseline = Micro_sens_baseline.rename( columns={"Date": "Baseline Date", "Clarithromycin Susceptibility": "Clarithromycin Susceptibility Baseline"})
# Micro_sens_followup = Micro_sens_followup.rename( columns={"Date": "Follow-up Date", "Clarithromycin Susceptibility": "Clarithromycin Susceptibility Follow-up"})
# Macrolide_conv = Micro_sens_baseline.join(Micro_sens_followup)
# def func(c):
#     if c['Clarithromycin Susceptibility Baseline'] == 0 and c['Clarithromycin Susceptibility Follow-up']==1:
#         return 'Conversion'
#     else:
#         return 'No Conversion'
# Macrolide_conv['Macrolide Susceptibility Conversion'] = Macrolide_conv.apply(func, axis=1)
#
# Macrolide_conv
# ##
# Macrolide_sens_gb = Macrolide_sens.groupby(['year', 'Clarithromycin Susceptibility', 'Index'])
# Macrolide_sens_gb = pd.DataFrame(Macrolide_sens_gb.size())
# Macrolide_sens_gb = Macrolide_sens_gb.groupby(['year','Clarithromycin Susceptibility'])
# Macrolide_sens_gb = pd.DataFrame(Macrolide_sens_gb.size())
# Macrolide_sens_gb = Macrolide_sens_gb.unstack()
# Macrolide_sens_gb = Macrolide_sens_gb.rename(columns= {0 : 'Sensitive', 1: 'Resistant'})
# Macrolide_sens_gb.columns = [' '.join(col).strip() for col in Macrolide_sens_gb.columns.values]
# Macrolide_sens_gb = Macrolide_sens_gb .rename(columns= {'Sensitive Sensitive' : 'Sensitive', 'Sensitive Resistant': 'Resistant'})
# Macrolide_sens_gb = Macrolide_sens_gb.fillna(value=0)
# Macrolide_sens_gb["Number of Susceptibility Test"] = Macrolide_sens_gb['Resistant'] + Macrolide_sens_gb['Sensitive']
# Macrolide_sens_gb
#
# def proportion(c):
#     return c['Resistant']/(c['Sensitive'] + c ['Resistant'])
# Macrolide_sens_gb['Yearly Proportion of Macrolide Resistance'] = Macrolide_sens_gb.apply(proportion, axis=1)
#

Macrolide_species['Clarithromycin Susceptibility'] = Macrolide_species['Clarithromycin Susceptibility'].replace('R', 1)
Macrolide_species['Clarithromycin Susceptibility'] = Macrolide_species['Clarithromycin Susceptibility'].replace('S', 0)
Macrolide_species['Clarithromycin Susceptibility'] = Macrolide_species['Clarithromycin Susceptibility'].replace('I', np.nan)
Macrolide_species = Macrolide_species.dropna()
Macrolide_species = Macrolide_species.astype({'Clarithromycin Susceptibility':'category'})
Macrolide_species['year'] = Macrolide_species['Date'].dt.year

Macrolide_species =  Macrolide_species.drop_duplicates(['Index', 'year','Clarithromycin Susceptibility'], keep='first')
Macrolide_species =  Macrolide_species.sort_values(by='Clarithromycin Susceptibility', ascending=False)
Macrolide_species =  Macrolide_species.drop_duplicates(['Index', 'year',], keep='first')

def func(c):
    if 'Abscessus'  in c['Species'] or 'abscessus' in c['Species'] or 'ABSCESSUS' in c['Species']:
        return 'M. Abscessus'
    elif 'Avium'  in c['Species'] or 'avium' in c['Species'] or 'AVIUM' in c['Species']:
        return 'MAC'
    else:
        return 'Other Species'
Macrolide_species['Species']= Macrolide_species.apply(func,axis=1)

######WORKING adjustmen######
#Macrolide_species = Macrolide_species.loc[Macrolide_species['Species'] == 'M. Abscessus']
Macrolide_sens = Macrolide_species
Macrolide_sens = Macrolide_sens.drop('Species', axis=1)
Macrolide_sens = Macrolide_sens.astype({'Clarithromycin Susceptibility':'category'})
Macrolide_sens['year'] = Macrolide_sens['Date'].dt.year

Macrolide_sens =  Macrolide_sens.drop_duplicates(['Index', 'year', 'Clarithromycin Susceptibility'], keep='first')
Macrolide_sens =  Macrolide_sens.sort_values(by='Clarithromycin Susceptibility', ascending=False)
Macrolide_sens =  Macrolide_sens.drop_duplicates(['Index', 'year',], keep='first')

#DST count
dst_count = Macrolide_sens
dst_count['# of DST Test'] = 1
dst_count = dst_count.groupby('Index')
dst_count = dst_count['# of DST Test'].value_counts()
dst_count = pd.DataFrame(dst_count)
#dst_count.columns = [' '.join(col).strip() for col in dst_count.columns.values]
dst_count = dst_count.rename(columns= {'# of DST Test' : 'DST Count'})
dst_count = dst_count.reset_index().set_index('Index')
dst_count = dst_count['DST Count']
dst_count = pd.DataFrame(dst_count)
#Conversion of Susceptibility
Macrolide_conv = Macrolide_sens[['Clarithromycin Susceptibility', 'Index', 'Date']]
Micro_sens_baseline = Macrolide_conv.loc[Macrolide_conv.groupby(['Index'])['Date'].idxmin()].set_index(['Index'])
Micro_sens_followup = Macrolide_conv.loc[Macrolide_conv.groupby(['Index'])['Date'].idxmax()].set_index(['Index'])
Micro_sens_baseline = Micro_sens_baseline.rename( columns={"Date": "Baseline Date", "Clarithromycin Susceptibility": "Clarithromycin Susceptibility Baseline"})
Micro_sens_followup = Micro_sens_followup.rename( columns={"Date": "Follow-up Date", "Clarithromycin Susceptibility": "Clarithromycin Susceptibility Follow-up"})
Macrolide_conv = Micro_sens_baseline.join(Micro_sens_followup)
def func(c):
    if c['Clarithromycin Susceptibility Baseline'] == 0 and c['Clarithromycin Susceptibility Follow-up']==1:
        return 'Conversion'
    else:
        return 'No Conversion'
Macrolide_conv['Macrolide Susceptibility Conversion'] = Macrolide_conv.apply(func, axis=1)

##

Macrolide_sens_gb = Macrolide_sens.groupby(['year', 'Clarithromycin Susceptibility', 'Index'])
Macrolide_sens_gb = pd.DataFrame(Macrolide_sens_gb.size())
Macrolide_sens_gb = Macrolide_sens_gb.groupby(['year','Clarithromycin Susceptibility'])
Macrolide_sens_gb = pd.DataFrame(Macrolide_sens_gb.size())
Macrolide_sens_gb = Macrolide_sens_gb.unstack()
Macrolide_sens_gb = Macrolide_sens_gb.rename(columns= {0 : 'Sensitive', 1: 'Resistant'})
Macrolide_sens_gb.columns = [' '.join(col).strip() for col in Macrolide_sens_gb.columns.values]
Macrolide_sens_gb = Macrolide_sens_gb .rename(columns= {'Sensitive Sensitive' : 'Sensitive', 'Sensitive Resistant': 'Resistant'})
Macrolide_sens_gb = Macrolide_sens_gb.fillna(value=0)
Macrolide_sens_gb["Number of Susceptibility Test"] = Macrolide_sens_gb['Resistant'] + Macrolide_sens_gb['Sensitive']
Macrolide_sens_gb

def proportion(c):
    return c['Resistant']/(c['Sensitive'] + c ['Resistant'])
Macrolide_sens_gb['Yearly Proportion of Macrolide Resistance'] = Macrolide_sens_gb.apply(proportion, axis=1)







#####Proportion of species####
Macrolide_species_gb =np.nan
Macrolide_species_gb = Macrolide_species.groupby(['year', 'Species', 'Index'])
Macrolide_species_gb= pd.DataFrame(Macrolide_species_gb.size())
Macrolide_species_gb = Macrolide_species_gb.groupby(['year','Species'])
Macrolide_species_gb = pd.DataFrame(Macrolide_species_gb.size())
Macrolide_species_gb  = Macrolide_species_gb.unstack()
Macrolide_species_gb  = Macrolide_species_gb.rename(columns= {0 : 'Sensitive', 1: 'Resistant'})
Macrolide_species_gb.columns = [' '.join(col).strip() for col in Macrolide_species_gb.columns.values]

Macrolide_species_gb = Macrolide_species_gb.rename(columns= {'Sensitive MAC' : 'MAC', 'Sensitive Other Species': 'Other Species'})
Macrolide_species_gb = Macrolide_species_gb.fillna(value=0)
Macrolide_species_gb["Number of Susceptibility Test"] = Macrolide_species_gb['MAC'] + Macrolide_species_gb['Other Species']

def proportion(c):
    return c['MAC'] / c['Number of Susceptibility Test']
Macrolide_species_gb['Proportion of tested species that were MAC'] = Macrolide_species_gb.apply(proportion, axis=1)
Macrolide_species_gb
#
# Macrolide_species_gb.columns = [' '.join(col).strip() for col in Macrolide_species_gb.columns.values]
# Macrolide_species_gb = Macrolide_species_gb .rename(columns= {'Sensitive M. Abscessus' : 'M. Abscessus', 'Sensitive Other Species': 'Other Species'})
# Macrolide_species_gb = Macrolide_species_gb.fillna(value=0)
# Macrolide_species_gb["Number of Susceptibility Test"] = Macrolide_species_gb['M. Abscessus'] + Macrolide_species_gb['Other Species']
#
# def proportion(c):
#     return c['M. Abscessus'] / c['Number of Susceptibility Test']
#
# Macrolide_species_gb['Proportion of tested species that were M. Abscessus'] = Macrolide_species_gb.apply(proportion, axis=1)
# Macrolide_species_gb = Macrolide_species_gb.drop('Number of Susceptibility Test', axis=1)
# Macrolide_sens_gb = Macrolide_sens_gb.join(Macrolide_species_gb)
# Macrolide_sens_gb
# Macrolide_sens_gb.to_csv('/Volumes/homedir$/MAC Project/Complete Project/Micro_Cx_nodup.csv')
#
# Columns = ['Species']
# Categorical = ['Species']
# groupby = ['Surgery for MAC?']
# Species = TableOne(Macrolide_species, Columns, Categorical)
# Species.to_csv('/Volumes/homedir$/MAC Project/Complete Project/Susceptibility/species.csv')
#
#
#
#
#
# Macrolide_species1['Clarithromycin Susceptibility'] = Macrolide_species1['Clarithromycin Susceptibility'].replace('R', 1)
# Macrolide_species1['Clarithromycin Susceptibility'] = Macrolide_species1['Clarithromycin Susceptibility'].replace('S', 0)
# Macrolide_species1['Clarithromycin Susceptibility'] = Macrolide_species1['Clarithromycin Susceptibility'].replace('I', np.nan)
# Macrolide_species1 = Macrolide_species1.dropna()
# Macrolide_species1 = Macrolide_species1.astype({'Clarithromycin Susceptibility':'category'})
# Macrolide_species1['year'] = Macrolide_species1['Date'].dt.year
#
# Macrolide_species1 =  Macrolide_species1.drop_duplicates(['Index', 'year','Clarithromycin Susceptibility'], keep='first')
# Macrolide_species1 =  Macrolide_species1.sort_values(by='Clarithromycin Susceptibility', ascending=False)
# Macrolide_species1 =  Macrolide_species1.drop_duplicates(['Index', 'year',], keep='first')
# Macrolide_species1
#
# def func(c):
#     if 'Avium'  in c['Species'] or 'avium' in c['Species'] or 'AVIUM' in c['Species']:
#         return 'MAC'
#     else:
#         return 'Other Species'
# Macrolide_species1['Species']= Macrolide_species1.apply(func,axis=1)
# Macrolide_species1.to_csv('/Volumes/homedir$/MAC Project/Complete Project/temp.csv')
# Macrolide_species_gb1 =np.nan
# Macrolide_species_gb1 = Macrolide_species1.groupby(['year', 'Species', 'Index'])
# Macrolide_species_gb1= pd.DataFrame(Macrolide_species_gb1.size())
# Macrolide_species_gb1 = Macrolide_species_gb1.groupby(['year','Species'])
# Macrolide_species_gb1 = pd.DataFrame(Macrolide_species_gb1.size())
# Macrolide_species_gb1  = Macrolide_species_gb1.unstack()
# Macrolide_species_gb1  = Macrolide_species_gb1.rename(columns= {0 : 'Sensitive', 1: 'Resistant'})
# Macrolide_species_gb1.columns = [' '.join(col).strip() for col in Macrolide_species_gb1.columns.values]
# Macrolide_species_gb1 = Macrolide_species_gb1.rename(columns= {'Sensitive MAC' : 'MAC', 'Sensitive Other Species': 'Other Species'})
# Macrolide_species_gb1 = Macrolide_species_gb1.fillna(value=0)
# Macrolide_species_gb1["Number of Susceptibility Test"] = Macrolide_species_gb1['MAC'] + Macrolide_species_gb1['Other Species']
#
# def proportion(c):
#     return c['MAC'] / c['Number of Susceptibility Test']
#
# Macrolide_species_gb1['Proportion of tested species that were MAC'] = Macrolide_species_gb1.apply(proportion, axis=1)
# Macrolide_species_gb1
# Macrolide_species_gb1 = Macrolide_species_gb1.drop(['Number of Susceptibility Test', 'Other Species'], axis=1)
# Macrolide_sens_gb = Macrolide_sens_gb.join(Macrolide_species_gb['MAC', 'Other Species'])
Macrolide_sens_gb[['MAC', 'Other Species']] = Macrolide_species_gb[['MAC', 'Other Species']]
Macrolide_sens_gb = Macrolide_sens_gb.join(Micro_all_pos_gb)
Macrolide_sens_gb.to_csv('/Volumes/homedir$/MAC Project/Complete Project/Micro_Cx_nodup.csv')

Macrolide_species_gb =np.nan
Macrolide_species = Macrolide_species.groupby(['Species', 'Index'])
Macrolide_species_gb= pd.DataFrame(Macrolide_species.size())
Macrolide_species_gb = Macrolide_species_gb.reset_index().set_index('Index')
Macrolide_species_gb
Macrolide_species_gb.to_csv('/Volumes/homedir$/MAC Project/Complete Project/temp_species.csv')
#-------------------------- Radiology ---------------------------#
#Bronchiectasis#
EMPI_bronc = []
Bronchiectasis = []
Date_bronc = []
radiology_type_bronc = []
focal_bronch = []
pattern_bronchiectasis = re.compile(r'(?i)(bronchiectasis)')
pattern_nobronch = re.compile(r'(?i)(no\s.*bronchiectasis)')
pattern_change = re.compile(r'(?i)(no\s.*(change|new).*bronchiectasis)')
pattern_diffuse = re.compile('(?i)(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout).*bronchi')
pattern_diffuse1 = re.compile(r'(?i)bronchi.*(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout)')
pattern_focal = re.compile(r'(?i)((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex))).*?bronchi')
pattern_focal1 = re.compile(r'(?i)bronchi.*?((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex)))')


for report_rad in MedicalReport('Radiology.txt', end='[report_end]'):
        if re.search(pattern_bronchiectasis, report_rad['Report_Text']):
            if re.search(r'HISTORY', report_rad['Report_Text']):
                matches = re.findall(r'REPORT([\s\S]+)',report_rad['Report_Text'])
                for match in matches:
                    match_bronc = match.replace("\r"," ")
                    match_bronc = match_bronc.replace("\n"," ")
                    match_bronc = match_bronc.split('. ')
                    #Bronchiectasis with 2 or more negating qualifiers
                    for sub_string in match_bronc:
                        if re.search(pattern_nobronch, sub_string):
                            if sub_string.lower().count('no ') >=2:
                                if re.search(r'(?i)no\s.*?bronchiectasis.*no\s', sub_string):
                                    sub_string_and = sub_string.split('and')
                                    for sub_str in sub_string_and:
                                        if re.search(pattern_change, sub_str):
                                            if re.search(pattern_diffuse, sub_str):
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Diffuse Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                                focal_bronch.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string):
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Diffuse Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                                focal_bronch.append('n/a')
                                            elif re.search(pattern_focal, sub_string):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_bronch.append(match[0])
                                                    EMPI_bronc.append(report_rad['EMPI'])
                                                    Bronchiectasis.append('Focal Bronchiectasis')
                                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_bronch.append(match[0])
                                                    EMPI_bronc.append(report_rad['EMPI'])
                                                    Bronchiectasis.append('Focal Bronchiectasis')
                                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                            else:
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Bronchiectasis NOS')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                                focal_bronch.append('n/a')
                                        elif re.search(pattern_nobronch, sub_str):
                                            print('True Negative')
                                        elif re.search(r'(?i)bronchiectasis', sub_str):
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Bronchiectasis NOS')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                            focal_bronch.append('n/a')
                            #group with only 1 negating qualifier
                            else:
                                #Change between negating qualifier and bronch
                                if re.search(pattern_change, sub_string):
                                    if re.search(pattern_diffuse, sub_string):
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Diffuse Bronchiectasis')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                        focal_bronch.append('n/a')
                                    elif re.search(pattern_diffuse1, sub_string):
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Diffuse Bronchiectasis')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                        focal_bronch.append('n/a')
                                    elif re.search(pattern_focal, sub_string):
                                        matches = re.findall(pattern_focal, sub_string)
                                        for match in matches:
                                            focal_bronch.append(match[0])
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Focal Bronchiectasis')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                    elif re.search(pattern_focal1, sub_string):
                                        matches = re.findall(pattern_focal1, sub_string)
                                        for match in matches:
                                            focal_bronch.append(match[0])
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Focal Bronchiectasis')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                    else:
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Bronchiectasis NOS')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                        focal_bronch.append('n/a')
                                #True negative work up
                                else:
                                    split_by_delim = sub_string.split('and')
                                    for sub_string_negatives in split_by_delim:
                                        if re.search(pattern_nobronch, sub_string_negatives):
                                            print('True Negative')
                                        else:
                                            if re.search(pattern_diffuse, sub_string_negatives):
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Diffuse Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                                focal_bronch.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string_negatives):
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Diffuse Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                                focal_bronch.append('n/a')
                                            elif re.search(pattern_focal, sub_string_negatives):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_bronch.append(match[0])
                                                    EMPI_bronc.append(report_rad['EMPI'])
                                                    Bronchiectasis.append('Focal Bronchiectasis')
                                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string_negatives):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_bronch.append(match[0])
                                                    EMPI_bronc.append(report_rad['EMPI'])
                                                    Bronchiectasis.append('Focal Bronchiectasis')
                                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                            elif re.search(r'(?i)bronchiectasis', sub_string_negatives):
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Bronchiectasis NOS')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                                focal_bronch.append('n/a')
                                            # else:
                                            #     print(sub_string_negatives)
                        #Positves without negatating qualifier
                        else:
                            if re.search(r'(?i)bronchiectasis', sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Diffuse Bronchiectasis')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                    focal_bronch.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Diffuse Bronchiectasis')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                    focal_bronch.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_bronch.append(match[0])
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Focal Bronchiectasis')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_bronch.append(match[0])
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Focal Bronchiectasis')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                else:
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Bronchiectasis NOS')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                    focal_bronch.append('n/a')
            else:
                match_bronc = report_rad['Report_Text'].replace("\r"," ")
                match_bronc = match_bronc.replace("\n"," ")
                match_bronc = match_bronc.split('. ')
                #Bronchiectasis with 2 or more negating qualifiers
                for sub_string in match_bronc:
                    if re.search(pattern_nobronch, sub_string):
                        if sub_string.lower().count('no ') >=2:
                            if re.search(r'(?i)no\s.*?bronchiectasis.*no\s', sub_string):
                                sub_string_and = sub_string.split('and')
                                for sub_str in sub_string_and:
                                    if re.search(pattern_change, sub_str):
                                        if re.search(pattern_diffuse, sub_str):
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Diffuse Bronchiectasis')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                            focal_bronch.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string):
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Diffuse Bronchiectasis')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                            focal_bronch.append('n/a')
                                        elif re.search(pattern_focal, sub_string):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_bronch.append(match[0])
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Focal Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_bronch.append(match[0])
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Focal Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                        else:
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Bronchiectasis NOS')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                            focal_bronch.append('n/a')
                                    elif re.search(pattern_nobronch, sub_str):
                                        print('True Negative')
                                    elif re.search(r'(?i)bronchiectasis', sub_str):
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Bronchiectasis NOS')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                        focal_bronch.append('n/a')
                        #group with only 1 negating qualifier
                        else:
                            #Change between negating qualifier and bronch
                            if re.search(pattern_change, sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Diffuse Bronchiectasis')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                    focal_bronch.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Diffuse Bronchiectasis')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                    focal_bronch.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_bronch.append(match[0])
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Focal Bronchiectasis')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_bronch.append(match[0])
                                        EMPI_bronc.append(report_rad['EMPI'])
                                        Bronchiectasis.append('Focal Bronchiectasis')
                                        Date_bronc.append(report_rad['Report_Date_Time'])
                                        radiology_type_bronc.append(report_rad['Report_Description'])
                                else:
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Bronchiectasis NOS')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                                    focal_bronch.append('n/a')
                            #True negative work up
                            else:
                                split_by_delim = sub_string.split('and')
                                for sub_string_negatives in split_by_delim:
                                    if re.search(pattern_nobronch, sub_string_negatives):
                                        print('True Negative')
                                    else:
                                        if re.search(pattern_diffuse, sub_string_negatives):
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Diffuse Bronchiectasis')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                            focal_bronch.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string_negatives):
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Diffuse Bronchiectasis')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                            focal_bronch.append('n/a')
                                        elif re.search(pattern_focal, sub_string_negatives):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_bronch.append(match[0])
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Focal Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string_negatives):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_bronch.append(match[0])
                                                EMPI_bronc.append(report_rad['EMPI'])
                                                Bronchiectasis.append('Focal Bronchiectasis')
                                                Date_bronc.append(report_rad['Report_Date_Time'])
                                                radiology_type_bronc.append(report_rad['Report_Description'])
                                        elif re.search(r'(?i)bronchiectasis', sub_string_negatives):
                                            EMPI_bronc.append(report_rad['EMPI'])
                                            Bronchiectasis.append('Bronchiectasis NOS')
                                            Date_bronc.append(report_rad['Report_Date_Time'])
                                            radiology_type_bronc.append(report_rad['Report_Description'])
                                            focal_bronch.append('n/a')
                                        # else:
                                        #     print(sub_string_negatives)
                    #Positves without negatating qualifier
                    else:
                        if re.search(r'(?i)bronchiectasis', sub_string):
                            if re.search(pattern_diffuse, sub_string):
                                EMPI_bronc.append(report_rad['EMPI'])
                                Bronchiectasis.append('Diffuse Bronchiectasis')
                                Date_bronc.append(report_rad['Report_Date_Time'])
                                radiology_type_bronc.append(report_rad['Report_Description'])
                                focal_bronch.append('n/a')
                            elif re.search(pattern_diffuse1, sub_string):
                                EMPI_bronc.append(report_rad['EMPI'])
                                Bronchiectasis.append('Diffuse Bronchiectasis')
                                Date_bronc.append(report_rad['Report_Date_Time'])
                                radiology_type_bronc.append(report_rad['Report_Description'])
                                focal_bronch.append('n/a')
                            elif re.search(pattern_focal, sub_string):
                                matches = re.findall(pattern_focal, sub_string)
                                for match in matches:
                                    focal_bronch.append(match[0])
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Focal Bronchiectasis')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                            elif re.search(pattern_focal1, sub_string):
                                matches = re.findall(pattern_focal1, sub_string)
                                for match in matches:
                                    focal_bronch.append(match[0])
                                    EMPI_bronc.append(report_rad['EMPI'])
                                    Bronchiectasis.append('Focal Bronchiectasis')
                                    Date_bronc.append(report_rad['Report_Date_Time'])
                                    radiology_type_bronc.append(report_rad['Report_Description'])
                            else:
                                EMPI_bronc.append(report_rad['EMPI'])
                                Bronchiectasis.append('Bronchiectasis NOS')
                                Date_bronc.append(report_rad['Report_Date_Time'])
                                radiology_type_bronc.append(report_rad['Report_Description'])
                                focal_bronch.append('n/a')



Bronchiectasis_df = pd.DataFrame({'Index':EMPI_bronc, 'Bronchiectasis':Bronchiectasis, 'Date': Date_bronc, 'Radiology Type':radiology_type_bronc, 'Focal Location':focal_bronch})
Bronchiectasis_df['Index'] = Bronchiectasis_df['Index'].str.extract(r'(\d+)')
Bronchiectasis_df['Date'] = Bronchiectasis_df['Date'].str.extract(r'(\d+\/\d+\/\d+)')
Bronchiectasis_df['Radiology Type'] = Bronchiectasis_df['Radiology Type'].str.replace(r'(?i)(^.*CT.*$)', 'CT')
Bronchiectasis_df['Radiology Type'] = Bronchiectasis_df['Radiology Type'].str.replace(r'(?i)(^.*chest.*$)', 'CXR')
Bronchiectasis_df['Date'] = pd.to_datetime(Bronchiectasis_df['Date'])
Bronchiectasis_df['Focal Location'] = Bronchiectasis_df['Focal Location'].str.replace(r'(?i)(\s+)', ' ')
Bronchiectasis_df['Focal Location'] = Bronchiectasis_df['Focal Location'].str.lower()
Bronchiectasis_df = Bronchiectasis_df.drop_duplicates(('Index', 'Date', 'Bronchiectasis', 'Focal Location'), keep='first')
# Bronchiectasis_df = Bronchiectasis_df.drop_duplicates(subset=['Radiology Type', 'Date', 'Index'], keep='first', inplace=False)

Bronchiectasis_counts = Bronchiectasis_df.groupby(['Index', 'Date', 'Radiology Type'])
Bronchiectasis_counts = Bronchiectasis_counts['Bronchiectasis'].value_counts()
Bronchiectasis_counts = pd.DataFrame(Bronchiectasis_counts)
Bronchiectasis_counts.columns = ['Bronchiectasis Count']
Bronchiectasis_counts = Bronchiectasis_counts.reset_index()
Bronchiectasis_df = Bronchiectasis_df.merge(Bronchiectasis_counts, how='inner')
Bronchiectasis_df = Bronchiectasis_df.set_index('Index')



def func(c):
    if c['Bronchiectasis'] == 'Diffuse Bronchiectasis':
        return 1
    elif c['Bronchiectasis'] == 'Focal Bronchiectaisis':
        return 2
    else:
        return 3
Bronchiectasis_df['Rank'] = Bronchiectasis_df.apply(func, axis=1)

Bronchiectasis_df = Bronchiectasis_df.sort_values('Rank')

def func(c):
    if c['Bronchiectasis'] == 'Focal Bronchiectasis':
        if c['Bronchiectasis Count'] == 1:
            return 'Focal Bronchiectasis'
        elif c['Bronchiectasis Count'] >= 2:
            return 'Diffuse Bronchiectasis'
    else:
        return c['Bronchiectasis']
Bronchiectasis_df['Bronchiectasis'] = Bronchiectasis_df.apply(func, axis=1)
Bronchiectasis_df = Bronchiectasis_df.reset_index()
Bronchiectasis_df = Bronchiectasis_df.drop_duplicates(subset=['Index', 'Radiology Type', 'Date', ], keep='first')
Bronchiectasis_df = Bronchiectasis_df.set_index('Index')
#Bronchiectasis_df.to_csv('/Volumes/homedir$/MAC Project/Complete Project/temp.csv')
#107450130
Bronchiectasis_df= Bronchiectasis_df.drop(['Bronchiectasis Count', 'Rank'], axis=1)


def func(c):
    if c['Bronchiectasis'] == 'Diffuse Bronchiectasis':
        return 'n/a'
    else:
        return c['Focal Location']

Bronchiectasis_df['Focal Location'] = Bronchiectasis_df.apply(func, axis=1)


Bronchiectasis_df1 = Bronchiectasis_df
Bronchiectasis_df['Date of first Dx'] = NTB_diagnosis_mindate['Date of first Dx']
Bronchiectasis_df = Bronchiectasis_df.reset_index()
Bronchiectasis_df['Difference' ] = ((Bronchiectasis_df['Date'] - Bronchiectasis_df['Date of first Dx']).dt.days)
Bronchiectasis_CT = Bronchiectasis_df.loc[(Bronchiectasis_df['Radiology Type'] == 'CT')]
Bronchiectasis_CT = Bronchiectasis_CT.loc[(Bronchiectasis_CT['Bronchiectasis'] != 'Bronchiectasis NOS')]
Bronchiectasis_CT_baseline = Bronchiectasis_CT.loc[(Bronchiectasis_CT['Difference'] <= 365)&(Bronchiectasis_CT['Difference'] >= -730)]
Bronchiectasis_CT_baseline = Bronchiectasis_CT_baseline.loc[Bronchiectasis_CT_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Bronchiectasis_CXR = Bronchiectasis_df.loc[(Bronchiectasis_df['Radiology Type'] == 'CXR')]
Bronchiectasis_CXR = Bronchiectasis_CXR.loc[(Bronchiectasis_CXR['Bronchiectasis'] != 'Bronchiectasis NOS')]
Bronchiectasis_CXR_baseline = Bronchiectasis_CXR.loc[(Bronchiectasis_CXR['Difference'] <= 365)&(Bronchiectasis_CXR['Difference'] >= -730)]
Bronchiectasis_CXR_baseline = Bronchiectasis_CXR_baseline.loc[Bronchiectasis_CXR_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Bronchiectasis_nos = Bronchiectasis_df.loc[(Bronchiectasis_df['Bronchiectasis'] == 'Bronchiectasis NOS')]
Bronchiectasis_nos_baseline = Bronchiectasis_nos.loc[(Bronchiectasis_nos['Difference'] <= 365)& (Bronchiectasis_nos['Difference'] >= -730)]
Bronchiectasis_nos_baseline = Bronchiectasis_nos_baseline.loc[Bronchiectasis_nos_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Bronchiectasis_nos_baseline = Bronchiectasis_nos_baseline.loc[(Bronchiectasis_nos_baseline['Radiology Type'] == 'CXR')|(Bronchiectasis_nos_baseline['Radiology Type'] == 'CT')]
Bronchiectasis_CT_baseline = Bronchiectasis_CT_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Bronchiectasis_CT_baseline = Bronchiectasis_CT_baseline.rename(columns={"Bronchiectasis": "CT Bronchiectasis Baseline", "Date": "Bronchiectasis CT Baseline Date", 'Focal Location':'CT Bronchiectasis Location Baseline'})
Bronchiectasis_baseline = Bronchiectasis_CT_baseline.join(Bronchiectasis_CXR_baseline, how='outer')
Bronchiectasis_baseline = Bronchiectasis_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Bronchiectasis_baseline = Bronchiectasis_baseline.rename(columns={"Bronchiectasis": "CXR Bronchiectasis Baseline", "Date": "Bronchiectasis CXR Baseline Date", 'Focal Location':'CXR Bronchiectasis Location Baseline'})
Bronchiectasis_nos_baseline = Bronchiectasis_nos_baseline.drop(['Difference', 'Date of first Dx'], axis=1)
Bronchiectasis_nos_baseline = Bronchiectasis_nos_baseline.rename(columns={"Bronchiectasis": "Bronchiectasis Baseline-NOS", "Date": "Baseline Date-Bronchiectasis NOS", 'Radiology Type':'Radiology Type-Bronchiectasis NOS(Baseline)'})
Bronchiectasis_baseline = Bronchiectasis_baseline.join(Bronchiectasis_nos_baseline, how='outer')
Bronchiectasis_baseline = Bronchiectasis_baseline.drop('Focal Location', axis=1)
Bronchiectasis_baseline


Bronchiectasis_df1 = Bronchiectasis_df1.drop('Date of first Dx', axis=1)
Bronchiectasis_df1['Follow-up Date'] = Medications['Follow-up Date']
Bronchiectasis_df1 = Bronchiectasis_df1.reset_index()
Bronchiectasis_df1['Difference'] = ((Bronchiectasis_df1['Date'] - Bronchiectasis_df1['Follow-up Date']).dt.days)
Bronchiectasis_CT1 = Bronchiectasis_df1.loc[(Bronchiectasis_df1['Radiology Type'] == 'CT')]
Bronchiectasis_CT1 = Bronchiectasis_CT1.loc[(Bronchiectasis_CT1['Bronchiectasis'] != 'Bronchiectasis NOS')]
Bronchiectasis_CT_fu = Bronchiectasis_CT1.loc[(Bronchiectasis_CT1['Difference'] >= 730)]
Bronchiectasis_CT_fu = Bronchiectasis_CT_fu.loc[Bronchiectasis_CT_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Bronchiectasis_CXR1 = Bronchiectasis_df1.loc[(Bronchiectasis_df1['Radiology Type'] == 'CXR')]
Bronchiectasis_CXR1 = Bronchiectasis_CXR1.loc[(Bronchiectasis_CXR1['Bronchiectasis'] != 'Bronchiectasis NOS')]
Bronchiectasis_CXR_fu = Bronchiectasis_CXR1.loc[(Bronchiectasis_CXR1['Difference'] >= 730)]
Bronchiectasis_CXR_fu = Bronchiectasis_CXR_fu.loc[Bronchiectasis_CXR_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Bronchiectasis_nos1 = Bronchiectasis_df1.loc[(Bronchiectasis_df1['Bronchiectasis'] == 'Bronchiectasis NOS')]
Bronchiectasis_nos_fu = Bronchiectasis_nos1.loc[(Bronchiectasis_nos1['Difference'] >= 730)]
Bronchiectasis_nos_fu = Bronchiectasis_nos_fu.loc[Bronchiectasis_nos_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Bronchiectasis_nos_fu = Bronchiectasis_nos_fu.loc[(Bronchiectasis_nos_fu['Radiology Type'] == 'CXR')|(Bronchiectasis_nos_fu['Radiology Type'] == 'CT')]
Bronchiectasis_CT_fu = Bronchiectasis_CT_fu.drop(['Difference', 'Follow-up Date', 'Radiology Type'], axis=1)
Bronchiectasis_CT_fu = Bronchiectasis_CT_fu.rename(columns={"Bronchiectasis": "CT Bronchiectasis Follow-up", "Date": "Bronchiectasis CT Follow-up Date", 'Focal Location':'CT Bronchiectasis Location FU'})
Bronchiectasis_fu = Bronchiectasis_CT_fu.join(Bronchiectasis_CXR_fu, how='outer')
Bronchiectasis_fu = Bronchiectasis_fu.drop(['Difference', 'Radiology Type'], axis=1)
Bronchiectasis_fu = Bronchiectasis_fu.rename(columns={"Bronchiectasis": "CXR Bronchiectasis Follow-up", "Date": "Bronchiectasis CXR Follow-up Date", 'Focal Location':'CXR Bronchiectasis Location FU'})
Bronchiectasis_nos_fu = Bronchiectasis_nos_fu.drop(['Difference', 'Follow-up Date'], axis=1)
Bronchiectasis_nos_fu = Bronchiectasis_nos_fu.rename(columns={"Bronchiectasis": "Bronchiectasis Follow-up-NOS", "Date": "Follow-up Date-Bronchiectasis NOS", 'Radiology Type':'Radiology Type-Bronchiectasis NOS(Follow-up)'})
Bronchiectasis_fu = Bronchiectasis_fu.join(Bronchiectasis_nos_fu, how='outer')
Bronchiectasis_fu = Bronchiectasis_fu.drop(['Follow-up Date', 'Focal Location'], axis=1)
#Bronchiectasis_df.to_csv('/Volumes/homedir$/MAC Project/Complete Project//temp.csv')


#-------------Cavitary----------#
EMPI_cavit = []
Cavitary = []
Date_cavit = []
radiology_type_cavit = []
focal_cavit = []
pattern_cavitary = re.compile(r'(?i)(cavit)')
pattern_nocavit = re.compile(r'(?i)(no\s.*cavit)')
pattern_change = re.compile(r'(?i)(no\s.*(change|new).*cavit)')
pattern_diffuse = re.compile('(?i)(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|widespread|extensive|multifocal|bases|multilob|both|multiple|scattered|(left.*right)|(right.*left)|throughout).*cavit')
pattern_diffuse1 = re.compile(r'(?i)cavit.*(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|widespread|extensive|multifocal|bases|multilob|both|multiple|scattered|(left.*right)|(right.*left)|throughout)')
pattern_focal = re.compile(r'(?i)((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex))).*?cavit')
pattern_focal1 = re.compile(r'(?i)cavit.*?((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex)))')


for report_rad in MedicalReport('Radiology.txt', end='[report_end]'):
        if re.search(pattern_cavitary, report_rad['Report_Text']):
            if re.search(r'HISTORY', report_rad['Report_Text']):
                matches = re.findall(r'REPORT([\s\S]+)',report_rad['Report_Text'])
                for match in matches:
                    match_cavit = match.replace("\r"," ")
                    match_cavit = match_cavit.replace("\n"," ")
                    match_cavit = match_cavit.split('. ')
                    #Cavitary with 2 or more negating qualifiers
                    for sub_string in match_cavit:
                        if re.search(pattern_nocavit, sub_string):
                            if sub_string.lower().count('no ') >=2:
                                if re.search(r'(?i)no\s.*?cavit.*no\s', sub_string):
                                    sub_string_and = sub_string.split('and')
                                    for sub_str in sub_string_and:
                                        if re.search(pattern_change, sub_str):
                                            if re.search(pattern_diffuse, sub_str):
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Diffuse Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                                focal_cavit.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string):
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Diffuse Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                                focal_cavit.append('n/a')
                                            elif re.search(pattern_focal, sub_string):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_cavit.append(match[0])
                                                    EMPI_cavit.append(report_rad['EMPI'])
                                                    Cavitary.append('Focal Cavitary')
                                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_cavit.append(match[0])
                                                    EMPI_cavit.append(report_rad['EMPI'])
                                                    Cavitary.append('Focal Cavitary')
                                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                            else:
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Cavitary NOS')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                                focal_cavit.append('n/a')
                                        elif re.search(pattern_nocavit, sub_str):
                                            print('True Negative')
                                        elif re.search(r'(?i)cavitary', sub_str):
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Cavitary NOS')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                            focal_cavit.append('n/a')
                            #group with only 1 negating qualifier
                            else:
                                #Change between negating qualifier and cavit
                                if re.search(pattern_change, sub_string):
                                    if re.search(pattern_diffuse, sub_string):
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Diffuse Cavitary')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                        focal_cavit.append('n/a')
                                    elif re.search(pattern_diffuse1, sub_string):
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Diffuse Cavitary')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                        focal_cavit.append('n/a')
                                    elif re.search(pattern_focal, sub_string):
                                        matches = re.findall(pattern_focal, sub_string)
                                        for match in matches:
                                            focal_cavit.append(match[0])
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Focal Cavitary')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                    elif re.search(pattern_focal1, sub_string):
                                        matches = re.findall(pattern_focal1, sub_string)
                                        for match in matches:
                                            focal_cavit.append(match[0])
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Focal Cavitary')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                    else:
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Cavitary NOS')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                        focal_cavit.append('n/a')
                                #True negative work up
                                else:
                                    split_by_delim = sub_string.split('and')
                                    for sub_string_negatives in split_by_delim:
                                        if re.search(pattern_nocavit, sub_string_negatives):
                                            print('True Negative')
                                        else:
                                            if re.search(pattern_diffuse, sub_string_negatives):
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Diffuse Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                                focal_cavit.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string_negatives):
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Diffuse Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                                focal_cavit.append('n/a')
                                            elif re.search(pattern_focal, sub_string_negatives):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_cavit.append(match[0])
                                                    EMPI_cavit.append(report_rad['EMPI'])
                                                    Cavitary.append('Focal Cavitary')
                                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string_negatives):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_cavit.append(match[0])
                                                    EMPI_cavit.append(report_rad['EMPI'])
                                                    Cavitary.append('Focal Cavitary')
                                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                            elif re.search(r'(?i)cavitary', sub_string_negatives):
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Cavitary NOS')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                                focal_cavit.append('n/a')
                                            # else:
                                            #     print(sub_string_negatives)
                        #Positves without negatating qualifier
                        else:
                            if re.search(r'(?i)cavit', sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Diffuse Cavitary')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                    focal_cavit.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Diffuse Cavitary')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                    focal_cavit.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_cavit.append(match[0])
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Focal Cavitary')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_cavit.append(match[0])
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Focal Cavitary')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                else:
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Cavitary NOS')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                    focal_cavit.append('n/a')
            else:
                match_cavit = report_rad['Report_Text'].replace("\r"," ")
                match_cavit = match_cavit.replace("\n"," ")
                match_cavit = match_cavit.split('. ')
                #Cavitary with 2 or more negating qualifiers
                for sub_string in match_cavit:
                    if re.search(pattern_nocavit, sub_string):
                        if sub_string.lower().count('no ') >=2:
                            if re.search(r'(?i)no\s.*?cavit.*no\s', sub_string):
                                sub_string_and = sub_string.split('and')
                                for sub_str in sub_string_and:
                                    if re.search(pattern_change, sub_str):
                                        if re.search(pattern_diffuse, sub_str):
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Diffuse Cavitary')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                            focal_cavit.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string):
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Diffuse Cavitary')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                            focal_cavit.append('n/a')
                                        elif re.search(pattern_focal, sub_string):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_cavit.append(match[0])
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Focal Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_cavit.append(match[0])
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Focal Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                        else:
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Cavitary NOS')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                            focal_cavit.append('n/a')
                                    elif re.search(pattern_nocavit, sub_str):
                                        print('True Negative')
                                    elif re.search(r'(?i)cavitary', sub_str):
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Cavitary NOS')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                        focal_cavit.append('n/a')
                        #group with only 1 negating qualifier
                        else:
                            #Change between negating qualifier and cavit
                            if re.search(pattern_change, sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Diffuse Cavitary')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                    focal_cavit.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Diffuse Cavitary')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                    focal_cavit.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_cavit.append(match[0])
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Focal Cavitary')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_cavit.append(match[0])
                                        EMPI_cavit.append(report_rad['EMPI'])
                                        Cavitary.append('Focal Cavitary')
                                        Date_cavit.append(report_rad['Report_Date_Time'])
                                        radiology_type_cavit.append(report_rad['Report_Description'])
                                else:
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Cavitary NOS')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                                    focal_cavit.append('n/a')
                            #True negative work up
                            else:
                                split_by_delim = sub_string.split('and')
                                for sub_string_negatives in split_by_delim:
                                    if re.search(pattern_nocavit, sub_string_negatives):
                                        print('True Negative')
                                    else:
                                        if re.search(pattern_diffuse, sub_string_negatives):
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Diffuse Cavitary')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                            focal_cavit.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string_negatives):
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Diffuse Cavitary')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                            focal_cavit.append('n/a')
                                        elif re.search(pattern_focal, sub_string_negatives):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_cavit.append(match[0])
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Focal Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string_negatives):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_cavit.append(match[0])
                                                EMPI_cavit.append(report_rad['EMPI'])
                                                Cavitary.append('Focal Cavitary')
                                                Date_cavit.append(report_rad['Report_Date_Time'])
                                                radiology_type_cavit.append(report_rad['Report_Description'])
                                        elif re.search(r'(?i)cavit', sub_string_negatives):
                                            EMPI_cavit.append(report_rad['EMPI'])
                                            Cavitary.append('Cavitary NOS')
                                            Date_cavit.append(report_rad['Report_Date_Time'])
                                            radiology_type_cavit.append(report_rad['Report_Description'])
                                            focal_cavit.append('n/a')
                                        # else:
                                        #     print(sub_string_negatives)
                    #Positves without negatating qualifier
                    else:
                        if re.search(r'(?i)cavit', sub_string):
                            if re.search(pattern_diffuse, sub_string):
                                EMPI_cavit.append(report_rad['EMPI'])
                                Cavitary.append('Diffuse Cavitary')
                                Date_cavit.append(report_rad['Report_Date_Time'])
                                radiology_type_cavit.append(report_rad['Report_Description'])
                                focal_cavit.append('n/a')
                            elif re.search(pattern_diffuse1, sub_string):
                                EMPI_cavit.append(report_rad['EMPI'])
                                Cavitary.append('Diffuse Cavitary')
                                Date_cavit.append(report_rad['Report_Date_Time'])
                                radiology_type_cavit.append(report_rad['Report_Description'])
                                focal_cavit.append('n/a')
                            elif re.search(pattern_focal, sub_string):
                                matches = re.findall(pattern_focal, sub_string)
                                for match in matches:
                                    focal_cavit.append(match[0])
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Focal Cavitary')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                            elif re.search(pattern_focal1, sub_string):
                                matches = re.findall(pattern_focal1, sub_string)
                                for match in matches:
                                    focal_cavit.append(match[0])
                                    EMPI_cavit.append(report_rad['EMPI'])
                                    Cavitary.append('Focal Cavitary')
                                    Date_cavit.append(report_rad['Report_Date_Time'])
                                    radiology_type_cavit.append(report_rad['Report_Description'])
                            else:
                                EMPI_cavit.append(report_rad['EMPI'])
                                Cavitary.append('Cavitary NOS')
                                Date_cavit.append(report_rad['Report_Date_Time'])
                                radiology_type_cavit.append(report_rad['Report_Description'])
                                focal_cavit.append('n/a')



Cavitary_df = pd.DataFrame({'Index':EMPI_cavit, 'Cavitary':Cavitary, 'Date': Date_cavit, 'Radiology Type':radiology_type_cavit, 'Focal Location':focal_cavit})
Cavitary_df['Index'] = Cavitary_df['Index'].str.extract(r'(\d+)')
Cavitary_df['Date'] = Cavitary_df['Date'].str.extract(r'(\d+\/\d+\/\d+)')
Cavitary_df['Radiology Type'] = Cavitary_df['Radiology Type'].str.replace(r'(?i)(^.*CT.*$)', 'CT')
Cavitary_df['Radiology Type'] = Cavitary_df['Radiology Type'].str.replace(r'(?i)(^.*chest.*$)', 'CXR')
Cavitary_df['Date'] = pd.to_datetime(Cavitary_df['Date'])
Cavitary_df['Focal Location'] = Cavitary_df['Focal Location'].str.replace(r'(?i)(\s+)', ' ')
Cavitary_df['Focal Location'] = Cavitary_df['Focal Location'].str.lower()
Cavitary_df = Cavitary_df.drop_duplicates(('Index', 'Date', 'Cavitary', 'Focal Location'), keep='first')
#Cavitary_df.to_csv('/Volumes/homedir$/MAC Project/Complete Project//temp.csv')
# Cavitary_df = Cavitary_df.drop_duplicates(subset=['Radiology Type', 'Date', 'Index'], keep='first', inplace=False)

Cavitary_counts = Cavitary_df.groupby(['Index', 'Date', 'Radiology Type'])
Cavitary_counts = Cavitary_counts['Cavitary'].value_counts()
Cavitary_counts = pd.DataFrame(Cavitary_counts)
Cavitary_counts.columns = ['Cavitary Count']
Cavitary_counts = Cavitary_counts.reset_index()
Cavitary_df = Cavitary_df.merge(Cavitary_counts, how='inner')
Cavitary_df = Cavitary_df.set_index('Index')
def func(c):
    if c['Cavitary'] == 'Diffuse Cavitary':
        return 1
    elif c['Cavitary'] == 'Focal Cavitary':
        return 2
    else:
        return 3
Cavitary_df['Rank'] = Cavitary_df.apply(func, axis=1)

Cavitary_df = Cavitary_df.sort_values('Rank')

def func(c):
    if c['Cavitary'] == 'Focal Cavitary':
        if c['Cavitary Count'] == 1:
            return 'Focal Cavitary'
        elif c['Cavitary Count'] >= 2:
            return 'Diffuse Cavitary'
    else:
        return c['Cavitary']

Cavitary_df['Cavitary'] = Cavitary_df.apply(func, axis=1)
Cavitary_df = Cavitary_df.reset_index()
Cavitary_df = Cavitary_df.drop_duplicates(subset=['Index', 'Radiology Type', 'Date', ], keep='first')
Cavitary_df = Cavitary_df.set_index('Index')
Cavitary_df= Cavitary_df.drop(['Cavitary Count', 'Rank'], axis=1)

def func(c):
    if c['Cavitary'] == 'Diffuse Cavitary':
        return 'n/a'
    else:
        return c['Focal Location']

Cavitary_df['Focal Location'] = Cavitary_df.apply(func, axis=1)
Cavitary_df = Cavitary_df.drop(['Cavitary Count', 'Rank'])
Cavitary_df1 = Cavitary_df
Cavitary_df['Date of first Dx'] = NTB_diagnosis_mindate['Date of first Dx']
Cavitary_df = Cavitary_df.reset_index()
Cavitary_df['Difference' ] = ((Cavitary_df['Date'] - Cavitary_df['Date of first Dx']).dt.days)
Cavitary_CT = Cavitary_df.loc[(Cavitary_df['Radiology Type'] == 'CT')]
Cavitary_CT = Cavitary_CT.loc[(Cavitary_CT['Cavitary'] != 'Cavitary NOS')]
Cavitary_CT_baseline = Cavitary_CT.loc[(Cavitary_CT['Difference'] <= 365)&(Cavitary_CT['Difference'] >= -730)]
Cavitary_CT_baseline = Cavitary_CT_baseline.loc[Cavitary_CT_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Cavitary_CXR = Cavitary_df.loc[(Cavitary_df['Radiology Type'] == 'CXR')]
Cavitary_CXR = Cavitary_CXR.loc[(Cavitary_CXR['Cavitary'] != 'Cavitary NOS')]
Cavitary_CXR_baseline = Cavitary_CXR.loc[(Cavitary_CXR['Difference'] <= 365)&(Cavitary_CXR['Difference'] >= -730)]
Cavitary_CXR_baseline = Cavitary_CXR_baseline.loc[Cavitary_CXR_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Cavitary_nos = Cavitary_df.loc[(Cavitary_df['Cavitary'] == 'Cavitary NOS')]
Cavitary_nos_baseline = Cavitary_nos.loc[(Cavitary_nos['Difference'] <= 365)& (Cavitary_nos['Difference'] >= -730)]
Cavitary_nos_baseline = Cavitary_nos_baseline.loc[Cavitary_nos_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Cavitary_nos_baseline = Cavitary_nos_baseline.loc[(Cavitary_nos_baseline['Radiology Type'] == 'CXR')|(Cavitary_nos_baseline['Radiology Type'] == 'CT')]
Cavitary_CT_baseline = Cavitary_CT_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Cavitary_CT_baseline = Cavitary_CT_baseline.rename(columns={"Cavitary": "CT Cavitary Baseline", "Date": "Cavitary CT Baseline Date", 'Focal Location':'CT Cavitary Location Baseline'})
Cavitary_baseline = Cavitary_CT_baseline.join(Cavitary_CXR_baseline, how='outer')
Cavitary_baseline = Cavitary_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Cavitary_baseline = Cavitary_baseline.rename(columns={"Cavitary": "CXR Cavitary Baseline", "Date": "Cavitary CXR Baseline Date", 'Focal Location':'CXR Cavitary Location Baseline'})
Cavitary_nos_baseline = Cavitary_nos_baseline.drop(['Difference', 'Date of first Dx'], axis=1)
Cavitary_nos_baseline = Cavitary_nos_baseline.rename(columns={"Cavitary": "Cavitary Baseline-NOS", "Date": "Baseline Date-Cavitary NOS", 'Radiology Type':'Radiology Type-Cavitary NOS(Baseline)'})
Cavitary_baseline = Cavitary_baseline.join(Cavitary_nos_baseline, how='outer')
Cavitary_baseline = Cavitary_baseline.drop('Focal Location', axis=1)
Cavitary_baseline

Cavitary_df1 = Cavitary_df1.drop('Date of first Dx', axis=1)
Cavitary_df1['Follow-up Date'] = Medications['Follow-up Date']
Cavitary_df1 = Cavitary_df1.reset_index()
Cavitary_df1['Difference'] = ((Cavitary_df1['Date'] - Cavitary_df1['Follow-up Date']).dt.days)
Cavitary_CT1 = Cavitary_df1.loc[(Cavitary_df1['Radiology Type'] == 'CT')]
Cavitary_CT1 = Cavitary_CT1.loc[(Cavitary_CT1['Cavitary'] != 'Cavitary NOS')]
Cavitary_CT_fu = Cavitary_CT1.loc[(Cavitary_CT1['Difference'] >= 730)]
Cavitary_CT_fu = Cavitary_CT_fu.loc[Cavitary_CT_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Cavitary_CXR1 = Cavitary_df1.loc[(Cavitary_df1['Radiology Type'] == 'CXR')]
Cavitary_CXR1 = Cavitary_CXR1.loc[(Cavitary_CXR1['Cavitary'] != 'Cavitary NOS')]
Cavitary_CXR_fu = Cavitary_CXR1.loc[(Cavitary_CXR1['Difference'] >= 730)]
Cavitary_CXR_fu = Cavitary_CXR_fu.loc[Cavitary_CXR_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Cavitary_nos1 = Cavitary_df1.loc[(Cavitary_df1['Cavitary'] == 'Cavitary NOS')]
Cavitary_nos_fu = Cavitary_nos1.loc[(Cavitary_nos1['Difference'] >= 730)]
Cavitary_nos_fu = Cavitary_nos_fu.loc[Cavitary_nos_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Cavitary_nos_fu = Cavitary_nos_fu.loc[(Cavitary_nos_fu['Radiology Type'] == 'CXR')|(Cavitary_nos_fu['Radiology Type'] == 'CT')]
Cavitary_CT_fu = Cavitary_CT_fu.drop(['Difference', 'Follow-up Date', 'Radiology Type'], axis=1)
Cavitary_CT_fu = Cavitary_CT_fu.rename(columns={"Cavitary": "CT Cavitary Follow-up", "Date": "Cavitary CT Follow-up Date", 'Focal Location':'CT Cavitary Location FU'})
Cavitary_fu = Cavitary_CT_fu.join(Cavitary_CXR_fu, how='outer')
Cavitary_fu = Cavitary_fu.drop(['Difference', 'Radiology Type'], axis=1)
Cavitary_fu = Cavitary_fu.rename(columns={"Cavitary": "CXR Cavitary Follow-up", "Date": "Cavitary CXR Follow-up Date", 'Focal Location':'CXR Cavitary Location FU'})
Cavitary_nos_fu = Cavitary_nos_fu.drop(['Difference', 'Follow-up Date'], axis=1)
Cavitary_nos_fu = Cavitary_nos_fu.rename(columns={"Cavitary": "Cavitary Follow-up-NOS", "Date": "Follow-up Date-Cavitary NOS", 'Radiology Type':'Radiology Type-Cavitary NOS(Follow-up)'})
Cavitary_fu = Cavitary_fu.join(Cavitary_nos_fu, how='outer')
Cavitary_fu = Cavitary_fu.drop(['Follow-up Date', 'Focal Location'], axis=1)
Cavitary_fu

#-----------Consolidation---------##


EMPI_consol = []
Consolidation = []
Date_consol = []
radiology_type_consol = []
focal_consol = []
pattern_consolidation = re.compile(r'(?i)(consolidation)')
pattern_noconsol = re.compile(r'(?i)(no\s.*consolidation)')
pattern_change = re.compile(r'(?i)(no\s.*(change|new).*consolidation)')
pattern_diffuse = re.compile('(?i)(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout).*consol')
pattern_diffuse1 = re.compile(r'(?i)consol.*(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout)')
pattern_focal = re.compile(r'(?i)((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex))).*?consol')
pattern_focal1 = re.compile(r'(?i)consol.*?((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex)))')


for report_rad in MedicalReport('Radiology.txt', end='[report_end]'):
        if re.search(pattern_consolidation, report_rad['Report_Text']):
            if re.search(r'HISTORY', report_rad['Report_Text']):
                matches = re.findall(r'REPORT([\s\S]+)',report_rad['Report_Text'])
                for match in matches:
                    match_consol = match.replace("\r"," ")
                    match_consol = match_consol.replace("\n"," ")
                    match_consol = match_consol.split('. ')
                    #Consolidation with 2 or more negating qualifiers
                    for sub_string in match_consol:
                        if re.search(pattern_noconsol, sub_string):
                            if sub_string.lower().count('no ') >=2:
                                if re.search(r'(?i)no\s.*?consolidation.*no\s', sub_string):
                                    sub_string_and = sub_string.split('and')
                                    for sub_str in sub_string_and:
                                        if re.search(pattern_change, sub_str):
                                            if re.search(pattern_diffuse, sub_str):
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Diffuse Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                                focal_consol.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string):
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Diffuse Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                                focal_consol.append('n/a')
                                            elif re.search(pattern_focal, sub_string):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_consol.append(match[0])
                                                    EMPI_consol.append(report_rad['EMPI'])
                                                    Consolidation.append('Focal Consolidation')
                                                    Date_consol.append(report_rad['Report_Date_Time'])
                                                    radiology_type_consol.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_consol.append(match[0])
                                                    EMPI_consol.append(report_rad['EMPI'])
                                                    Consolidation.append('Focal Consolidation')
                                                    Date_consol.append(report_rad['Report_Date_Time'])
                                                    radiology_type_consol.append(report_rad['Report_Description'])
                                            else:
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Consolidation NOS')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                                focal_consol.append('n/a')
                                        elif re.search(pattern_noconsol, sub_str):
                                            print('True Negative')
                                        elif re.search(r'(?i)consolidation', sub_str):
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Consolidation NOS')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                            focal_consol.append('n/a')
                            #group with only 1 negating qualifier
                            else:
                                #Change between negating qualifier and consol
                                if re.search(pattern_change, sub_string):
                                    if re.search(pattern_diffuse, sub_string):
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Diffuse Consolidation')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                        focal_consol.append('n/a')
                                    elif re.search(pattern_diffuse1, sub_string):
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Diffuse Consolidation')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                        focal_consol.append('n/a')
                                    elif re.search(pattern_focal, sub_string):
                                        matches = re.findall(pattern_focal, sub_string)
                                        for match in matches:
                                            focal_consol.append(match[0])
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Focal Consolidation')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                    elif re.search(pattern_focal1, sub_string):
                                        matches = re.findall(pattern_focal1, sub_string)
                                        for match in matches:
                                            focal_consol.append(match[0])
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Focal Consolidation')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                    else:
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Consolidation NOS')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                        focal_consol.append('n/a')
                                #True negative work up
                                else:
                                    split_by_delim = sub_string.split('and')
                                    for sub_string_negatives in split_by_delim:
                                        if re.search(pattern_noconsol, sub_string_negatives):
                                            print('True Negative')
                                        else:
                                            if re.search(pattern_diffuse, sub_string_negatives):
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Diffuse Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                                focal_consol.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string_negatives):
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Diffuse Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                                focal_consol.append('n/a')
                                            elif re.search(pattern_focal, sub_string_negatives):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_consol.append(match[0])
                                                    EMPI_consol.append(report_rad['EMPI'])
                                                    Consolidation.append('Focal Consolidation')
                                                    Date_consol.append(report_rad['Report_Date_Time'])
                                                    radiology_type_consol.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string_negatives):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_consol.append(match[0])
                                                    EMPI_consol.append(report_rad['EMPI'])
                                                    Consolidation.append('Focal Consolidation')
                                                    Date_consol.append(report_rad['Report_Date_Time'])
                                                    radiology_type_consol.append(report_rad['Report_Description'])
                                            elif re.search(r'(?i)consolidation', sub_string_negatives):
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Consolidation NOS')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                                focal_consol.append('n/a')
                                            # else:
                                            #     print(sub_string_negatives)
                        #Positves without negatating qualifier
                        else:
                            if re.search(r'(?i)consolidation', sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Diffuse Consolidation')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                                    focal_consol.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Diffuse Consolidation')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                                    focal_consol.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_consol.append(match[0])
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Focal Consolidation')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_consol.append(match[0])
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Focal Consolidation')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                else:
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Consolidation NOS')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                                    focal_consol.append('n/a')
            else:
                match_consol = report_rad['Report_Text'].replace("\r"," ")
                match_consol = match_consol.replace("\n"," ")
                match_consol = match_consol.split('. ')
                #Consolidation with 2 or more negating qualifiers
                for sub_string in match_consol:
                    if re.search(pattern_noconsol, sub_string):
                        if sub_string.lower().count('no ') >=2:
                            if re.search(r'(?i)no\s.*?consolidation.*no\s', sub_string):
                                sub_string_and = sub_string.split('and')
                                for sub_str in sub_string_and:
                                    if re.search(pattern_change, sub_str):
                                        if re.search(pattern_diffuse, sub_str):
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Diffuse Consolidation')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                            focal_consol.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string):
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Diffuse Consolidation')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                            focal_consol.append('n/a')
                                        elif re.search(pattern_focal, sub_string):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_consol.append(match[0])
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Focal Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_consol.append(match[0])
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Focal Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                        else:
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Consolidation NOS')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                            focal_consol.append('n/a')
                                    elif re.search(pattern_noconsol, sub_str):
                                        print('True Negative')
                                    elif re.search(r'(?i)consolidation', sub_str):
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Consolidation NOS')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                        focal_consol.append('n/a')
                        #group with only 1 negating qualifier
                        else:
                            #Change between negating qualifier and consol
                            if re.search(pattern_change, sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Diffuse Consolidation')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                                    focal_consol.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Diffuse Consolidation')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                                    focal_consol.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_consol.append(match[0])
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Focal Consolidation')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_consol.append(match[0])
                                        EMPI_consol.append(report_rad['EMPI'])
                                        Consolidation.append('Focal Consolidation')
                                        Date_consol.append(report_rad['Report_Date_Time'])
                                        radiology_type_consol.append(report_rad['Report_Description'])
                                else:
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Consolidation NOS')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                                    focal_consol.append('n/a')
                            #True negative work up
                            else:
                                split_by_delim = sub_string.split('and')
                                for sub_string_negatives in split_by_delim:
                                    if re.search(pattern_noconsol, sub_string_negatives):
                                        print('True Negative')
                                    else:
                                        if re.search(pattern_diffuse, sub_string_negatives):
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Diffuse Consolidation')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                            focal_consol.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string_negatives):
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Diffuse Consolidation')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                            focal_consol.append('n/a')
                                        elif re.search(pattern_focal, sub_string_negatives):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_consol.append(match[0])
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Focal Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string_negatives):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_consol.append(match[0])
                                                EMPI_consol.append(report_rad['EMPI'])
                                                Consolidation.append('Focal Consolidation')
                                                Date_consol.append(report_rad['Report_Date_Time'])
                                                radiology_type_consol.append(report_rad['Report_Description'])
                                        elif re.search(r'(?i)consolidation', sub_string_negatives):
                                            EMPI_consol.append(report_rad['EMPI'])
                                            Consolidation.append('Consolidation NOS')
                                            Date_consol.append(report_rad['Report_Date_Time'])
                                            radiology_type_consol.append(report_rad['Report_Description'])
                                            focal_consol.append('n/a')
                                        # else:
                                        #     print(sub_string_negatives)
                    #Positves without negatating qualifier
                    else:
                        if re.search(r'(?i)consolidation', sub_string):
                            if re.search(pattern_diffuse, sub_string):
                                EMPI_consol.append(report_rad['EMPI'])
                                Consolidation.append('Diffuse Consolidation')
                                Date_consol.append(report_rad['Report_Date_Time'])
                                radiology_type_consol.append(report_rad['Report_Description'])
                                focal_consol.append('n/a')
                            elif re.search(pattern_diffuse1, sub_string):
                                EMPI_consol.append(report_rad['EMPI'])
                                Consolidation.append('Diffuse Consolidation')
                                Date_consol.append(report_rad['Report_Date_Time'])
                                radiology_type_consol.append(report_rad['Report_Description'])
                                focal_consol.append('n/a')
                            elif re.search(pattern_focal, sub_string):
                                matches = re.findall(pattern_focal, sub_string)
                                for match in matches:
                                    focal_consol.append(match[0])
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Focal Consolidation')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                            elif re.search(pattern_focal1, sub_string):
                                matches = re.findall(pattern_focal1, sub_string)
                                for match in matches:
                                    focal_consol.append(match[0])
                                    EMPI_consol.append(report_rad['EMPI'])
                                    Consolidation.append('Focal Consolidation')
                                    Date_consol.append(report_rad['Report_Date_Time'])
                                    radiology_type_consol.append(report_rad['Report_Description'])
                            else:
                                EMPI_consol.append(report_rad['EMPI'])
                                Consolidation.append('Consolidation NOS')
                                Date_consol.append(report_rad['Report_Date_Time'])
                                radiology_type_consol.append(report_rad['Report_Description'])
                                focal_consol.append('n/a')



Consolidation_df = pd.DataFrame({'Index':EMPI_consol, 'Consolidation':Consolidation, 'Date': Date_consol, 'Radiology Type':radiology_type_consol, 'Focal Location':focal_consol})
Consolidation_df['Index'] = Consolidation_df['Index'].str.extract(r'(\d+)')
Consolidation_df['Date'] = Consolidation_df['Date'].str.extract(r'(\d+\/\d+\/\d+)')
Consolidation_df['Radiology Type'] = Consolidation_df['Radiology Type'].str.replace(r'(?i)(^.*CT.*$)', 'CT')
Consolidation_df['Radiology Type'] = Consolidation_df['Radiology Type'].str.replace(r'(?i)(^.*chest.*$)', 'CXR')
Consolidation_df['Date'] = pd.to_datetime(Consolidation_df['Date'])
Consolidation_df['Focal Location'] = Consolidation_df['Focal Location'].str.replace(r'(?i)(\s+)', ' ')
Consolidation_df['Focal Location'] = Consolidation_df['Focal Location'].str.lower()
Consolidation_df = Consolidation_df.drop_duplicates(('Index', 'Date', 'Consolidation', 'Focal Location'), keep='first')

#Consolidation_df.to_csv('/Volumes/homedir$/MAC Project/Complete Project//temp.csv')
# Consolidation_df = Consolidation_df.drop_duplicates(subset=['Radiology Type', 'Date', 'Index'], keep='first', inplace=False)

Consolidation_counts = Consolidation_df.groupby(['Index', 'Date', 'Radiology Type'])
Consolidation_counts = Consolidation_counts['Consolidation'].value_counts()
Consolidation_counts = pd.DataFrame(Consolidation_counts)
Consolidation_counts.columns = ['Consolidation Count']
Consolidation_counts = Consolidation_counts.reset_index()
Consolidation_df = Consolidation_df.merge(Consolidation_counts, how='inner')
Consolidation_df = Consolidation_df.set_index('Index')
def func(c):
    if c['Consolidation'] == 'Diffuse Consolidation':
        return 1
    elif c['Consolidation'] == 'Focal Consolidation':
        return 2
    else:
        return 3
Consolidation_df['Rank'] = Consolidation_df.apply(func, axis=1)

Consolidation_df = Consolidation_df.sort_values('Rank')

def func(c):
    if c['Consolidation'] == 'Focal Consolidation':
        if c['Consolidation Count'] == 1:
            return 'Focal Consolidation'
        elif c['Consolidation Count'] >= 2:
            return 'Diffuse Consolidation'
    else:
        return c['Consolidation']
Consolidation_df['Consolidation'] = Consolidation_df.apply(func, axis=1)
Consolidation_df = Consolidation_df.reset_index()
Consolidation_df = Consolidation_df.drop_duplicates(subset=['Index', 'Radiology Type', 'Date', ], keep='first')
Consolidation_df = Consolidation_df.set_index('Index')
Consolidation_df= Consolidation_df.drop(['Consolidation Count', 'Rank'], axis=1)

def func(c):
    if c['Consolidation'] == 'Diffuse Consolidation':
        return 'n/a'
    else:
        return c['Focal Location']

Consolidation_df['Focal Location'] = Consolidation_df.apply(func, axis=1)

Consolidation_df1 = Consolidation_df
Consolidation_df['Date of first Dx'] = NTB_diagnosis_mindate['Date of first Dx']
Consolidation_df = Consolidation_df.reset_index()
Consolidation_df['Difference' ] = ((Consolidation_df['Date'] - Consolidation_df['Date of first Dx']).dt.days)
Consolidation_CT = Consolidation_df.loc[(Consolidation_df['Radiology Type'] == 'CT')]
Consolidation_CT = Consolidation_CT.loc[(Consolidation_CT['Consolidation'] != 'Consolidation NOS')]
Consolidation_CT_baseline = Consolidation_CT.loc[(Consolidation_CT['Difference'] <= 365)&(Consolidation_CT['Difference'] >= -730)]
Consolidation_CT_baseline = Consolidation_CT_baseline.loc[Consolidation_CT_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Consolidation_CXR = Consolidation_df.loc[(Consolidation_df['Radiology Type'] == 'CXR')]
Consolidation_CXR = Consolidation_CXR.loc[(Consolidation_CXR['Consolidation'] != 'Consolidation NOS')]
Consolidation_CXR_baseline = Consolidation_CXR.loc[(Consolidation_CXR['Difference'] <= 365)&(Consolidation_CXR['Difference'] >= -730)]
Consolidation_CXR_baseline = Consolidation_CXR_baseline.loc[Consolidation_CXR_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Consolidation_nos = Consolidation_df.loc[(Consolidation_df['Consolidation'] == 'Consolidation NOS')]
Consolidation_nos_baseline = Consolidation_nos.loc[(Consolidation_nos['Difference'] <= 365)& (Consolidation_nos['Difference'] >= -730)]
Consolidation_nos_baseline = Consolidation_nos_baseline.loc[Consolidation_nos_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Consolidation_nos_baseline = Consolidation_nos_baseline.loc[(Consolidation_nos_baseline['Radiology Type'] == 'CXR')|(Consolidation_nos_baseline['Radiology Type'] == 'CT')]
Consolidation_CT_baseline = Consolidation_CT_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Consolidation_CT_baseline = Consolidation_CT_baseline.rename(columns={"Consolidation": "CT Consolidation Baseline", "Date": "Consolidation CT Baseline Date", 'Focal Location':'CT Consolidation Location Baseline'})
Consolidation_baseline = Consolidation_CT_baseline.join(Consolidation_CXR_baseline, how='outer')
Consolidation_baseline = Consolidation_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Consolidation_baseline = Consolidation_baseline.rename(columns={"Consolidation": "CXR Consolidation Baseline", "Date": "Consolidation CXR Baseline Date", 'Focal Location':'CXR Consolidation Location Baseline'})
Consolidation_nos_baseline = Consolidation_nos_baseline.drop(['Difference', 'Date of first Dx'], axis=1)
Consolidation_nos_baseline = Consolidation_nos_baseline.rename(columns={"Consolidation": "Consolidation Baseline-NOS", "Date": "Baseline Date-Consolidation NOS", 'Radiology Type':'Radiology Type-Consolidation NOS(Baseline)'})
Consolidation_baseline = Consolidation_baseline.join(Consolidation_nos_baseline, how='outer')
Consolidation_baseline = Consolidation_baseline.drop('Focal Location', axis=1)
Consolidation_baseline



Consolidation_df1 = Consolidation_df1.drop('Date of first Dx', axis=1)
Consolidation_df1['Follow-up Date'] = Medications['Follow-up Date']
Consolidation_df1 = Consolidation_df1.reset_index()
Consolidation_df1['Difference'] = ((Consolidation_df1['Date'] - Consolidation_df1['Follow-up Date']).dt.days)
Consolidation_CT1 = Consolidation_df1.loc[(Consolidation_df1['Radiology Type'] == 'CT')]
Consolidation_CT1 = Consolidation_CT1.loc[(Consolidation_CT1['Consolidation'] != 'Consolidation NOS')]
Consolidation_CT_fu = Consolidation_CT1.loc[(Consolidation_CT1['Difference'] >= 730)]
Consolidation_CT_fu = Consolidation_CT_fu.loc[Consolidation_CT_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Consolidation_CXR1 = Consolidation_df1.loc[(Consolidation_df1['Radiology Type'] == 'CXR')]
Consolidation_CXR1 = Consolidation_CXR1.loc[(Consolidation_CXR1['Consolidation'] != 'Consolidation NOS')]
Consolidation_CXR_fu = Consolidation_CXR1.loc[(Consolidation_CXR1['Difference'] >= 730)]
Consolidation_CXR_fu = Consolidation_CXR_fu.loc[Consolidation_CXR_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Consolidation_nos1 = Consolidation_df1.loc[(Consolidation_df1['Consolidation'] == 'Consolidation NOS')]
Consolidation_nos_fu = Consolidation_nos1.loc[(Consolidation_nos1['Difference'] >= 730)]
Consolidation_nos_fu = Consolidation_nos_fu.loc[Consolidation_nos_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Consolidation_nos_fu = Consolidation_nos_fu.loc[(Consolidation_nos_fu['Radiology Type'] == 'CXR')|(Consolidation_nos_fu['Radiology Type'] == 'CT')]
Consolidation_CT_fu = Consolidation_CT_fu.drop(['Difference', 'Follow-up Date', 'Radiology Type'], axis=1)
Consolidation_CT_fu = Consolidation_CT_fu.rename(columns={"Consolidation": "CT Consolidation Follow-up", "Date": "Consolidation CT Follow-up Date", 'Focal Location':'CT Consolidation Location FU'})
Consolidation_fu = Consolidation_CT_fu.join(Consolidation_CXR_fu, how='outer')
Consolidation_fu = Consolidation_fu.drop(['Difference', 'Radiology Type'], axis=1)
Consolidation_fu = Consolidation_fu.rename(columns={"Consolidation": "CXR Consolidation Follow-up", "Date": "Consolidation CXR Follow-up Date", 'Focal Location':'CXR Consolidation Location FU'})
Consolidation_nos_fu = Consolidation_nos_fu.drop(['Difference', 'Follow-up Date'], axis=1)
Consolidation_nos_fu = Consolidation_nos_fu.rename(columns={"Consolidation": "Consolidation Follow-up-NOS", "Date": "Follow-up Date-Consolidation NOS", 'Radiology Type':'Radiology Type-Consolidation NOS(Follow-up)'})
Consolidation_fu = Consolidation_fu.join(Consolidation_nos_fu, how='outer')
Consolidation_fu = Consolidation_fu.drop(['Follow-up Date', 'Focal Location'], axis=1)
Consolidation_fu
#Consolidation_fu.to_csv('/Volumes/homedir$/MAC Project/Complete Project//temp.csv')



####---------Nodular opacity--------#

EMPI_nodule = []
Nodule = []
Date_nodule = []
radiology_type_nodule = []
focal_nodule = []
pattern_nodule = re.compile(r'(?i)(nodular opacity)')
pattern_nonodule = re.compile(r'(?i)(no\s.*nodular opacity)')
pattern_change = re.compile(r'(?i)(no\s.*(change|new).*nodular_opacity)')
pattern_diffuse = re.compile('(?i)(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout).*nodular opacit')
pattern_diffuse1 = re.compile(r'(?i)nodular opacit.*(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout)')
pattern_focal = re.compile(r'(?i)((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex))).*?nodular opacit')
pattern_focal1 = re.compile(r'(?i)nodular opacit.*((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex)))')


for report_rad in MedicalReport('Radiology.txt', end='[report_end]'):
        if re.search(pattern_nodule, report_rad['Report_Text']):
            if re.search(r'HISTORY', report_rad['Report_Text']):
                matches = re.findall(r'REPORT([\s\S]+)',report_rad['Report_Text'])
                for match in matches:
                    match_nodule = match.replace("\r"," ")
                    match_nodule = match_nodule.replace("\n"," ")
                    match_nodule = match_nodule.split('. ')
                    #Nodular opacity with 2 or more negating qualifiers
                    for sub_string in match_nodule:
                        if re.search(pattern_nonodule, sub_string):
                            if sub_string.lower().count('no ') >=2:
                                if re.search(r'(?i)no\s.*?nodular opacit.*no\s', sub_string):
                                    sub_string_and = sub_string.split('and')
                                    for sub_str in sub_string_and:
                                        if re.search(pattern_change, sub_str):
                                            if re.search(pattern_diffuse, sub_str):
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Diffuse Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                                focal_nodule.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string):
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Diffuse Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                                focal_nodule.append('n/a')
                                            elif re.search(pattern_focal, sub_string):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_nodule.append(match[0])
                                                    EMPI_nodule.append(report_rad['EMPI'])
                                                    Nodule.append('Focal Nodular opacity')
                                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_nodule.append(match[0])
                                                    EMPI_nodule.append(report_rad['EMPI'])
                                                    Nodule.append('Focal Nodular opacity')
                                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                            else:
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Nodular opacity NOS')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                                focal_nodule.append('n/a')
                                        elif re.search(pattern_nonodule, sub_str):
                                            print('True Negative')
                                        elif re.search(r'(?i)nodular opacity', sub_str):
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Nodular opacity NOS')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                            focal_nodule.append('n/a')
                            #group with only 1 negating qualifier
                            else:
                                #Change between negating qualifier and nodule
                                if re.search(pattern_change, sub_string):
                                    if re.search(pattern_diffuse, sub_string):
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Diffuse Nodular opacity')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                        focal_nodule.append('n/a')
                                    elif re.search(pattern_diffuse1, sub_string):
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Diffuse Nodular opacity')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                        focal_nodule.append('n/a')
                                    elif re.search(pattern_focal, sub_string):
                                        matches = re.findall(pattern_focal, sub_string)
                                        for match in matches:
                                            focal_nodule.append(match[0])
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Focal Nodular opacity')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                    elif re.search(pattern_focal1, sub_string):
                                        matches = re.findall(pattern_focal1, sub_string)
                                        for match in matches:
                                            focal_nodule.append(match[0])
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Focal Nodular opacity')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                    else:
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Nodular opacity NOS')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                        focal_nodule.append('n/a')
                                #True negative work up
                                else:
                                    split_by_delim = sub_string.split('and')
                                    for sub_string_negatives in split_by_delim:
                                        if re.search(pattern_nonodule, sub_string_negatives):
                                            print('True Negative')
                                        else:
                                            if re.search(pattern_diffuse, sub_string_negatives):
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Diffuse Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                                focal_nodule.append('n/a')
                                            elif re.search(pattern_diffuse1, sub_string_negatives):
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Diffuse Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                                focal_nodule.append('n/a')
                                            elif re.search(pattern_focal, sub_string_negatives):
                                                matches = re.findall(pattern_focal, sub_string)
                                                for match in matches:
                                                    focal_nodule.append(match[0])
                                                    EMPI_nodule.append(report_rad['EMPI'])
                                                    Nodule.append('Focal Nodular opacity')
                                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                            elif re.search(pattern_focal1, sub_string_negatives):
                                                matches = re.findall(pattern_focal1, sub_string)
                                                for match in matches:
                                                    focal_nodule.append(match[0])
                                                    EMPI_nodule.append(report_rad['EMPI'])
                                                    Nodule.append('Focal Nodular opacity')
                                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                            elif re.search(r'(?i)nodular opacity', sub_string_negatives):
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Nodular opacity NOS')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                                focal_nodule.append('n/a')
                                            # else:
                                            #     print(sub_string_negatives)
                        #Positves without negatating qualifier
                        else:
                            if re.search(r'(?i)nodular opacity', sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Diffuse Nodular opacity')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                    focal_nodule.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Diffuse Nodular opacity')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                    focal_nodule.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_nodule.append(match[0])
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Focal Nodular opacity')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_nodule.append(match[0])
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Focal Nodular opacity')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                else:
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Nodular opacity NOS')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                    focal_nodule.append('n/a')
            else:
                match_nodule = report_rad['Report_Text'].replace("\r"," ")
                match_nodule = match_nodule.replace("\n"," ")
                match_nodule = match_nodule.split('. ')
                #Nodular opacity with 2 or more negating qualifiers
                for sub_string in match_nodule:
                    if re.search(pattern_nonodule, sub_string):
                        if sub_string.lower().count('no ') >=2:
                            if re.search(r'(?i)no\s.*?nodular opacity.*no\s', sub_string):
                                sub_string_and = sub_string.split('and')
                                for sub_str in sub_string_and:
                                    if re.search(pattern_change, sub_str):
                                        if re.search(pattern_diffuse, sub_str):
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Diffuse Nodular opacity')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                            focal_nodule.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string):
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Diffuse Nodular opacity')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                            focal_nodule.append('n/a')
                                        elif re.search(pattern_focal, sub_string):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_nodule.append(match[0])
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Focal Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_nodule.append(match[0])
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Focal Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                        else:
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Nodular opacity NOS')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                            focal_nodule.append('n/a')
                                    elif re.search(pattern_nonodule, sub_str):
                                        print('True Negative')
                                    elif re.search(r'(?i)nodular opacity', sub_str):
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Nodular opacity NOS')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                        focal_nodule.append('n/a')
                        #group with only 1 negating qualifier
                        else:
                            #Change between negating qualifier and nodule
                            if re.search(pattern_change, sub_string):
                                if re.search(pattern_diffuse, sub_string):
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Diffuse Nodular opacity')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                    focal_nodule.append('n/a')
                                elif re.search(pattern_diffuse1, sub_string):
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Diffuse Nodular opacity')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                    focal_nodule.append('n/a')
                                elif re.search(pattern_focal, sub_string):
                                    matches = re.findall(pattern_focal, sub_string)
                                    for match in matches:
                                        focal_nodule.append(match[0])
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Focal Nodular opacity')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                elif re.search(pattern_focal1, sub_string):
                                    matches = re.findall(pattern_focal1, sub_string)
                                    for match in matches:
                                        focal_nodule.append(match[0])
                                        EMPI_nodule.append(report_rad['EMPI'])
                                        Nodule.append('Focal Nodular opacity')
                                        Date_nodule.append(report_rad['Report_Date_Time'])
                                        radiology_type_nodule.append(report_rad['Report_Description'])
                                else:
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Nodular opacity NOS')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                                    focal_nodule.append('n/a')
                            #True negative work up
                            else:
                                split_by_delim = sub_string.split('and')
                                for sub_string_negatives in split_by_delim:
                                    if re.search(pattern_nonodule, sub_string_negatives):
                                        print('True Negative')
                                    else:
                                        if re.search(pattern_diffuse, sub_string_negatives):
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Diffuse Nodular opacity')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                            focal_nodule.append('n/a')
                                        elif re.search(pattern_diffuse1, sub_string_negatives):
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Diffuse Nodular opacity')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                            focal_nodule.append('n/a')
                                        elif re.search(pattern_focal, sub_string_negatives):
                                            matches = re.findall(pattern_focal, sub_string)
                                            for match in matches:
                                                focal_nodule.append(match[0])
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Focal Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                        elif re.search(pattern_focal1, sub_string_negatives):
                                            matches = re.findall(pattern_focal1, sub_string)
                                            for match in matches:
                                                focal_nodule.append(match[0])
                                                EMPI_nodule.append(report_rad['EMPI'])
                                                Nodule.append('Focal Nodular opacity')
                                                Date_nodule.append(report_rad['Report_Date_Time'])
                                                radiology_type_nodule.append(report_rad['Report_Description'])
                                        elif re.search(r'(?i)nodular opacity', sub_string_negatives):
                                            EMPI_nodule.append(report_rad['EMPI'])
                                            Nodule.append('Nodular opacity NOS')
                                            Date_nodule.append(report_rad['Report_Date_Time'])
                                            radiology_type_nodule.append(report_rad['Report_Description'])
                                            focal_nodule.append('n/a')
                                        # else:
                                        #     print(sub_string_negatives)
                    #Positves without negatating qualifier
                    else:
                        if re.search(r'(?i)nodular opacity', sub_string):
                            if re.search(pattern_diffuse, sub_string):
                                EMPI_nodule.append(report_rad['EMPI'])
                                Nodule.append('Diffuse Nodular opacity')
                                Date_nodule.append(report_rad['Report_Date_Time'])
                                radiology_type_nodule.append(report_rad['Report_Description'])
                                focal_nodule.append('n/a')
                            elif re.search(pattern_diffuse1, sub_string):
                                EMPI_nodule.append(report_rad['EMPI'])
                                Nodule.append('Diffuse Nodular opacity')
                                Date_nodule.append(report_rad['Report_Date_Time'])
                                radiology_type_nodule.append(report_rad['Report_Description'])
                                focal_nodule.append('n/a')
                            elif re.search(pattern_focal, sub_string):
                                matches = re.findall(pattern_focal, sub_string)
                                for match in matches:
                                    focal_nodule.append(match[0])
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Focal Nodular opacity')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                            elif re.search(pattern_focal1, sub_string):
                                matches = re.findall(pattern_focal1, sub_string)
                                for match in matches:
                                    focal_nodule.append(match[0])
                                    EMPI_nodule.append(report_rad['EMPI'])
                                    Nodule.append('Focal Nodular opacity')
                                    Date_nodule.append(report_rad['Report_Date_Time'])
                                    radiology_type_nodule.append(report_rad['Report_Description'])
                            else:
                                EMPI_nodule.append(report_rad['EMPI'])
                                Nodule.append('Nodular opacity NOS')
                                Date_nodule.append(report_rad['Report_Date_Time'])
                                radiology_type_nodule.append(report_rad['Report_Description'])
                                focal_nodule.append('n/a')



Nodular_opacity_df = pd.DataFrame({'Index':EMPI_nodule, 'Nodular opacity':Nodule, 'Date': Date_nodule, 'Radiology Type':radiology_type_nodule, 'Focal Location':focal_nodule})
Nodular_opacity_df['Index'] = Nodular_opacity_df['Index'].str.extract(r'(\d+)')
Nodular_opacity_df['Date'] = Nodular_opacity_df['Date'].str.extract(r'(\d+\/\d+\/\d+)')
Nodular_opacity_df['Radiology Type'] = Nodular_opacity_df['Radiology Type'].str.replace(r'(?i)(^.*CT.*$)', 'CT')
Nodular_opacity_df['Radiology Type'] = Nodular_opacity_df['Radiology Type'].str.replace(r'(?i)(^.*chest.*$)', 'CXR')
Nodular_opacity_df['Date'] = pd.to_datetime(Nodular_opacity_df['Date'])
Nodular_opacity_df['Focal Location'] = Nodular_opacity_df['Focal Location'].str.replace(r'(?i)(\s+)', ' ')
Nodular_opacity_df['Focal Location'] = Nodular_opacity_df['Focal Location'].str.lower()
Nodular_opacity_df = Nodular_opacity_df.drop_duplicates(('Index', 'Date', 'Nodular opacity', 'Focal Location'), keep='first')

#Nodular_opacity_df.to_csv('/Volumes/homedir$/MAC Project/Complete Project//temp.csv')
# Nodular_opacity_df = Nodular_opacity_df.drop_duplicates(subset=['Radiology Type', 'Date', 'Index'], keep='first', inplace=False)

Nodular_opacity_counts = Nodular_opacity_df.groupby(['Index', 'Date', 'Radiology Type'])
Nodular_opacity_counts = Nodular_opacity_counts['Nodular opacity'].value_counts()
Nodular_opacity_counts = pd.DataFrame(Nodular_opacity_counts)
Nodular_opacity_counts.columns = ['Nodular opacity Count']
Nodular_opacity_counts = Nodular_opacity_counts.reset_index()
Nodular_opacity_df = Nodular_opacity_df.merge(Nodular_opacity_counts, how='inner')
Nodular_opacity_df = Nodular_opacity_df.set_index('Index')
def func(c):
    if c['Nodular opacity'] == 'Diffuse Nodular opacity':
        return 1
    elif c['Nodular opacity'] == 'Focal Nodular opacity':
        return 2
    else:
        return 3
Nodular_opacity_df['Rank'] = Nodular_opacity_df.apply(func, axis=1)

Nodular_opacity_df = Nodular_opacity_df.sort_values('Rank')

def func(c):
    if c['Nodular opacity'] == 'Focal Nodular opacity':
        if c['Nodular opacity Count'] == 1:
            return 'Focal Nodular opacity'
        elif c['Nodular opacity Count'] >= 2:
            return 'Diffuse Nodular opacity'
    else:
        return c['Nodular opacity']
Nodular_opacity_df['Nodular opacity'] = Nodular_opacity_df.apply(func, axis=1)
Nodular_opacity_df = Nodular_opacity_df.reset_index()
Nodular_opacity_df = Nodular_opacity_df.drop_duplicates(subset=['Index', 'Radiology Type', 'Date', ], keep='first')
Nodular_opacity_df = Nodular_opacity_df.set_index('Index')

Nodular_opacity_df= Nodular_opacity_df.drop(['Nodular opacity Count', 'Rank'], axis=1)

def func(c):
    if c['Nodular opacity'] == 'Diffuse Nodular opacity':
        return 'n/a'
    else:
        return c['Focal Location']

Nodular_opacity_df['Focal Location'] = Nodular_opacity_df.apply(func, axis=1)


Nodular_opacity_df1 = Nodular_opacity_df
Nodular_opacity_df['Date of first Dx'] = NTB_diagnosis_mindate['Date of first Dx']
Nodular_opacity_df = Nodular_opacity_df.reset_index()
Nodular_opacity_df['Difference' ] = ((Nodular_opacity_df['Date'] - Nodular_opacity_df['Date of first Dx']).dt.days)
Nodular_opacity_CT = Nodular_opacity_df.loc[(Nodular_opacity_df['Radiology Type'] == 'CT')]
Nodular_opacity_CT = Nodular_opacity_CT.loc[(Nodular_opacity_CT['Nodular opacity'] != 'Nodular opacity NOS')]
Nodular_opacity_CT
Nodular_opacity_CT_baseline = Nodular_opacity_CT.loc[(Nodular_opacity_CT['Difference'] <= 365)&(Nodular_opacity_CT['Difference'] >= -730)]
Nodular_opacity_CT_baseline = Nodular_opacity_CT_baseline.loc[Nodular_opacity_CT_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Nodular_opacity_CXR = Nodular_opacity_df.loc[(Nodular_opacity_df['Radiology Type'] == 'CXR')]
Nodular_opacity_CXR = Nodular_opacity_CXR.loc[(Nodular_opacity_CXR['Nodular opacity'] != 'Nodular opacity NOS')]
Nodular_opacity_CXR_baseline = Nodular_opacity_CXR.loc[(Nodular_opacity_CXR['Difference'] <= 365)&(Nodular_opacity_CXR['Difference'] >= -730)]
Nodular_opacity_CXR_baseline = Nodular_opacity_CXR_baseline.loc[Nodular_opacity_CXR_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Nodular_opacity_nos = Nodular_opacity_df.loc[(Nodular_opacity_df['Nodular opacity'] == 'Nodular opacity NOS')]
Nodular_opacity_nos_baseline = Nodular_opacity_nos.loc[(Nodular_opacity_nos['Difference'] <= 365)& (Nodular_opacity_nos['Difference'] >= -730)]
Nodular_opacity_nos_baseline = Nodular_opacity_nos_baseline.loc[Nodular_opacity_nos_baseline.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Nodular_opacity_nos_baseline = Nodular_opacity_nos_baseline.loc[(Nodular_opacity_nos_baseline['Radiology Type'] == 'CXR')|(Nodular_opacity_nos_baseline['Radiology Type'] == 'CT')]
Nodular_opacity_CT_baseline = Nodular_opacity_CT_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Nodular_opacity_CT_baseline = Nodular_opacity_CT_baseline.rename(columns={"Nodular opacity": "CT Nodular opacity Baseline", "Date": "Nodular Opactiy CT Baseline Date", 'Focal Location':'CT Nodular opacity Location Baseline'})
Nodular_opacity_baseline = Nodular_opacity_CT_baseline.join(Nodular_opacity_CXR_baseline, how='outer')
Nodular_opacity_baseline = Nodular_opacity_baseline.drop(['Difference', 'Date of first Dx', 'Radiology Type'], axis=1)
Nodular_opacity_baseline = Nodular_opacity_baseline.rename(columns={"Nodular opacity": "CXR Nodular opacity Baseline", "Date": "Nodular opacity CXR Baseline Date", 'Focal Location':'CXR Nodular opacity Location Baseline'})
Nodular_opacity_nos_baseline = Nodular_opacity_nos_baseline.drop(['Difference', 'Date of first Dx'], axis=1)
Nodular_opacity_nos_baseline = Nodular_opacity_nos_baseline.rename(columns={"Nodular opacity": "Nodular opacity Baseline-NOS", "Date": "Baseline Date-Nodular opacity NOS", 'Radiology Type':'Radiology Type-Nodular opacity NOS(Baseline)'})
Nodular_opacity_baseline = Nodular_opacity_baseline.join(Nodular_opacity_nos_baseline, how='outer')
Nodular_opacity_baseline = Nodular_opacity_baseline.drop('Focal Location', axis=1)
Nodular_opacity_baseline


Nodular_opacity_df1 = Nodular_opacity_df1.drop('Date of first Dx', axis=1)
Nodular_opacity_df1['Follow-up Date'] = Medications['Follow-up Date']
Nodular_opacity_df1 = Nodular_opacity_df1.reset_index()
Nodular_opacity_df1['Difference'] = ((Nodular_opacity_df1['Date'] - Nodular_opacity_df1['Follow-up Date']).dt.days)
Nodular_opacity_CT1 = Nodular_opacity_df1.loc[(Nodular_opacity_df1['Radiology Type'] == 'CT')]
Nodular_opacity_CT1 = Nodular_opacity_CT1.loc[(Nodular_opacity_CT1['Nodular opacity'] != 'Nodular opacity NOS')]
Nodular_opacity_CT_fu = Nodular_opacity_CT1.loc[(Nodular_opacity_CT1['Difference'] >= 730)]
Nodular_opacity_CT_fu = Nodular_opacity_CT_fu.loc[Nodular_opacity_CT_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Nodular_opacity_CXR1 = Nodular_opacity_df1.loc[(Nodular_opacity_df1['Radiology Type'] == 'CXR')]
Nodular_opacity_CXR1 = Nodular_opacity_CXR1.loc[(Nodular_opacity_CXR1['Nodular opacity'] != 'Nodular opacity NOS')]
Nodular_opacity_CXR_fu = Nodular_opacity_CXR1.loc[(Nodular_opacity_CXR1['Difference'] >= 730)]
Nodular_opacity_CXR_fu = Nodular_opacity_CXR_fu.loc[Nodular_opacity_CXR_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Nodular_opacity_nos1 = Nodular_opacity_df1.loc[(Nodular_opacity_df1['Nodular opacity'] == 'Nodular opacity NOS')]
Nodular_opacity_nos_fu = Nodular_opacity_nos1.loc[(Nodular_opacity_nos1['Difference'] >= 730)]
Nodular_opacity_nos_fu = Nodular_opacity_nos_fu.loc[Nodular_opacity_nos_fu.groupby(['Index'])['Difference'].idxmin()].set_index(['Index'])
Nodular_opacity_nos_fu = Nodular_opacity_nos_fu.loc[(Nodular_opacity_nos_fu['Radiology Type'] == 'CXR')|(Nodular_opacity_nos_fu['Radiology Type'] == 'CT')]
Nodular_opacity_CT_fu = Nodular_opacity_CT_fu.drop(['Difference', 'Follow-up Date', 'Radiology Type'], axis=1)
Nodular_opacity_CT_fu = Nodular_opacity_CT_fu.rename(columns={"Nodular opacity": "CT Nodular opacity Follow-up", "Date": "Nodular opacity CT Follow-up Date", 'Focal Location':'CT Nodular opacity Location FU'})
Nodular_opacity_fu = Nodular_opacity_CT_fu.join(Nodular_opacity_CXR_fu, how='outer')
Nodular_opacity_fu = Nodular_opacity_fu.drop(['Difference', 'Radiology Type'], axis=1)
Nodular_opacity_fu = Nodular_opacity_fu.rename(columns={"Nodular opacity": "CXR Nodular opacity Follow-up", "Date": "Nodular opacity CXR Follow-up Date", 'Focal Location':'CXR Nodular opacity Location FU'})
Nodular_opacity_nos_fu = Nodular_opacity_nos_fu.drop(['Difference', 'Follow-up Date'], axis=1)
Nodular_opacity_nos_fu = Nodular_opacity_nos_fu.rename(columns={"Nodular opacity": "Nodular opacity Follow-up-NOS", "Date": "Follow-up Date-Nodular opacity NOS", 'Radiology Type':'Radiology Type-Nodular opacity NOS(Follow-up)'})
Nodular_opacity_fu = Nodular_opacity_fu.join(Nodular_opacity_nos_fu, how='outer')
Nodular_opacity_fu = Nodular_opacity_fu.drop(['Follow-up Date', 'Focal Location'], axis=1)

#Nodular_opacity_fu.to_csv('/Volumes/homedir$/MAC Project/Complete Project//temp.csv')
#---------------Radiology Impression--------------#

EMPI_impression = []
impression = []
Date_impression = []
radiology_type_impression = []
focal_impression = []
pattern_noimpression = re.compile(r'(?i)(no\s.*(cavi|bronchiec|consolidation|nodular\s*opacit))')
pattern_change = re.compile(r'(?i)(no\s.*(change).*(cavi|bronchiec|consolidation|nodular\s*opacit))')
pattern_unchanged = re.compile(r'(?i)(cavi|bronchiec|consolidation|nodular\s*opacit).*(unchanged|stable|persistent)')
pattern_unchanged1 = re.compile(r'(?i)(unchanged|stable|persistent).*(cavi|bronchiec|consolidation|nodular\s*opacit)')
pattern_diffuse = re.compile('(?i)(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout).*cavi')
pattern_diffuse1 = re.compile(r'(?i)cavi.*(((right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper).*and.*(right|left|mid|central|basal|bi|upper|RUL|RML|RLL|LUL|LLL|lingula|lower|upper))|biapical|bibasil|diffuse|extensive|bilateral|many|both|widespread|extensive|multifocal|bases|multilob|multiple|scattered|(left.*right)|(right.*left)|throughout)')
pattern_focal = re.compile(r'(?i)((consolidation|bronchiectasis|nodular\s*opacit|cavit).*(consolidation|bronchiectasis|nodular\s*opacit|cavit).*(consolidation|bronchiectasis|nodular\s*opacit|cavit).*(consolidation|bronchiectasis|nodular\s*opacit|cavit)|(consolidation|bronchiectasis|nodular\s*opacit|cavit).*(consolidation|bronchiectasis|nodular\s*opacit|cavit).*(consolidation|bronchiectasis|nodular\s*opacit|cavit)|(consolidation|bronchiectasis|nodular\s*opacit|cavit).*(consolidation|bronchiectasis|nodular\s*opacit|cavit)|(consolidation|bronchiectasis|nodular\s*opacit|cavit))')
pattern_focal1 = re.compile(r'(?i)cavi.*?((left|right)\s*(lower|upper|middle|lingula|apic|mid|basi|base[^l]|apex)|(RLL|RUL|RML|LUL|LLL)|lingula|middle|((left|right)\s+\S+\s+(base|apic|apex)))')
pattern_improved = re.compile(r'(?i)(improv|resolution)')
pattern_worse = re.compile(r'(?i)(wors|expand|larger|progress|increas|new)')
for report_rad in MedicalReport('Radiology.txt', end='[report_end]'):
    temp = re.findall('(Impression|IMPRESSION)([\s\S]*)', report_rad['Report_Text'])
    for match in temp:
        match_cav1 = match[1]
        match_cav1 = match_cav1.replace("\r"," ")
        match_cav1 = match_cav1.replace("\n"," ")
        match_cav1 = match_cav1.split('.')
        for string in match_cav1:
            match_cav1 = re.split(r'\s+(?=[A-Z])', string)
            for sub_string in match_cav1:
                if re.search(r'(cavi|bronchiec|consolidation|nodular\s*opacit)', sub_string):
                    if re.search(r'(?i)(recomm|advis|follow)', sub_string):
                        print('Recommendation')
                    elif re.search(pattern_noimpression, sub_string):
                        if re.search(pattern_change, sub_string):
                            matches = re.findall(pattern_focal, sub_string)
                            for match in matches:
                                focal_impression.append(match[0])
                                EMPI_impression.append(report_rad['EMPI'])
                                impression.append('No change in...')
                                Date_impression.append(report_rad['Report_Date_Time'])
                                radiology_type_impression.append(report_rad['Report_Description'])
                    elif re.search(pattern_unchanged, sub_string):
                        matches = re.findall(pattern_focal, sub_string)
                        for match in matches:
                            focal_impression.append(match[0])
                            EMPI_impression.append(report_rad['EMPI'])
                            impression.append('No change in...')
                            Date_impression.append(report_rad['Report_Date_Time'])
                            radiology_type_impression.append(report_rad['Report_Description'])
                    elif re.search(pattern_unchanged1, sub_string):
                        matches = re.findall(pattern_focal, sub_string)
                        for match in matches:
                            focal_impression.append(match[0])
                            EMPI_impression.append(report_rad['EMPI'])
                            impression.append('No change in...')
                            Date_impression.append(report_rad['Report_Date_Time'])
                            radiology_type_impression.append(report_rad['Report_Description'])
                    elif re.search(pattern_improved, sub_string):
                        matches = re.findall(pattern_focal, sub_string)
                        for match in matches:
                            focal_impression.append(match[0])
                            EMPI_impression.append(report_rad['EMPI'])
                            impression.append('Improvement in...')
                            Date_impression.append(report_rad['Report_Date_Time'])
                            radiology_type_impression.append(report_rad['Report_Description'])
                    elif re.search(pattern_worse, sub_string):
                        matches = re.findall(pattern_focal, sub_string)
                        for match in matches:
                            focal_impression.append(match[0])
                            EMPI_impression.append(report_rad['EMPI'])
                            impression.append('Worsening in...')
                            Date_impression.append(report_rad['Report_Date_Time'])
                            radiology_type_impression.append(report_rad['Report_Description'])
                    else:
                        print(sub_string)


df = pd.DataFrame({'Index':EMPI_impression, 'Impression':impression, 'Date': Date_impression, 'Radiology Type':radiology_type_impression, 'Lesion':focal_impression})
df['Date'] = df['Date'].str.extract(r'(\d+\/\d+\/\d+)')
df['Index'] = df['Index'].str.extract(r'(\d+)')
df['Radiology Type'] = df['Radiology Type'].str.replace(r'(?i)(^.*CT.*$)', 'CT')
df['Radiology Type'] = df['Radiology Type'].str.replace(r'(?i)(^.*chest.*$)', 'CXR')
df['Date'] = pd.to_datetime(df['Date'])
df['Lesion'] = df['Lesion'].str.lower()
df['Lesion'] = df['Lesion'].str.replace(r'\s+', ' ')
def func(c):
    if 'cavi' in c['Lesion'] and 'consolidation' in c['Lesion'] and 'nodular opacit' in c['Lesion'] and 'bronch' in c['Lesion']:
        return 'Cavitary, consolidation, nodular opacity, and bronchiectasis'
    elif 'cavi' in c['Lesion'] and 'consolidation' in c['Lesion'] and 'nodular opaci' in c['Lesion']:
        return 'Cavitary, consolidation, and nodular opacity'
    elif 'cavi' in c['Lesion'] and 'consolidation' in c['Lesion'] and 'bronch' in c['Lesion']:
        return 'Cavitary, consolidation, and bronchiectasis'
    elif 'cavi' in c['Lesion'] and 'nodular opacit' in c['Lesion'] and 'bronch' in c['Lesion']:
        return 'Cavitary, nodular opacity, and bronchiectasis'
    elif 'consolidation' in c['Lesion'] and 'nodular opacit' in c['Lesion'] and 'bronch' in c['Lesion']:
        return 'Consolidation, nodular opacity, and bronchiectasis'
    elif 'cavi' in c['Lesion'] and 'consolidation' in c['Lesion']:
        return 'Cavitary and consolidation'
    elif 'cavi' in c['Lesion'] and 'nodular opacit' in c['Lesion']:
        return 'Cavitary and nodular opacity'
    elif 'cavi' in c['Lesion'] and 'bronch' in c['Lesion']:
        return 'Cavitary and bronchiectasis'
    elif 'consolidation' in c['Lesion'] and 'nodular opacit' in c['Lesion']:
        return 'Consolidation and nodular opacity'
    elif 'consolidation' in c['Lesion'] and 'bronch' in c['Lesion']:
        return 'Consolidation and bronchiectasis'
    elif 'nodular opacit' in c['Lesion'] and 'bronch' in c['Lesion']:
        return 'Nodular opacity and bronchiectasis'
    elif 'cavi' in c['Lesion']:
        return 'Cavitary'
    elif 'consolidation' in c['Lesion']:
        return 'Consolidation'
    elif 'nodular opacit' in c['Lesion']:
        return 'Nodular opacity'
    elif 'bronch' in c['Lesion']:
        return 'Bronchiectasis'
df = df.set_index('Index')
df['Lesion'] = df.apply(func, axis=1)
df['Follow-up Date'] = Medications['Follow-up Date']
df = df.reset_index()
df['Difference'] = ((df['Date'] - df['Follow-up Date']).dt.days)
df_max = df.loc[df.groupby(['Index'])['Date'].idxmax()].set_index('Index')
df_max = df_max.rename(columns={"Date": "Impression Date"})
df = df_max[['Impression Date', 'Impression', 'Lesion', 'Radiology Type']]

####----------##Total Patients with CT or CXR in system
EMPI  = []
radiology_type = []
date = []

CT = re.compile(r'(?i)^.*CT.*$')
CXR = re.compile('(?i)^.*chest.*$')

for report_rad in MedicalReport('Radiology.txt', end='[report_end]'):
    if re.search(CT, report_rad['Report_Description']):
        EMPI.append(report_rad['EMPI'])
        radiology_type.append('CT')
        date.append(report_rad['Report_Date_Time'])
    elif re.search(CXR,report_rad['Report_Description']):
        EMPI.append(report_rad['EMPI'])
        radiology_type.append('CXR')
        date.append(report_rad['Report_Date_Time'])

Nodular_opacity_df = Nodular_opacity_df.reset_index()
Nodular_opacity_df['Difference' ] = ((Nodular_opacity_df['Date'] - Nodular_opacity_df['Date of first Dx']).dt.days)

total_imaging = pd.DataFrame({'Index':EMPI, 'Radiology type':radiology_type, 'Date':date})
total_imaging1 = pd.DataFrame({'Index':EMPI})
total_imaging['Index'] = total_imaging['Index'].str.extract(r'(\d+)')
total_imaging = total_imaging.set_index('Index')
total_imaging['Date of first Dx'] = NTB_diagnosis_mindate['Date of first Dx']
total_imaging = total_imaging.reset_index()
total_imaging['Date'] = pd.to_datetime(total_imaging['Date'])
total_imaging['Difference' ] = ((total_imaging['Date'] - total_imaging['Date of first Dx']).dt.days)

CT_baseline = total_imaging.loc[(total_imaging['Radiology type'] == 'CT')]
CXR_baseline = total_imaging.loc[(total_imaging['Radiology type'] == 'CXR')]

CT_baseline = CT_baseline.loc[(CT_baseline['Difference'] <= 365)&(CT_baseline['Difference'] >= -730)]
CXR_baseline = CXR_baseline.loc[(CXR_baseline['Difference'] <= 365)&(CXR_baseline['Difference'] >= -730)]
CT_baseline = CT_baseline .drop_duplicates('Index', keep='first').set_index('Index')
CXR_baseline = CXR_baseline .drop_duplicates('Index', keep='first').set_index('Index')
CXR_baseline['Baseline CXR'] = 'Yes'
CT_baseline['Baseline CT'] = 'Yes'
total_imaging1 = total_imaging1.drop_duplicates('Index', keep='first')
total_imaging1['Any CT or CXR?'] = 'Yeah'
total_imaging1 = total_imaging1.set_index('Index')

#------------------------Cardiology---------------#
# MVP = []
# MVP_EMPI = []
# MVP_Date = []
#
#
# pattern_mvp = re.compile(r'(MITRAL\sVALVE[\s\S]+?mitral\svalve\sprolapse[\s\S]+?\.)')
#
# for report in MedicalReport('Cardiology.txt', end='[report_end]'):
#     for match_MVP in pattern_mvp.findall(report['Report_Text']):
#         match_MVP = match_MVP.replace("\r"," ")
#         match_MVP = match_MVP.replace("\n"," ")
#         if 'no evidence of mitral valve prolapse' in match_MVP:
#             MVP.append('No MVP')
#             MVP_EMPI.append(report['EMPI'])
#             MVP_Date.append(report['Report_Date_Time'])
#         elif 'no significant mitral valve prolapse' in match_MVP:
#             MVP.append('No MVP')
#             MVP_EMPI.append(report['EMPI'])
#             MVP_Date.append(report['Report_Date_Time'])
#         elif 'does not meet criteria for mitral valve' in match_MVP:
#             MVP.append('No MVP')
#             MVP_EMPI.append(report['EMPI'])
#             MVP_Date.append(report['Report_Date_Time'])
#         elif 'no evidence of minimal mitral valve prolapse' in match_MVP:
#             MVP.append('No MVP')
#             MVP_EMPI.append(report['EMPI'])
#             MVP_Date.append(report['Report_Date_Time'])
#         else:
#             MVP.append('MVP Present')
#             MVP_EMPI.append(report['EMPI'])
#             MVP_Date.append(report['Report_Date_Time'])
#
#
# MVP = pd.DataFrame({'Index':MVP_EMPI, 'Date':MVP_Date, 'MVP':MVP})
# MVP['Index'] = MVP['Index'].str.extract(r'(\d+)')
# MVP['Date'] = MVP['Date'].str.extract(r'(\d+\/\d+\/\d+)')
# MVP['Date'] = pd.to_datetime(MVP['Date'])
# MVP= MVP.drop('Date', axis=1)
# MVP = MVP.drop_duplicates('Index')
# MVP = MVP.set_index(MVP['Index'])
# MVP=MVP.drop('Index', axis=1)
# MVP


#------------- Combining all dataframes together-----------#
Merged = Demographics.join(NTB_diagnosis_mindate)
Merged['BMI Baseline'] = BMI_baseline['BMI']
Merged['BMI Follow-up'] = BMI_followup['BMI']
Merged = Merged.join(Height_df, how='outer')
Merged['Smoking Status'] = Smoking_recent['Smoking Status']
Merged['Smoking Status'] = Merged['Smoking Status'].fillna(np.nan)
Merged['Positive Sputum Cultures'] = Micro_pos_inclusion['Counts SPUTUM']
Merged['Positive BAL Cultures'] = Micro_pos_inclusion['Counts BAL']
Merged['# of Cxs sent']= micro_total_cx['# of Cxs sent']
Merged = Merged.join(Micro_smear_df, how='outer')
Merged['Date of Most Recent Pos Cx'] = Micro_recent_pos_cx['Date of Most Recent Pos Cx']
Merged= Merged.join(Micro, how='outer')
Merged['Number of cultures since treatment initiation']= micro_denominator_gb['Number of cultures since treatment initiation']
Merged['Negative Cultures since Reference Date'] = micro_all_df_gb['Negative Cultures since Reference Date']
Merged['Date of Most Recent Pos Smear'] = Micro_smear_recent_pos['Date of Most Recent Pos Smear']
Merged['Date of First Pos Cx'] = Micro_first_pos_cx['Cx Date']
Merged['Date of First Pos Smear'] = Micro_first_pos_smear['Smear Date']
Merged['DST Count'] = dst_count['DST Count']
Merged['Species'] = species_gb['Species']
Merged['Coinfection'] = Coinfection['Coinfection']
#Merged['Last Date'] = Follow['Last Date']
Merged = Merged.join(Diagnosis, how='outer')
Merged = Merged.join(PFTs_combined, how='outer')
Merged = Merged.join(Medications, how='outer')
# Merged['Baseline Clarithromycin Suscestibility'] = Micro_sens_baseline['Clarithromycin Susceptibility']
# Merged['Baseline Sens Date'] = Micro_sens_baseline['Date']
# Merged['Followup Clarithromycin Susceptibility'] = Micro_sens_followup['Clarithromycin Susceptibility']
# Merged['Followup Sens Date'] = Micro_sens_followup['Date']
Merged = Merged.join(Bronchiectasis_baseline, how='outer')
Merged = Merged.join(Bronchiectasis_fu, how='outer')
Merged = Merged.join(Cavitary_baseline, how='outer')
Merged = Merged.join(Cavitary_fu, how='outer')
Merged = Merged.join(Nodular_opacity_baseline, how='outer')
Merged = Merged.join(Nodular_opacity_fu, how='outer')
Merged = Merged.join(Consolidation_baseline, how='outer')
Merged = Merged.join(Consolidation_fu, how='outer')
Merged = Merged.join(df, how='outer')
Merged = Merged.join(total_imaging1, how='outer')
Merged['Baseline CT'] = CT_baseline['Baseline CT']
Merged['Baseline CXR'] = CXR_baseline['Baseline CXR']
Merged[['GERD', 'Allergic Bronchopulmonary Aspergillosis','COPD', 'Cystic Fibrosis','HIV', 'Rheumatoid arthritis', 'Breast Cancer', 'IBD', 'Scoliosis', 'Pectus Excavatum']]= Merged[['GERD', 'Allergic Bronchopulmonary Aspergillosis','COPD','Cystic Fibrosis', 'HIV', 'Rheumatoid arthritis', 'Breast Cancer', 'IBD', 'Scoliosis', 'Pectus Excavatum']].replace(np.nan, 'Not Present')
Merged['BMI Baseline'] = Merged['BMI Baseline'].fillna(0)
Merged['BMI Follow-up'] = Merged['BMI Follow-up'].fillna(0)
Merged['Macrolide Susceptibility Conversion'] = Macrolide_conv['Macrolide Susceptibility Conversion']
def func(c):
    if c['BMI Baseline'] == 0:
        return c['Calulated BMI Baseline']
    else:
        return c['BMI Baseline']
Merged['BMI Baseline'] = Merged.apply(func, axis=1)

def func(c):
    if c['BMI Follow-up'] == 0:
        return c['Calulated BMI Follow-up']
    else:
        return c['BMI Follow-up']
Merged['BMI Follow-up'] = Merged.apply(func, axis=1)

Microbiologic_inclusion = Merged.loc[(Merged['Positive BAL Cultures'] >= 1)|(Merged['Positive Sputum Cultures'] >= 2)| ((Merged['Positive Sputum Cultures'] >= 1)& (Merged['Total Positive Smears'] >= 1)| (Merged['Surgery for MAC?'] == 'Yes')) ]
Microbiologic_inclusion = Microbiologic_inclusion.loc[(Microbiologic_inclusion['Age at the time of Dx'] >=18) ]

Microbiologic_inclusion['Microbiologic Dx Crtiera?'] = 'Microbiologic Dx Criteria Met'
Microbiologic_inclusion['MVP'] = Microbiologic_inclusion['MVP'].fillna('No MVP')


extracted = pd.read_csv('/Volumes/homedir$/MAC Project/Complete Project/Surgery Patient with extracted data.csv')
extracted['Index'] = extracted['Index'].astype(str)
extracted = extracted.set_index('Index')
extracted['Manual Baseline PFTs Date']= pd.to_datetime(extracted['Manual Baseline PFTs Date'])
extracted['Manual Follow-up PFTs Date']= pd.to_datetime(extracted['Manual Follow-up PFTs Date'])
extracted['Documentation date of symptoms'] = pd.to_datetime(extracted['Documentation date of symptoms'])

#Extra Surgery Patient Notes
Microbiologic_inclusion = Microbiologic_inclusion.join(extracted, how='outer')

Microbiologic_inclusion['Calculated BMI Baseline_manual'] = Microbiologic_inclusion['Manual Weight Baseline']/(Microbiologic_inclusion['Height'] *Microbiologic_inclusion['Height']) * 703.00
Microbiologic_inclusion['Calculated BMI Follow-up_manual'] = Microbiologic_inclusion['Manual Weight Follow-up']/(Microbiologic_inclusion['Height'] *Microbiologic_inclusion['Height']) * 703.00

Microbiologic_inclusion['BMI Baseline'] = Microbiologic_inclusion['BMI Baseline'].fillna(0)
Microbiologic_inclusion['BMI Follow-up'] = Microbiologic_inclusion['BMI Follow-up'].fillna(0)
Microbiologic_inclusion['Manual BMI Baseline'] = Microbiologic_inclusion['Manual BMI Baseline'].fillna(0)
Microbiologic_inclusion['Manual BMI Follow-up'] = Microbiologic_inclusion['Manual BMI Follow-up'].fillna(0)
def func(c):
    if c['BMI Baseline'] == 0:
        if c['Manual BMI Baseline'] != 0:
            return c['Manual BMI Baseline']
        else:
            return c['Calculated BMI Baseline_manual']
    else:
        return c['BMI Baseline']

Microbiologic_inclusion['BMI Baseline'] = Microbiologic_inclusion.apply(func, axis=1)

def func(c):
    if c['BMI Follow-up'] == 0:
        if c['Manual BMI Follow-up'] != 0:
            return c['Manual BMI Follow-up']
        else:
            return c['Calculated BMI Follow-up_manual']
    else:
        return c['BMI Follow-up']


Microbiologic_inclusion['BMI Follow-up'] = Microbiologic_inclusion.apply(func, axis=1)

Microbiologic_inclusion['Baseline % Predicted FEV1'] = Microbiologic_inclusion['Baseline % Predicted FEV1'].fillna(0)
def func(c):
    if c['Baseline % Predicted FEV1'] == 0:
        return c['Baseline % Predicted FEV1-Manual']
    else:
        return c['Baseline % Predicted FEV1']
Microbiologic_inclusion['Baseline % Predicted FEV1'] = Microbiologic_inclusion.apply(func, axis=1)

Microbiologic_inclusion['Baseline% Predicted FEV1/FVC'] = Microbiologic_inclusion['Baseline% Predicted FEV1/FVC'].fillna(0)
def func(c):
    if c['Baseline% Predicted FEV1/FVC'] == 0:
        return c['Manual Baseline % Predicted FEV1/FVC']
    else:
        return c['Baseline% Predicted FEV1/FVC']
Microbiologic_inclusion['Baseline% Predicted FEV1/FVC'] = Microbiologic_inclusion.apply(func, axis=1)

Microbiologic_inclusion['Baseline % Predicted FVC'] = Microbiologic_inclusion['Baseline % Predicted FVC'].fillna(0)
def func(c):
    if c['Baseline % Predicted FVC'] ==0:
        return c['Manual Baseline % Predicted FVC']
    else:
        return c['Baseline % Predicted FVC']
Microbiologic_inclusion['Baseline % Predicted FVC'] = Microbiologic_inclusion.apply(func, axis=1)

Microbiologic_inclusion['Baseline PFTs Date'] = Microbiologic_inclusion['Baseline PFTs Date'].fillna(0)
def func(c):
    if c['Baseline PFTs Date'] == 0:
        return c['Manual Baseline PFTs Date']
    else:
        return c['Baseline PFTs Date']
Microbiologic_inclusion['Baseline PFTs Date'] = Microbiologic_inclusion.apply(func, axis=1)

Microbiologic_inclusion['Follow-up % Predicted FEV1'] = Microbiologic_inclusion['Follow-up % Predicted FEV1'].fillna(0)
def func(c):
    if c['Follow-up % Predicted FEV1']== 0:
        return c['Follow-up % Predicted FEV1-Manual']
    else:
        return c['Follow-up % Predicted FEV1']
Microbiologic_inclusion['Follow-up % Predicted FEV1'] = Microbiologic_inclusion.apply(func, axis=1)

Microbiologic_inclusion['Follow-up % Predicted FEV1/FVC'] =Microbiologic_inclusion['Follow-up % Predicted FEV1/FVC'].fillna(0)
def func(c):
    if c['Follow-up % Predicted FEV1/FVC'] ==0:
        return c['Manual Follow-up % Predicted FEV1/FVC']
    else:
        return c['Follow-up % Predicted FEV1/FVC']
Microbiologic_inclusion['Follow-up % Predicted FEV1/FVC'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['Follow-up % Predicted FVC'] = Microbiologic_inclusion['Follow-up % Predicted FVC'].fillna(0)
def func(c):
    if c['Follow-up % Predicted FVC'] ==0:
        return c['Manual Follow-up % Predicted FVC']
    else:
        return c['Follow-up % Predicted FVC']
Microbiologic_inclusion['Follow-up % Predicted FVC'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['Follow-up PFTs Date'] = Microbiologic_inclusion['Follow-up PFTs Date'].fillna(0)
def func(c):
    if c['Follow-up PFTs Date'] ==0:
        return c['Manual Follow-up PFTs Date']
    else:
        return c['Follow-up PFTs Date']
Microbiologic_inclusion['Follow-up PFTs Date'] = Microbiologic_inclusion.apply(func, axis=1)

def func(c):
    if c['CT Bronchiectasis Baseline'] is not np.nan:
        return 'Yes'
    elif c['CT Cavitary Baseline'] is not np.nan:
        return 'Yes'
    elif c['CT Consolidation Baseline'] is not np.nan:
        return 'Yes'
    elif c['CT Nodular opacity Baseline'] is not np.nan:
        return 'Yes'
    elif c['CXR Bronchiectasis Baseline'] is not np.nan:
        return 'Yes'
    elif c['CXR Cavitary Baseline'] is not np.nan:
        return 'Yes'
    elif c['CXR Consolidation Baseline'] is not np.nan:
        return 'Yes'
    elif c['CXR Nodular opacity Baseline'] is not np.nan:
        return 'Yes'

Microbiologic_inclusion['Evidence of MAC?'] =  Microbiologic_inclusion.apply(func, axis=1)

def func(c):
    if c['species manual'] is not np.nan:
        return c['species manual']
    else:
        return c['Species']

Microbiologic_inclusion['Species'] = Microbiologic_inclusion.apply(func, axis=1)
###Time Followed

#Microbiologic_inclusion['Time followed'] = Microbiologic_inclusion['Last date'] - Microbiologic_inclusion['Date of first Dx']
#Microbiologic_inclusion['Time followed'] = Microbiologic_inclusion['Time followed'].fillna(0)
#Microbiologic_inclusion['Time followed'] = Microbiologic_inclusion['Time followed'].astype(str)
#Microbiologic_inclusion['Time followed'] = Microbiologic_inclusion['Time followed'].str.extract(r'(\d+)\sdays', expand=True)

##Microbiologic Conversion
Microbiologic_inclusion['Negative Cultures since Reference Date'] = Microbiologic_inclusion['Negative Cultures since Reference Date'].fillna(0)
Microbiologic_inclusion['Negative Cultures since Reference Date']
Microbiologic_inclusion['Number of cultures since treatment initiation']
def func(c):
    if c['Number of cultures since treatment initiation'] >=2:
        if c['Negative Cultures since Reference Date'] < 2:
            return 'No'
        else:
            return 'Yes'
    elif c['Number of cultures since treatment initiation'] ==1:
        if c['Negative Cultures since Reference Date'] < 1:
            return 'No'
        else:
            return 'Yes'
    else:
        return np.nan


Microbiologic_inclusion['Microbiologic Conversion'] = Microbiologic_inclusion.apply(func, axis=1)

###2 year mortality

Microbiologic_inclusion['Time to Mortality'] = ((Microbiologic_inclusion['Date of Death']- Microbiologic_inclusion['Date of first Dx']).fillna(0)/np.timedelta64(1, 'D')).astype(int)

Microbiologic_inclusion['Date of first Dx']
#1825
date = datetime(2016,1,1)
def func(c):
    if c['Date of first Dx'] <= datetime(2016,1,1):
        if c['Time to Mortality'] == 0:
            return 'No'
        elif c['Time to Mortality'] <= 730:
            return 'Yes'
        else:
            return 'No'
    else:
        return np.nan
Microbiologic_inclusion['5 year mortality'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['5 year mortality']

#Coding Independent variable for medication regimens

Microbiologic_inclusion['All Treatments'] = Microbiologic_inclusion['All Treatments'].astype(str)
Microbiologic_inclusion['Multiple Clarithromycin Tx courses'] = Microbiologic_inclusion['Multiple Clarithromycin Tx courses'].astype(str)
Microbiologic_inclusion['Multiple Rifampicin Tx courses'] = Microbiologic_inclusion['Multiple Rifampicin Tx courses'].astype(str)
#Microbiologic_inclusion['Multiple Rifabutin Tx courses'] = Microbiologic_inclusion['Multiple Rifabutin Tx courses'].astype(str)
Microbiologic_inclusion['Multiple Ethambutol Tx courses'] = Microbiologic_inclusion['Multiple Ethambutol Tx courses'].astype(str)
Microbiologic_inclusion['Multiple Bedaquiline Tx courses'] = Microbiologic_inclusion['Multiple Bedaqualine Tx courses'].astype(str)
Microbiologic_inclusion['Multiple Amikacin Tx courses'] = Microbiologic_inclusion['Multiple Amikacin Tx courses'].astype(str)
Microbiologic_inclusion['Multiple Clofazimine Tx courses'] = Microbiologic_inclusion['Multiple Clofazimine Tx courses'].astype(str)

Microbiologic_inclusion['MAC Treatment'] = np.nan
Microbiologic_inclusion['Species'] = Microbiologic_inclusion['Species'].astype(str)

def func(c):
    if 'MAC' in c['Species']:
        if 'thromycin' in c['All Treatments']:
            if 'ambutol' in c['All Treatments']:
                if 'Rifabutin' in  c['All Treatments'] or 'Rifampicin' in c['All Treatments']:
                    return 'Adequate'
                    # if c['Multiple Clarithromycin Tx courses'] == 'Multiple Courses' or  c['Multiple Rifampicin Tx courses'] == 'Multiple Courses' or c['Multiple Rifabutin Tx courses'] == 'Multiple Courses' or c['Multiple Ethambutol Tx courses'] == 'Multiple Courses' or c['Multiple Clofazimine Tx courses'] == 'Multiple Courses' or c['Multiple Amikacin Tx courses'] == 'Multiple Courses' or c['Multiple Bedaqualine Tx courses'] == 'Multiple Courses':
                    #     return 'Adequate Multiple'
                    # else:
                    #     return 'Adequate Single'
                elif 'Clofazimine' in c['All Treatments'] or 'Bedaqualine' in c['All Treatments'] or 'Amikacin' in c['All Treatments']:
                    return 'Adequate'
                    # if c['Multiple Clarithromycin Tx courses'] == 'Multiple Courses' or  c['Multiple Rifampicin Tx courses'] == 'Multiple Courses' or c['Multiple Rifabutin Tx courses'] == 'Multiple Courses' or c['Multiple Ethambutol Tx courses'] == 'Multiple Courses' or c['Multiple Clofazimine Tx courses'] == 'Multiple Courses' or c['Multiple Amikacin Tx courses'] == 'Multiple Courses' or c['Multiple Bedaqualine Tx courses'] == 'Multiple Courses':
                    #     return 'Adequate Multiple'
                    # else:
                    #     return 'Adequate Single'
                else:
                    return 'Inadequate'
            elif 'Rifabutin' in  c['All Treatments'] or 'Rifampicin' in c['All Treatments']:
                if 'Clofazimine' in c['All Treatments'] or 'Bedaqualine' in c['All Treatments'] or 'Amikacin' in c['All Treatments']:
                    return 'Adequate'
                    # if c['Multiple Clarithromycin Tx courses'] == 'Multiple Courses' or  c['Multiple Rifampicin Tx courses'] == 'Multiple Courses' or c['Multiple Rifabutin Tx courses'] == 'Multiple Courses' or c['Multiple Ethambutol Tx courses'] == 'Multiple Courses' or c['Multiple Clofazimine Tx courses'] == 'Multiple Courses' or c['Multiple Amikacin Tx courses'] == 'Multiple Courses' or c['Multiple Bedaqualine Tx courses'] == 'Multiple Courses':
                    #     return 'Adequate Multiple'
                    # else:
                    #     return 'Adequate Single'
                else:
                    return 'Inadequate'
            else:
                return 'Inadequate'
        elif 'ambutol' in c['All Treatments']:
            if 'Rifabutin' or 'Rifampin' or 'Rifampicin' in c['All Treatments']:
                if 'Clofazimine' in c['All Treatments'] or 'Bedaqualine' in c['All Treatments'] or 'Amikacin' in c['All Treatments']:
                    return 'Adequate'
                    # if c['Multiple Clarithromycin Tx courses'] == 'Multiple Courses' or  c['Multiple Rifampicin Tx courses'] == 'Multiple Courses' or c['Multiple Rifabutin Tx courses'] == 'Multiple Courses' or c['Multiple Ethambutol Tx courses'] == 'Multiple Courses' or c['Multiple Clofazimine Tx courses'] == 'Multiple Courses' or c['Multiple Amikacin Tx courses'] == 'Multiple Courses' or c['Multiple Bedaqualine Tx courses'] == 'Multiple Courses':
                    #     return 'Adequate Multiple'
                    # else:
                    #     return 'Adequate Single'
                else:
                    return 'Inadequate'
            else:
                return 'Inadequate'
        else:
            return 'Inadequate'
    else:
        return c['MAC Treatment']


Microbiologic_inclusion['MAC Treatment'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['All Treatments'] = Microbiologic_inclusion['All Treatments'].astype(str)

def func(c):
    if 'MAC' in c['Species']:
        if 'Clarithromycin' in c['All Treatments'] or 'ambutol' in c['All Treatments'] or  'Rifabutin' in  c['All Treatments'] or 'Rifampicin' in c['All Treatments'] or 'Clofazimine' in c['All Treatments'] or 'Bedaqualine' in c['All Treatments'] or 'Amikacin' in c['All Treatments']:
            return 'Treatment Attempt'
Microbiologic_inclusion['Treatment Attempt?'] = Microbiologic_inclusion.apply(func, axis=1)

def func(c):
    if c['All Treatments Manual'] == 'Adequate':
        return 'Adequate'
    else:
        return c['MAC Treatment']
Microbiologic_inclusion['MAC Treatment'] = Microbiologic_inclusion.apply(func, axis=1)
# def func(c):
#     if 'MAC' in c['Species']:
#         if 'Multiple Courses' in c['Multiple Clarithromycin Tx courses'] or 'Multiple Courses' in c['Multiple Azithromycin Tx courses']:
#             if 'Multiple Courses' in c['Multiple Ethambutol Tx courses']:
#                 if 'Multiple Courses' in c['Multiple Rifabutin Tx courses'] or 'Multiple Courses' in c['Multiple Rifampin Tx Courses'] or 'Multiple Courses' in c['Multiple Rifampicin Tx Courses'] :
#                     return 'Adequate Retreatment'
#                 else:
#                     return 'Inadequate'
#             else:
#                 return 'Inadequate'
#         else:
#             return 'Inadequate'
#     else:
#         return c['MAC Treatment']
#
# def func(c):
#     if 'Abscessus' in c['Species']:
#         if 'Amikacin' in c['All Treatments']:
#             if 'Imipenem' or 'Cefoxitin' or 'Tigecycline' in c['All Treatments']:
#                 return 'Adequate'
#             else:
#                 return 'Inadequate'
#         else:
#             return 'Inadequate'
#     else:
#         return c['MAC Treatment']
# Microbiologic_inclusion['MAC Treatment'] = Microbiologic_inclusion.apply(func, axis=1)
#
# def func(c):
#     if 'Kansasii' in c['Species']:
#         if 'Isoniazid' or 'thromycin' in c['All Treatments']:
#             if 'Rifabutin' or 'Rifampin' or 'Rifampicin' in c['All Treatments']:
#                 if 'Ethambutol' or 'floxacin' or 'Minocycline' or 'Bactrim':
#                     return 'Adequate'
#                 else:
#                     return 'Inadequate'
#             else:
#                 return 'Inadequate'
#         else:
#             return 'Inadequate'
#     else:
#         return c['MAC Treatment']
# Microbiologic_inclusion['MAC Treatment'] = Microbiologic_inclusion.apply(func, axis=1)
#
# Microbiologic_inclusion['MAC Treatment'] = Microbiologic_inclusion['MAC Treatment'].fillna('Inadequate')

Microbiologic_inclusion['Surgery for MAC?'] = Microbiologic_inclusion['Surgery for MAC?'].fillna('No')

#####-----Composite Dependent Variable Design-----------###
#%BMI Change
Microbiologic_inclusion['BMI Follow-up'] = Microbiologic_inclusion['BMI Follow-up'].astype(float)
Microbiologic_inclusion['BMI Baseline'] = Microbiologic_inclusion['BMI Baseline'].astype(float)

Microbiologic_inclusion['% Change in BMI'] = ((Microbiologic_inclusion['BMI Follow-up']- Microbiologic_inclusion['BMI Baseline'])/Microbiologic_inclusion['BMI Baseline'])*100


def func(c):
    if c['% Change in BMI'] <= -5:
        return '1'
    elif c['% Change in BMI'] >-5:
        return '0'
    else:
        return np.nan
Microbiologic_inclusion['BMI Composite'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['BMI Composite'] = Microbiologic_inclusion['BMI Composite'].astype(float)

###FEV1 Change
Microbiologic_inclusion['Baseline % Predicted FEV1'] = Microbiologic_inclusion['Baseline % Predicted FEV1'].astype(float)
Microbiologic_inclusion['Follow-up % Predicted FEV1'] = Microbiologic_inclusion['Follow-up % Predicted FEV1'].astype(float)
Microbiologic_inclusion['% Change in FEV1']= (Microbiologic_inclusion['Baseline % Predicted FEV1'] - Microbiologic_inclusion['Follow-up % Predicted FEV1'])/Microbiologic_inclusion['Baseline % Predicted FEV1']
Microbiologic_inclusion['% Change in FEV1'] = (Microbiologic_inclusion['% Change in FEV1']*100).astype(float)


def func(c):
    if c['COPD'] is 'Present':
        if c['% Change in FEV1'] < -25.0:
            return '1'
        elif c['% Change in FEV1'] > -25.0:
            return '0'
        else:
            return np.nan
    else:
        if c['% Change in FEV1'] < -12.0:
            return '1'
        elif c['% Change in FEV1'] > -12.0:
            return '0'
        else:
            return np.nan

Microbiologic_inclusion['FEV1 Composite'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['FEV1 Composite']= Microbiologic_inclusion['FEV1 Composite'].astype(float)


def func(c):
    if c['5 year mortality'] is 'Yes':
        return 1
    elif c['5 year mortality'] is 'No':
        return 0
    else:
        return np.nan
Microbiologic_inclusion['Mortality Composite'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['Mortality Composite'] = Microbiologic_inclusion['Mortality Composite'].astype(float)


def func(c):
    if c['Treatment Initiation'] <= c['Impression Date']:
        if c['Impression'] == 'Improvement in...':
            return 0
        elif c['Impression'] == 'No change in...':
            return 0
        elif c['Impression'] == 'Worsening in...':
            return 1
        elif c['Impression'] == np.nan:
            return np.nan

Microbiologic_inclusion['Radiology Impression Composite'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['Radiology Impression Composite'] = Microbiologic_inclusion['Radiology Impression Composite'].astype(float)


def func(c):
    if c['Microbiologic Conversion'] is'Yes':
        return 0
    elif c['Microbiologic Conversion'] is 'No':
        return 1
    else:
        return np.nan
Microbiologic_inclusion['Microbiologic Conversion Composite'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['Microbiologic Conversion Composite'] = Microbiologic_inclusion['Microbiologic Conversion Composite'].astype(float)

#Adding Composite score together
# Microbiologic_inclusion['Composite Score'] = 5
Microbiologic_inclusion['Composite Score'] = 0

def func(c):
    if c['Mortality Composite'] == 1:
        return 1
    elif c['FEV1 Composite'] ==1 or c['BMI Composite']==1 or c['Radiology Impression Composite']==1 or c['Microbiologic Conversion Composite']==1:
        return 1
    else:
        return 0

Microbiologic_inclusion['Composite Score'] = Microbiologic_inclusion.apply(func, axis=1)
def func(c):
    if c['Mortality Composite'] == 1:
        return 1
    else:
        if c['Microbiologic Conversion Composite']==1:
            return 1
        elif c['Microbiologic Conversion Composite'] == 0:
            return 0
        else:
            if c['Mortality Composite'] == 0:
                return 0

Microbiologic_inclusion['Composite Score'] = Microbiologic_inclusion.apply(func, axis=1)


Microbiologic_inclusion['Focal Radiology Baseline'] = ''
Microbiologic_inclusion['Focal Radiology Baseline'] = Microbiologic_inclusion['Focal Radiology Baseline'].astype(str)

def func(c):
    if c['CT Bronchiectasis Baseline'] == 'Focal Bronchiectasis':
        return c['CT Bronchiectasis Location Baseline'] +' (Bronchiectasis)'
    elif c['CXR Bronchiectasis Baseline'] == 'Focal Bronchiectasis':
        return c['CXR Bronchiectasis Location Baseline'] +' (Bronchiectasis)'
    else:
        return c['Focal Radiology Baseline']
Microbiologic_inclusion['Focal Radiology Baseline'] = Microbiologic_inclusion.apply(func, axis=1)

def func(c):
    if c['CT Nodular opacity Baseline'] == 'Focal Nodular opacity':
        return c['Focal Radiology Baseline']+ ',' +c['CT Nodular opacity Location Baseline'] +' (Nodular Opacity)'
    elif c['CXR Nodular opacity Baseline'] == 'Focal Nodular opacity':
        return c['Focal Radiology Baseline']+ ',' +c['CXR Nodular opacity Location Baseline'] +' (Nodular Opacity)'
    else:
        return c['Focal Radiology Baseline']
Microbiologic_inclusion['Focal Radiology Baseline'] = Microbiologic_inclusion.apply(func, axis=1)

def func(c):
    if c['CT Cavitary Baseline'] == 'Focal Cavitary' or c['CT Cavitary Baseline'] == 'Diffuse Cavitary':
        return c['Focal Radiology Baseline']+ ',' +c['CT Cavitary Location Baseline'] +' (Cavitary)'
    elif c['CXR Cavitary Baseline'] == 'Focal Cavitary' or c['CXR Cavitary Baseline'] == 'Diffuse Cavitary':
        return c['Focal Radiology Baseline']+ ',' +c['CXR Cavitary Location Baseline'] +' (Cavitary)'
    else:
        return c['Focal Radiology Baseline']
Microbiologic_inclusion['Focal Radiology Baseline'] = Microbiologic_inclusion.apply(func, axis=1)

def func(c):
    if c['CT Consolidation Baseline'] == 'Focal Consolidation':
        return c['Focal Radiology Baseline']+ ',' +c['CT Consolidation Location Baseline'] +' (Consolidation)'
    elif c['CXR Consolidation Baseline'] == 'Focal Consolidation':
        return c['Focal Radiology Baseline']+ ',' +c['CXR Consolidation Location Baseline'] +' (Consolidation)'
    else:
        return c['Focal Radiology Baseline']
Microbiologic_inclusion['Focal Radiology Baseline'] = Microbiologic_inclusion.apply(func, axis=1)
Microbiologic_inclusion['All Treatments Duplicate'] = Microbiologic_inclusion['All Treatments']

def func(c):
    if c['Baseline CT'] == 'Yes':
        return 'Yes'
    elif c['Baseline CXR'] == 'Yes':
        return 'Yes'
    else:
        return np.nan
Microbiologic_inclusion['Basline imaging'] = Microbiologic_inclusion.apply(func,axis=1)
Microbiologic_inclusion['Composite Score'] = Microbiologic_inclusion['Composite Score'].astype(str)
Microbiologic_inclusion.to_csv('/Volumes/homedir$/MAC Project/Complete Project/Microbiologic_inclusion.csv')

#for overall patient group table 1 produced by
Columns = ['Age at the time of Dx', 'Gender', 'Race', 'Living?', 'Smoking Status','Weight Baseline', 'BMI Baseline', 'GERD', 'Allergic Bronchopulmonary Aspergillosis','COPD','Cystic Fibrosis', 'HIV', 'Rheumatoid arthritis', 'Breast Cancer', 'IBD', 'Scoliosis', 'Pectus Excavatum', 'Baseline % Predicted FEV1', 'Baseline% Predicted FEV1/FVC', 'Baseline % Predicted FVC', 'Species', 'Coinfection']
Categorical = ['Gender', 'Race', 'Living?', 'Smoking Status', 'GERD', 'Allergic Bronchopulmonary Aspergillosis','COPD','Cystic Fibrosis', 'HIV', 'Rheumatoid arthritis', 'Breast Cancer', 'IBD', 'Scoliosis', 'Pectus Excavatum', 'Species', 'Coinfection']

groupby = ['Surgery for MAC?']
table1 = TableOne(Microbiologic_inclusion, Columns, Categorical)
table1.to_csv('/Volumes/homedir$/MAC Project/Complete Project/table1.csv')
table1

table2 = TableOne(Microbiologic_inclusion, Columns, Categorical, groupby, pval='true')
table2.to_csv('/Volumes/homedir$/MAC Project/Complete Project/table2.csv')
table2

#------------------Refined inclusion criteria-------------#
MAC_Focal = Microbiologic_inclusion.loc[ (Microbiologic_inclusion['Focal Radiology Baseline']  != '') & (Microbiologic_inclusion['Species'] == 'MAC') & (Microbiologic_inclusion['MAC Treatment'] == 'Adequate')]
MAC_Focal = MAC_Focal.loc[ (MAC_Focal['Composite Score'] != 'nan')]
#File below exported for regression
MAC_Focal.to_csv('/Volumes/homedir$/MAC Project/Complete Project/MAC_Focal.csv')


#Descriptive table 1 for cohorts after inclusion criteria applied
Columns = ['Age at the time of Dx', 'Gender', 'Race', 'Living?', 'Smoking Status','Weight Baseline', 'BMI Baseline', 'GERD', 'Allergic Bronchopulmonary Aspergillosis','COPD','Cystic Fibrosis', 'HIV', 'Rheumatoid arthritis', 'Breast Cancer', 'IBD', 'Scoliosis', 'Pectus Excavatum', 'Baseline % Predicted FEV1', 'Baseline% Predicted FEV1/FVC', 'Baseline % Predicted FVC', 'Species', 'Coinfection']
Categorical = ['Gender', 'Race', 'Living?', 'Smoking Status', 'GERD', 'Allergic Bronchopulmonary Aspergillosis','COPD','Cystic Fibrosis', 'HIV', 'Rheumatoid arthritis', 'Breast Cancer', 'IBD', 'Scoliosis', 'Pectus Excavatum', 'Species', 'Coinfection']
groupby = ['Surgery for MAC?']
table1 = TableOne(MAC_Focal, Columns, Categorical)
table1.to_csv('/Volumes/homedir$/MAC Project/Complete Project/table1.csv')
table1
table2 = TableOne(MAC_Focal, Columns, Categorical, groupby, pval='true')
table2.to_csv('/Volumes/homedir$/MAC Project/Complete Project/table2.csv')
table2


#Outcomes univariate tables for inclusion Criteria
Columns = ['BMI Composite', 'FEV1 Composite',	'Mortality Composite', 'Radiology Impression Composite'	, 'Microbiologic Conversion Composite',	'Composite Score']
Categorical = ['BMI Composite', 'FEV1 Composite',	'Mortality Composite', 'Radiology Impression Composite'	, 'Microbiologic Conversion Composite',	'Composite Score']

groupby = ['Surgery for MAC?']
table1 = TableOne(MAC_Focal, Columns, Categorical)
table1.to_csv('/Volumes/homedir$/MAC Project/Complete Project/table1.csv')
table1

table2 = TableOne(MAC_Focal, Columns, Categorical, groupby, pval='true')
table2.to_csv('/Volumes/homedir$/MAC Project/Complete Project/table2.csv')
table2




####------Other Tables----#######

#Radiologic Data
Categorical = ['CT Bronchiectasis Baseline','CXR Bronchiectasis Baseline', 'CT Cavitary Baseline', 'CXR Cavitary Baseline','CT Nodular opacity Baseline', 'CXR Nodular opacity Baseline', 'CT Consolidation Baseline', 'CXR Consolidation Baseline']
Columns = ['CT Bronchiectasis Baseline','CXR Bronchiectasis Baseline', 'CT Cavitary Baseline', 'CXR Cavitary Baseline','CT Nodular opacity Baseline', 'CXR Nodular opacity Baseline', 'CT Consolidation Baseline', 'CXR Consolidation Baseline']
Imaging = TableOne(Microbiologic_inclusion, Columns, Categorical, groupby)
Imaging.to_csv('/Volumes/homedir$/MAC Project/Complete Project//Imaging.csv')


Categorical = ['CT Bronchiectasis Baseline','CT Bronchiectasis Location Baseline', 'CT Cavitary Baseline','CT Cavitary Location Baseline', 'CT Nodular opacity Baseline', 'CT Nodular opacity Location Baseline', 'CT Consolidation Baseline', 'CT Consolidation Location Baseline']
Columns = ['CT Bronchiectasis Baseline','CT Bronchiectasis Location Baseline', 'CT Cavitary Baseline','CT Cavitary Location Baseline', 'CT Nodular opacity Baseline', 'CT Nodular opacity Location Baseline', 'CT Consolidation Baseline', 'CT Consolidation Location Baseline']
Imaging = TableOne(Microbiologic_inclusion, Columns, Categorical, groupby, pval='true')
Imaging.to_csv('/Volumes/homedir$/MAC Project/Complete Project//Imaging.csv')
Imaging
