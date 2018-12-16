# -*- coding: utf-8 -*-

from tqdm import tqdm_notebook

def write_to_file(filename, content):
    with open(filename, 'w') as out:
        out.write(content)

def export_alll_files(df_reports):
    df_reports = df_reports.reset_index()
    output = 'tmp/'
    df = df_reports[['Summary']].dropna(how='any', axis='index')
    values = df.reset_index().values
    for each in tqdm_notebook(values, desc="export report to folder"):
        write_to_file(output + each[0].replace('/', '-') + ".txt", each[1])

def add_sentiment_data(df_reports, sentiment_file='sentiment.csv'):
    df_sentiment = pd.read_csv(sentiment_file)
    df_sentiment.Filename = df_sentiment.Filename.str.replace('-', '/', regex=False)
    df_sentiment.Filename = df_sentiment.Filename.str.replace('.txt', '', regex=False)
    df_merged_report = df_reports.merge(df_sentiment, left_on='url',
                                        right_on='Filename', how='left')
    # because we only want one url
    df_merged_report.rename(columns={'Filename':'url'}, inplace=True)
    df_merged_report = df_merged_report.set_index('url')
    return df_merged_report

df_report_sentiment = add_sentiment_data(df_reports)
