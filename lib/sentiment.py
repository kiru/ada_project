# -*- coding: utf-8 -*-
'''
Thsi file contains content related to sentiment anylsis.

'''

import pandas as pd
import numpy  as np
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook


def write_to_file(filename, content):
    with open(filename, 'w') as out:
        out.write(content)

def export_alll_files(df_reports, output = 'tmp/'):
    '''
    From given reports, expor tall of them in to a temporary folder
    :param df_reports:
    :return: nothing
    '''

    df_reports = df_reports.reset_index()
    df_reports.head()
    df = df_reports[['url', 'Summary']].dropna(how='any', axis='index')
    values = df.values
    for each in tqdm_notebook(values, desc="export report to folder"):
        url = each[0]
        summary = each[1]
        # repalce slash with - because FS doesn't like it.
        write_to_file(output + url.replace('/', '-') + ".txt", summary)


def add_sentiment_data(df_reports, sentiment_file='sentiment.csv'):
    '''
    :param df_reports:  the original report
    :param sentiment_file:  the file with output from LIBWC
    :return:
    '''
    df_sentiment = pd.read_csv(sentiment_file)
    df_sentiment.Filename = df_sentiment.Filename.str.replace('-', '/', regex=False)
    df_sentiment.Filename = df_sentiment.Filename.str.replace('.txt', '', regex=False)
    df_merged_report = df_reports.merge(df_sentiment, left_on='url',
                                        right_on='Filename', how='left')
    # because we only want one url
    df_merged_report.rename(columns={'Filename': 'url'}, inplace=True)
    df_merged_report = df_merged_report.set_index('url')
    return df_merged_report

def get_emotion_data(df):
    df_longer_reports = df[df['WC'] > 100].copy()
    df_longer_reports.Shape = df_longer_reports.Shape.str.replace('([ ]+)', '')
    df_longer_reports.Shape = df_longer_reports.Shape.str.title()
    return df_longer_reports
    
def emotions_boxplot(df, showfliers=True):    
    emotions = ['family','friend','posemo','negemo','anger','sad',
                'anx','hear','feel','reward','achieve','risk',
                'tentat','certain']
    df_emotions = df[emotions]
    emotions_values = []
    for emo in emotions:
        emotions_values.append(df_emotions[emo].values)
    fig, ax = plt.subplots(figsize=(15, 6))
    
    ax = plt.boxplot(x = emotions_values, showfliers=showfliers)
    plt.ylabel('Percentage', fontsize=14)
    plt.title('Emotions',fontsize=18)
    plt.xticks(list(range(1,len(emotions)+1)), emotions)
    plt.show()
    
def plot_sentiment_nets(df):
    emotions_labels = ['feel','negemo','hear','posemo','reward','certain']
    shape_labels = ['Light', 'Triangle', 'Circle', 'Other', 'Unknown', 'Sphere']
    shape_stats = []
    shapes_list = []
    for shape in shape_labels:
        df_shape = df[(df.Shape == shape)].copy()
        shapes_list.append(df_shape[emotions_labels])
        for emo in emotions_labels:
            shape_stats.append(shapes_list[-1][emo].mean())
    shape_stats = np.asarray(shape_stats).reshape(6,6)

    angles=np.linspace(0, 2*np.pi, len(emotions_labels), endpoint=False)
    angles = np.concatenate((angles,[angles[0]]))
    stats = []
    for indice in range(6):
        stats.append(np.concatenate((shape_stats[indice], 
                                              [shape_stats[indice][0]])))  

    fig=plt.figure(figsize=(15,15))
    for i in range(6):
        ax = fig.add_subplot(321+i, polar=True)
        ax.plot(angles, stats[i], 'o-', linewidth=2, color='#751947')
        ax.fill(angles, stats[i], alpha=0.25,color='#751947')
        ax.set_thetagrids(angles * 180/np.pi, emotions_labels, fontsize=13)
        ax.set_title(shape_labels[i], fontsize=16)
        ax.grid(True)
    plt.show()