# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import requests
import pandas as pd
import seaborn as sns
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook
from datetime import datetime

def get_time_of_occurrence(data):
    data = data.sample(1000)
    """
    Takes the input of the whole dataframe
    Return:
       - Time and date of occurrance and report
       - Year of occurrance
    """
    data = data.rename(index=str, columns={'Occurred ':'Occurred'})
    occur_report = data[['Occurred', 'Reported']]
    df_time_occur_report = occur_report.assign(Occurred=occur_report.Occurred.str.split('(',n=1).str[0])
    #Create new column for years
    df_time_occur_report['year'] = np.nan
    df_time_occur_report.Occurred = df_time_occur_report.Occurred.str.strip()
    converted_time = to_datetime_add_year(df_time_occur_report.Occurred)
    df_time_occur_report.Occurred = converted_time
    #Assigns years of occurance to the column
    for i in range(len(df_time_occur_report.Occurred)):
        df_time_occur_report.year[i] = df_time_occur_report.Occurred[i].year
    return df_time_occur_report

def to_datetime_add_year(date):
    """
    Changes the date format of the dataframe
    Returns:
       - Updated time formats
    """
    converted = pd.DataFrame(pd.to_datetime(date,format='%m/%d/%Y %H:%M',
                   errors = 'coerce', exact=True))
    converted_2 = pd.DataFrame(pd.to_datetime(date,format='%m/%d/%Y',
                   errors = 'coerce', exact=True))
    values = converted_2[~converted_2.Occurred.isnull()]
    converted.update(values)

    return converted

def replace_empty_with_nan(data, feature):
    """
    Checks for the missing values in our dataset
    And transforms the missing values into NaNs
    """
    feature_names = list(data)
    data[feature] = data[feature].str.strip()
    data[feature] = np.where(data[feature] != '', data[feature], np.NaN)
    nan_count = data[feature].isna().sum()
    
    print('{} feature has {} missing values'.format(feature, nan_count))
    return data


def distribution_histogram(data, feature):
    plotting_data = data[feature].dropna()
    plt.figure(figsize=(15,9))
    plot = plt.hist(plotting_data, bins = 40, color = '#8B0000')
    # Tweak the visual presentation
    #plt.xaxis.grid(True)
    plt.title('Distribution of occurrance times')
    plt.xlabel('Year')
    plt.ylabel('Frequency')
    sns.despine(trim=False, left=False)


