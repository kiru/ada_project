import pandas as pd

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
    print("cleaning Summary..")
    df_ufo_reports['Summary'] = df_ufo_reports['Summary'].apply(lambda x: x.strip("['']") if len(x)>0 else "") # 333ys

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