# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import requests
import pandas as pd
import seaborn as sns
from scipy.stats import ks_2samp
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm_notebook
from datetime import datetime
from PIL import Image
import urllib
import requests



nltk.download('stopwords')
tokenizer = RegexpTokenizer(r'\w+')

# Global variable for color of the plots
color_global = '#0c89a0'

url_UFO = 'http://clipart.printcolorcraft.com/wp-content/uploads/ufo/cliparti1%20ufo%20clipart%2005.jpg'
url_fireball = 'https://i.imgur.com/tovze5p.jpg'
url_disk = 'https://hachuele.github.io/data-science-ufo-sightings/images/ufo_img_1.png'
url_triangle = 'https://i.imgur.com/HKQGbCl.jpg'
url_sphere = 'https://i.imgur.com/vxv7KuF.jpg'

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


def peaks_over_months(df):
    """
    Create a barplot for occurred sightings per month
    """
    df_peaks = df[['Occurred']].copy()
    df_peaks = df_peaks[(df_peaks.Occurred.dt.year > 1900)]
    index_list = df_peaks[df_peaks.Occurred.isna()].index
    df_peaks = df_peaks.dropna()
    df_peaks['year_month'] = df_peaks.Occurred.map(lambda x: x.strftime('%m'))
    plotting_times = df_peaks.groupby(by='year_month').count()

    fig, ax = subplots(figsize=(16,6))
    plt.bar(plotting_times.index, plotting_times.Occurred, color=color_global)
    plt.legend(['Intensity of occurance'], fontsize=16)
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Amount', fontsize=18)
    plt.show()
    
def get_plot_july(df):
    df_july = df[['Occurred']].copy()
    df_july = df_july[(df_july.Occurred.dt.year > 1900)]
    df_july = df_july[(df_july.Occurred.dt.month == 7)]
    index_list = df_july[df_july.Occurred.isna()].index
    df_july = df_july.dropna()
    df_july['days'] = df_july.Occurred.map(lambda x: x.strftime('%d'))
    july_plotting_times = df_july.groupby(by='days').count()

    fig, ax = subplots(figsize=(16,6))
    plt.bar(july_plotting_times.index, july_plotting_times.Occurred, color=color_global)
    plt.legend(['Intensity of occurance in July'], fontsize=16)
    plt.xlabel('Day', fontsize=18)
    plt.ylabel('Amount', fontsize=18)
    plt.show()
    
def get_data_for_months(df):
    """
    Takes an input of the whole data frame
    :return:
        an amount of reports per each day of the month over the whole time period (1900-2018)
    """
    df_month = df[['Occurred']].copy()
    df_month = df_month[(df_month.Occurred.dt.year > 1900)]
    months = []
    for i in range(1,13):
        df_month_iter = df_month[(df_month.Occurred.dt.month == i)].copy()
        index_list = df_month_iter[df_month_iter.Occurred.isna()].index
        df_month_iter = df_month_iter.dropna()
        df_month_iter['days'] = df_month_iter.Occurred.map(lambda x: x.strftime('%d'))
        each_month = df_month_iter.groupby(by='days').count()
        each_month['month'] = df_month_iter.Occurred.iloc[1].strftime('%B')
        months.append(each_month)
    return months

def plot_for_each_month(months):
    
    figs, axis = subplots(nrows=6,ncols=2,figsize=(16,14))
    
    month = 0
    for row in range(6):
        for col in range(2):
            axis[row, col].bar(months[month].index, months[month].Occurred, color = color_global)
            axis[row, col].legend(['{}'.format(months[month].month.iloc[1])], fontsize=14)
            month += 1
    figs.suptitle('Occurance of submisions over the months', fontsize=20)
    plt.subplots_adjust(hspace=0.4)       
    plt.show()

    
