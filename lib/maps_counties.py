###
###
###


import branca
import folium
import pandas as pd

data_folder = './geo_data/'
my_USA_map = data_folder + r'us-states.json'

# counties source = https://gist.githubusercontent.com/mbostock/4090846/raw/07e73f3c2d21558489604a0bc434b3a5cf41a867/us-county-names.tsv
counties_id = pd.read_csv(data_folder+"raw.tsv", sep='\t', header=0)

# population data
population_folder = './data/'
df_population_all = pd.read_excel(population_folder + 'PctUrbanRural_County.xls')
df_population_all = df_population_all[["COUNTYNAME","POP_COU"]]

# countie-map
USA_countie_map = data_folder + r'us-topo.json'

# colorscale
colorscale = branca.colormap.linear.YlOrRd_09.scale(0, 200)


###
###
###


def sightings_per_state(df):
    # prepare data for Sightings per State plot
    sight_per_state=df['State'].value_counts()
    df=sight_per_state.to_frame()
    df.reset_index(level=0, inplace=True)
    df.columns = ['State', 'Sightings']
    
    return df


def sightings_per_countie(df):
    '''
    Sightings per county
    '''
    df = df[df['Location'] != " "]
    # prepare data for Sightings per State plot
    sight_per_state=df['Location'].value_counts()
    df=sight_per_state.to_frame()
    df.reset_index(level=0, inplace=True)
    df.columns = ['Location', 'Sightings']
    
    return df



###
###
###


def style_function(feature):
    x = counties_id[counties_id["id"] == feature["id"]]
    if len(x.values) > 0:
        x = x.values[0][1]
    else:
        x = None
    
    # Sightings per countie
    sights = df_sightings_per_countie[df_sightings_per_countie["Location"] == x]
    sights = sights["Sightings"].values.sum()
    #print(x, sights)
    
    '''
    FIXME: problem 
        - counties with same names in different states 
        - example Jackson exists ~15 times
    ''' 
    # Population for normalization
    pop = df_population_all[df_population_all["COUNTYNAME"] == x]
    pop = pop["POP_COU"].sum()
    
    return {
        'fillOpacity': 0.5,
        'weight': 0,
        'fillColor': 'white' if x is None else colorscale(sights)
    }


###
###
###

df_sightings_per_countie = 0

def plot_countie_map(df):

    df = sightings_per_state(df)
    
    df_sightings_per_countie = sightings_per_countie(df)

    
    # map init
    m = folium.Map(
        location=[48, -102],
        tiles='cartodbpositron',
        zoom_start=3
    )

    # counties
    layer_counties = folium.TopoJson(
        open(USA_countie_map),
        'objects.counties',
        style_function=style_function
    )
    layer_counties.layer_name = 'counties'
    layer_counties.add_to(m)

    # states
    m.choropleth(geo_data=my_USA_map, data=df,
                     columns=['State', 'Sightings'],
                     key_on='feature.id',
                     fill_color='YlGn', fill_opacity=0.2, line_opacity=0.2,
                     legend_name='UFO sightings in the US',
                     name='states')

    folium.LayerControl().add_to(m)

    return m