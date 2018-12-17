import json
import pandas as pd
import numpy as np
import pynmea2
from tqdm import tqdm_notebook
import branca
import folium
import folium.plugins



def process_state_county_index_table():
    '''
    return
    cleaned frame of state - county - index
    '''
    
    # load counties (3250)
    geo_data_folder="./geo_data/"
    state_countie = pd.read_csv(geo_data_folder+"county_state.csv", dtype=str)
    s = pd.to_numeric(state_countie["State_idx"])
    state_countie["State_idx"] = s
    state_countie["idx"] = state_countie["State_idx"].astype(str) + state_countie["County_idx"]
    state_countie['County'] = state_countie['County'].map(lambda x: x.replace(" County", ""))
    state_countie["State_County"] = state_countie["State"] + "_" + state_countie["County"]
    state_countie = state_countie.drop(columns=['State_idx', 'County_idx', 'H'])
    
    # load us-cities (36651)
    us_cities = pd.read_csv(geo_data_folder + "uscitiesv1.4.csv")
    us_cities = us_cities[["city", "state_id", "county_fips", "county_name"]]
    us_cities["State_County"] = us_cities["state_id"] + "_" + us_cities["city"]
    us_cities.columns = ['city', 'State', 'idx', 'County', 'State_County']
    us_cities = us_cities.drop(['city'], axis=1)
    us_cities['idx'] = us_cities['idx'].astype(str)
    
    # merge cities to counties
    full_locations = us_cities.append(state_countie, ignore_index=True)
    full_locations = full_locations.drop_duplicates(subset='State_County', keep="last")
    full_locations.to_json("./geo_data/full_locations_index.json")
    
    return full_locations

us_state_code_dict = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

# population data processing
def process_population_data():
    '''
    return cleaned poulation file
    '''
    # loading the original file
    population_folder = './data/'
    df_population_all = pd.read_excel(population_folder + 'PctUrbanRural_County.xls')
    df_population_all = df_population_all[["COUNTYNAME","POP_COU","STATE", "AREA_COU", "STATENAME"]]

    # adding density and rural area data
    urban_rural_tresh = 4
    df_population_all["density"] = df_population_all["POP_COU"] / (df_population_all["AREA_COU"] / 100000)
    df_population_all["rural"] = df_population_all["density"] 
    df_population_all["rural"] = df_population_all["rural"].apply(lambda x: True if x > urban_rural_tresh else False)  

    # add county code for population file
    def code_to_name(x):
        if len(x) > 0:
            if x in us_state_code_dict:
                return us_state_code_dict[x]
        return x
    
    # apply state code and sort
    df_population_all["STATENAME"] = df_population_all["STATENAME"].apply(lambda x: code_to_name(x))
    df_population_all["State_County"] = df_population_all["STATENAME"] + "_" + df_population_all["COUNTYNAME"]
    df_population_all = df_population_all.sort_values("density", ascending=False)
    
    return df_population_all



def sightings_per_countie(df):
    '''
    return
    Sightings per county of state
    '''
    df = df[df['Location'] != np.nan]
    df["State_County"] = df['State']+"_"+df['Location']
    
    # prepare data for Sightings per County of State plot
    sight_per_state=df['State_County'].value_counts()
    df=sight_per_state.to_frame()
    df.reset_index(level=0, inplace=True)
    df.columns = ['State_County', 'Sightings']
    return df

#unnormalized_sights = sightings_per_countie(df_tst)

def normalized_countie_sightings(df):
    '''
    return
    normalized sightings for each state-county combination
    '''
    df_sightings_per_countie_new = sightings_per_countie(df)    

    for index, row in df_sightings_per_countie_new.iterrows():
        search_for = row["State_County"]
        pop_lookup = df_population_all[(df_population_all["State_County"] == search_for)]
        
        if (len(pop_lookup.values) > 0):
            population = pop_lookup["POP_COU"].values[0]
            sights = df_sightings_per_countie_new.iloc[index]["Sightings"]
            normalized_sights = (sights / population) * 100000
            df_sightings_per_countie_new.iloc[index, df_sightings_per_countie_new.columns.get_loc('Sightings')] = normalized_sights

    return df_sightings_per_countie_new   

###
###
### MAP SPECIFIC 
###
###

def conversion(old):
    '''
    takes either one lon or lat at the time
    convert GPS time location to float lon/lat
    '''
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    new = old.replace(u'°',' ').replace('\'',' ').replace('"',' ')
    new = new.split()
    new_dir = new.pop()
    new.extend([0,0,0])
    return (float(new[0])+float(new[1])/60.0+float(new[2])/3600.0) * direction[new_dir]

def process_airbases():
    df_airbases = pd.read_csv("./data/air_bases.csv")
    df_airbases["latitude"] = df_airbases["latitude"].apply(lambda x: conversion(x.replace("′","\'").replace("″","\"").replace("°","°")))
    df_airbases["longitude"] = df_airbases["longitude"].apply(lambda x: conversion(x.replace("′","\'").replace("″","\"").replace("°","°")))
    return df_airbases

###
###
### Normalized UFO Sights
###
###

# colorscale
colorscale = branca.colormap.linear.YlOrRd_09.scale(0, 150)


