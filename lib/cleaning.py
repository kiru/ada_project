import pandas as pd
import re
import numpy as np

#regex_cut_nuforc = r"\(\(NUFORC Note.[^\)]*\)\)"
#regex_cut_url = r"(https|http|www)(:\/\/|)([^\s )(]*)"


# return summary without any nuforc notes
def delete_Nuforc_from_sum(summary, nuforc_note):
    l = list(nuforc_note)
    for i in range(0,len(l)):
        summary = summary.replace(l[i], '')
    return summary

# extract any regex
def single_extract(summary, regex_extract):
    matches = re.finditer(regex_extract, summary, re.MULTILINE)    
    data=[]
    for matchNum, match in enumerate(matches):
        data.append(match.group())
    return data

# split and delete any regex from summary into new column new_feature
def split_regex_from_summary(df, regex_cut_url, new_feature):    
    # filter reports that have a summary
    filter_nan_summary = pd.isnull(df["Summary"])
    df = df[~filter_nan_summary]

    # split and remove 
    df[new_feature] = df.apply(lambda x: single_extract(x.Summary, regex_cut_url), axis = 1)
    df["Summary"] = df.apply(lambda x: delete_Nuforc_from_sum(x.Summary, x[new_feature]), axis = 1)    
    return df

# main split
def split_summary(df):
    regex_cut_nuforc = r"\(\(NUFORC Note.[^\)]*\)\)"
    regex_cut_url = r"(https|http|www)(:\/\/|)([^\s )(]*)"
    
    df_new = split_regex_from_summary(df, regex_cut_nuforc, "nuforc_note")
    df_new = split_regex_from_summary(df_new, regex_cut_url, "link")
    return df_new
    


# post process after scraping - run only once after import
def post_process(df_ufo_reports):
    # select non 404 reports - filters 105 rows
    filter_nan_summary = pd.isnull(df_ufo_reports["Summary"])
    df_ufo_reports = df_ufo_reports[~filter_nan_summary]
    
    # remove whitespace from column names
    df_ufo_reports.columns = df_ufo_reports.columns.str.strip()

    # Split Location into Location and State
    print("splitting Location..")
    df_ufo_reports[['Location', 'State']] = df_ufo_reports['Location'].str.split(',', n=1, expand=True)
    
    # clear unwanted characters
    print("cleaning Location..")
    df_ufo_reports['Location'] = df_ufo_reports['Location'].apply(lambda x: x.strip()) # 333ys
    
    print("cleaning State..")
    filter_nan_states = pd.isnull(df_ufo_reports["State"])
    df_ufo_reports = df_ufo_reports[~filter_nan_states]
    df_ufo_reports['State'] = df_ufo_reports['State'].apply(lambda x: x.strip()) # 333ys
    
    print("cleaning Reported")
    df_ufo_reports['Reported'] = df_ufo_reports['Reported'].apply(lambda x: x.strip()) # 333ys
    
    print("cleaning Posted..")    
    df_ufo_reports['Posted'] = df_ufo_reports['Posted'].apply(lambda x: x.strip()) # 333ys
    
    # clear unwanted characters 
    #print("cleaning Summary..")
    #df_ufo_reports['Summary'] = df_ufo_reports['Summary'].apply(lambda x: x.strip("['']") if len(x)>0 else "") # 333ys

    # re-arrange columns
    print("re-ordering columns..")
    df_ufo_reports = df_ufo_reports[["Duration","Location","State","Occurred","Posted","Reported","Shape","Summary","url"]]
    
    print("done")
    return df_ufo_reports

import folium
import matplotlib.pyplot as plt

def sightings_per_state_unnormalized(df_sight_per_state):
    # prepare data for Sightings per State plot
    sight_per_state=df_sight_per_state['State'].value_counts()
    df_sight_per_state=sight_per_state.to_frame()
    df_sight_per_state.reset_index(level=0, inplace=True)
    df_sight_per_state.columns = ['State','Sightings']
    
    data_folder = './geo_data/'
    my_USA_map = data_folder + r'us-states.json'
    
    us_map = folium.Map(location=[48, -102], zoom_start=3)

    us_map.choropleth(geo_data=my_USA_map, data=df_sight_per_state,
                 columns=['State', 'Sightings'],
                 key_on='feature.id',
                 fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2,
                 legend_name='UFO sightings in the US')
    return us_map
