import folium
import matplotlib.pyplot as plt
import pandas as pd

data_folder = './geo_data/'
my_USA_map = data_folder + r'us-states.json'

############################## UFO Reports by State ##############################

def sightings_per_state(df):
    # prepare data for Sightings per State plot
    sight_per_state=df['State'].value_counts()
    df=sight_per_state.to_frame()
    df.reset_index(level=0, inplace=True)
    df.columns = ['State','Sightings']
    
    
    us_map = folium.Map(location=[48, -102], zoom_start=3)
    us_map.choropleth(geo_data=my_USA_map, data=df,
                 columns=['State', 'Sightings'],
                 key_on='feature.id',
                 fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2,
                 legend_name='UFO sightings in the US')
    return us_map

############################## UFO Reports per Capita¶ ##############################

# states and their population
states_population = {'AK': 2915958,
                     'AL': 4780000,
                     'AR': 2915958,
                     'AS': 55519,
                     'AZ': 6392307,
                     'CA': 37253956,
                     'CO': 5029196,
                     'CT': 3574097,
                     'DC': 601723,
                     'DE': 897934,
                     'FL': 18801310,
                     'GA': 9687653,
                     'GU': 159358,
                     'HI': 1360301,
                     'IA': 3046355,
                     'ID': 1567582,
                     'IL': 12830632,
                     'IN': 6483802,
                     'KS': 2853118,
                     'KY': 4339367,
                     'LA': 4533372,
                     'MA': 6547629,
                     'MD': 5773785,
                     'ME': 1328361,
                     'MI': 9884129,
                     'MN': 5303925,
                     'MO': 5988927,
                     'MP': 53883,
                     'MS': 2968103,
                     'MT': 989415,
                     'NC': 9535692,
                     'ND': 672591,
                     'NE': 1826341,
                     'NH': 1316466,
                     'NJ': 8791936,
                     'NM': 2059192,
                     'NV': 2700691,
                     'NY': 19378087,
                     'OH': 11536725,
                     'OK': 3751616,
                     'OR': 3831073,
                     'PA': 12702887,
                     'PR': 3726157,
                     'RI': 1052931,
                     'SC': 4625401,
                     'SD': 814191,
                     'TN': 6346275,
                     'TX': 25146105,
                     'UT': 2763888,
                     'VA': 1853011,
                     'VI': 106405,
                     'VT': 625745,
                     'WA': 6724543,
                     'WI': 5687289,
                     'WV': 1853011,
                     'WY': 563767}

# contains state id's
states_keys = list(states_population.keys())

# rm commas
def replace_commas_in_dict():
    for key in states_population.keys():
        states_population[key] = states_population[key].replace(",","")
        states_population[key] = int(states_population[key])


def sightings_per_state_normalized(df):
    # prepare data for Sightings per State plot
    df=df['State'].value_counts()
    df=df.to_frame()
    df.reset_index(level=0, inplace=True)
    df.columns = ['State','Sightings']
    
    # filter us reports from the us states
    df = df[df["State"].isin(states_keys)]
    
    # normalize data
    state_dict = df["State"]
    state_new = df.apply(lambda x: x["Sightings"]/int(states_population[x["State"]]) * 100000, axis=1   )
    df["Sightings"] = state_new
    
    
    us_map = folium.Map(location=[48, -102], zoom_start=3)
    us_map.choropleth(geo_data=my_USA_map, data=df,
                 columns=['State', 'Sightings'],
                 key_on='feature.id',
                 fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2,
                 legend_name='UFO Reports per 100,000 People in United States')
    return us_map