def style_function_normalized(feature):
    '''
    takes feature which contains countie id
    based on id get the countyname from the index table full_locations
    get the number related to the county
    '''
    x = full_locations[full_locations["idx"] == (feature["id"])]
    if len(x.values) > 0:
        sum_countie = 0
        for i in x.values:
            sights = normal_sights[normal_sights["State_County"] == i[2]]
            sights = sights.values
            if len(sights) > 0:
                sum_countie += sights[0][1]
            
        countie_name = x["State_County"]
        countie_name = countie_name.values[0]
        
        if sum_countie > 0:
            return {
                'fillOpacity': 1,
                'weight': 0,
                'fillColor': 'white' if sum_countie is None else colorscale(sum_countie)
            }
    return {
        'fillOpacity': 1,
        'weight': 0,
        'fillColor': 'white'
    }
    
def get_countie_map_():
    '''
    return
    map with density layer
             normalized reports per country
             not normalized reports per country
             markers of airbases
    '''
    # geo data
    geo_data_folder = './geo_data/'
    us_state_map = geo_data_folder + r'us-states.json'
    us_countie_map = geo_data_folder + r'us-topo.json'
    
    # map init
    m = folium.Map(
        location=[48, -102],
        tiles='cartodbpositron',
        zoom_start=3
    )
    
    # counties normalized layer
    layer_counties_normalized = folium.TopoJson(
        open(us_countie_map),
        'objects.counties',
        style_function=style_function_normalized
    ).add_to(m)
    layer_counties_normalized.layer_name = 'counties normalized'

    # airbases cluster map
    df_airbases = process_airbases()
    cluster_markers = folium.plugins.MarkerCluster().add_to(m)
    tooltip = 'click!'
    for index, row in df_airbases.iterrows():
        folium.Marker(
            location=[row.latitude, row.longitude],
            popup='<i>'+row.base_name+'</i>',
            icon=folium.Icon(icon='plane', color="white", icon_color='black')
        ).add_to(cluster_markers)
    cluster_markers.layer_name = "airbase markers"

    
    # colorscale
    m.add_child(colorscale)
    
    folium.LayerControl().add_to(m)
    
    return m


###
###
### DENSITY
###
###

def style_function_density(feature):
    x = full_locations[full_locations["idx"] == (feature["id"])]
    if len(x.values) > 0:
        countie_name = x["State_County"]
        countie_name = countie_name.values[0]

        for i in x.values:
            rural = df_population_all[df_population_all["State_County"]==i[2]]
            rural = rural.values
            if len(rural) > 0:
                rural = rural[0][6]

                if rural == True:
                    return {
                        'fillOpacity': 0.3,
                        'weight': 0.4,
                        'fillColor': 'lightgreen' 
                    }
                if rural == False:
                    return {
                        'fillOpacity': 0.3,
                        'weight': 0.4,
                        'fillColor': 'yellow' 
                    }
    return {
        'fillOpacity': 0.5,
        'weight': 0.7,
        'fillColor': 'yellow' 
    }

def get_density_map_():
    '''
    return
    map with density layer
             normalized reports per country
             not normalized reports per country
             markers of airbases
    '''
    # geo data
    geo_data_folder = './geo_data/'
    us_state_map = geo_data_folder + r'us-states.json'
    us_countie_map = geo_data_folder + r'us-topo.json'
    
    # map init
    m = folium.Map(
        location=[48, -102],
        tiles='cartodbpositron',
        zoom_start=3
    )
    

    # densities layer 
    layer_densities = folium.TopoJson(
        open(us_countie_map),
        'objects.counties',
        style_function=style_function_density
    ).add_to(m)
    layer_densities.layer_name = 'population density'


    # colorscale
    m.add_child(colorscale)

    # airbases cluster map
    df_airbases = process_airbases()
    cluster_markers = folium.plugins.MarkerCluster().add_to(m)
    tooltip = 'click!'
    for index, row in df_airbases.iterrows():
        folium.Marker(
            location=[row.latitude, row.longitude],
            popup='<i>'+row.base_name+'</i>',
            icon=folium.Icon(icon='plane', color="white", icon_color='black')
        ).add_to(cluster_markers)
    cluster_markers.layer_name = "airbase markers"

    folium.LayerControl().add_to(m)
    
    return m


''' Further Preprocessing '''

def preprocess_city_clean():
    us_cities = pd.read_csv(geo_data_folder + "uscitiesv1.4.csv")
    unique_cities = us_cities[["city","county_name"]]

    # selected   = 15520
    # unselected = 36651

    city_to_conty = {}
    for x in unique_cities.values:
        # only those cities that have no population data
        if x[0] in manual_cities_list:   
            city_to_conty.update({x[0] : x[1]})

    return unique_cities

def contains(all_locations, one_county):
    only_contain = []
    for each in all_locations:
        if one_county in each:
            only_contain.append(each)
    return only_contain

def clean_location_by_countie_list(df_tst):
    
    #ist_counties = list(df_sightings_per_countie["State_County"])
    #soll_counties = list(full_locations["State_County"])

    all_locations = df_tst.Location.unique()
    old_to_new_locaion = {}
    for one_county in tqdm_notebook(soll_counties):
        current_loc = one_county.split("_")[1]
        to_replace = contains(all_locations, current_loc)
        for each_replacement in to_replace:
            old_to_new_locaion.update({each_replacement: current_loc})
    
    # replace old to new locations
    df_tst.Location.replace(old_to_new_locaion, inplace=True)
    return df_tst


''' imports before plot'''

df_tst = pd.read_json("./geo_data/sightings_for_maps_FINAL_joe.json")
normal_sights = pd.read_json("./geo_data/normal_sights.json")
full_locations = pd.read_json("./geo_data/full_locations_index.json")
df_population_all = process_population_data()