def spike_finder(year, month):
    """
    :returns: interactive plot to view the occurrance of reports over a year/month period
    """
    df_spike = df_reports[['Occurred']].copy()
    df_spike = df_spike[(df_spike.Occurred.dt.year == year)]
    df_spike = df_spike[(df_spike.Occurred.dt.month == month)]
    #df_spike = df_spike[(df_spike.Occurred.dt.day == day)]
    index_list = df_spike[df_spike.Occurred.isna()].index
    df_spike = df_spike.dropna()
    df_spike['day'] = df_spike.Occurred.map(lambda x: x.strftime('%d'))
    plotting = df_spike.groupby(by='day').count()
    fig, ax = plt.subplots(figsize=(15, 6))
    plt.bar(plotting.index, plotting.Occurred, )
    plt.legend(['Intensity of occurance in {}'.format(df_spike.Occurred.iloc[1].strftime('%B'))])
    plt.xlabel("Day in {}".format(df_spike.Occurred.iloc[1].strftime('%B')))
    plt.ylabel('Occurrance')
    plt.show()
    interactive_plot = interactive(spike_finder, year = IntSlider(min=2004,max=2007,step=1,value=2004),
                                              month = IntSlider(min=1,max=12,step=1,value=1))
    return interactive_plot

def occurance_report_difference(df):
    """
    Calculates the time difference between the occurrance and the
    reporting of the UFO sighting. Starting from 1964, transforming
    the time to hours and dropping the first 48 hours.
    :returns: list of np.arrays, where each indice is a month
    """
    df_dummy = df[['Duration', 'Occurred', 'Reported', 'Shape', 'nuforc_note']]
    df_dummy = df_dummy[(df_dummy.Occurred.dt.year > 1964)]
    df_dummy['difference'] = df_dummy.Reported - df_dummy.Occurred
    df_dummy.difference = df_dummy.difference.dt.total_seconds()/3600
    df_dummy = df_dummy[(df_dummy.difference > 48)]
    df_dummy['day'] = df_dummy.Occurred.dt.day
    seperate_days_diff = []
    for days in range(1, 32):
        seperate_days_diff.append(df_dummy.difference[(df_dummy.Occurred.dt.day == days)].values)
    return seperate_days_diff

def plot_occur_report_difference(data, showfliers=True):
    fig, ax = plt.subplots(figsize=(15, 6))
    ax = plt.boxplot(x = data, showfliers=showfliers)
    plt.xlabel('Day of the month', fontsize=14)
    plt.ylabel('Time in hours', fontsize=14)
    plt.title('Difference between the occurance of the event to the report of the event per day of the month',
              fontsize=18)

    plt.show()
    
def get_distribution_data(data):
    """
    Input of the difference from occurrance to reported time
    per each month
    :return: a list of suspicious and non-suspicious months
    """
    all_days = list(range(1,32))
    suspicious_days = [1,5,10,15,20,25,30]
    for day in suspicious_days:
        all_days.remove(day)
    data_all_days = []
    data_suspicious_days = []
    for day in all_days:
        data_all_days.append(data[day-1])
    for day in suspicious_days:
        data_suspicious_days.append(data[day-1])
    data_all_days = np.concatenate(data_all_days).ravel()
    data_suspicious_days = np.concatenate(data_suspicious_days).ravel()
    return data_all_days, data_suspicious_days


def kolmogorov_smirnov(data1, data2):
    """
    :return: True is at least one mean is different from the other
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html#scipy.stats.ks_2samp
    """
    statistic, pvalue = ks_2samp(data1, data2)

    print("Kolmogorov_Smirnov Statistic " + str(statistic) + " and p-value " + str(pvalue))
    if pvalue < 0.05:
        return True
    else:
        return False

def to_frec(df_report):
    """
    :return: frequency of words over reports per year
    """
    df_report_for_a_year = df_report['Summary'].values
    year = df_report.Occurred.dt.year.values[0]
    print("start", year)
    wordToFrequency = {}
    for item in tqdm_notebook(df_report_for_a_year):
        tokens = tokenizer.tokenize(item)   
        for t in tokens:
            if t.lower() not in stopwords.words('english'):
                #print(t.lower())
                if t in wordToFrequency:
                    wordToFrequency.update({t: wordToFrequency[t] + 1})
                else:
                    wordToFrequency[t] = 0
    print("done", year)
    return (year, wordToFrequency)    


