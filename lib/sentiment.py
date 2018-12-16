# -*- coding: utf-8 -*-
'''
Thsi file contains content related to sentiment anylsis.

'''

import pandas as pd
import numpy  as np
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