from  multiprocessing import Pool
def paralelize_word_frequency(df_reports):
    summary_list = []
    for year in range(1964, 2019):
        summary_list.append(df_reports[(df_reports.Occurred.dt.year == year)])

    with Pool(8) as p:
        year_to_word_freq = {}
        print("start")
        for year, freq in tqdm_notebook(p.imap(to_frec, summary_list)):
    year_to_word_freq[year] = freq
    return year_to_word_freq

def drop_most_popular_words(frequency_years):
    drop_list = ['light', 'lights', 'sky', 'object', 'saw', 'like']
    for year in range(1964, 2019):
        for name in drop_list:
            del frequency_years[year][name]

def mask_from_url(url):
    """
    :return: mask for the wordcloud
    """
    mask = np.array(Image.open(requests.get(url, stream=True).raw))
    return mask


def grey_color_func_red(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl({}, 100%, {}%)".format(10, np.random.randint(20,60)))

def grey_color_func_yellow(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl({}, 100%, {}%)".format(50, np.random.randint(20,60)))

def grey_color_func_green(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl({}, 100%, {}%)".format(120, np.random.randint(20,60)))

def grey_color_func_blue(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl({}, 100%, {}%)".format(170, np.random.randint(20,60)))

def grey_color_func_darker(word, font_size, position,orientation,random_state=None, **kwargs):
    return("hsl({}, 100%, {}%)".format(250, np.random.randint(20,60)))


# This function takes in your text and your mask and generates a wordcloud. 
def generate_clipart(year):
    """
    :return: clipart wordcloud based on the most popular shape of the year
    """
    disk = [1964,1965,1966,1967,1968,1969,1970,1971,1972,1973
            ,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,
           1985,1987]
    fireball = [1998, 1999, 2012, 2013]
    triangle = [1984, 1986, 1989, 1990, 1991, 1992, 1993, 1994, 2000,
                1997, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
    circle = [2009, 2010, 2011, 2015, 2016, 2017, 2018]
    if year in fireball:
        wc = WordCloud(width = 512, height = 512, background_color='white',
                   mask=mask_from_url(url_fireball), repeat=False, 
                       max_words=110).fit_words(frequency_years[year])
        wc.recolor(color_func=grey_color_func_red)
    elif year in triangle:
        wc = WordCloud(width = 512, height = 512, background_color='white',
                   mask=mask_from_url(url_triangle), repeat=False, 
                       max_words=110).fit_words(frequency_years[year])
        wc.recolor(color_func=grey_color_func_green)
    elif year in circle:
        wc = WordCloud(width = 512, height = 512, background_color='white',
                   mask=mask_from_url(url_sphere), repeat=False, 
                       max_words=110).fit_words(frequency_years[year])
        wc.recolor(color_func=grey_color_func_blue)
    else:
        wc = WordCloud(width = 512, height = 512, background_color='white',
                   mask=mask_from_url(url_UFO), repeat=False, 
                       max_words=110).fit_words(frequency_years[year])
        wc.recolor(color_func=grey_color_func_darker)
    plt.figure(figsize=(10,8),facecolor = 'white', edgecolor='blue')
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.show()


def show_wordcloud(year):
    x, y = np.ogrid[:1000, :1000]
    mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
    mask = 255 * mask.astype(int)

    wc = WordCloud(background_color="white", repeat=False, width=1000, height=1000, max_words=80)
    wc.fit_words(frequency_years[year])
    plt.figure(figsize=(12, 12))
    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    plt.show()
    interactive_plot = interactive(generate_clipart, year = IntSlider(min=1964,max=2018,step=1,value=2000))
    return interactive_plot