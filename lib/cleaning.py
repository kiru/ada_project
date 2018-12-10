import pandas as pd
import re
import numpy as np
import folium
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None  # default='warn'

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
    #print("splitting Location..")
    df_splitted_locaiton = df_ufo_reports['Location'].str.split(',', n=1)
    df_ufo_reports['Location'] = df_splitted_locaiton.str[0]
    df_ufo_reports['State'] = df_splitted_locaiton.str[1]

    # clear unwanted characters
    #print("cleaning Location..")
    df_ufo_reports['Location'] = df_ufo_reports['Location'].astype(str).apply(lambda x: x.strip())
    
    #print("cleaning State..")
    filter_nan_states = pd.isnull(df_ufo_reports["State"])
    df_ufo_reports = df_ufo_reports[~filter_nan_states]
    df_ufo_reports['State'] = df_ufo_reports['State'].apply(lambda x: x.strip())
    
    #print("cleaning Reported")
    df_ufo_reports['Reported'] = df_ufo_reports['Reported'].apply(lambda x: x.strip())
    
    #print("cleaning Posted..")    
    df_ufo_reports['Posted'] = df_ufo_reports['Posted'].apply(lambda x: x.strip())
    
    # re-arrange columns
    #print("re-ordering columns..")
    df_ufo_reports = df_ufo_reports[["Duration","Location","State","Occurred","Posted","Reported","Shape","Summary","url"]]
    
    #print("done")
    return df_ufo_reports

# return df without and with madar reports
def seperate_madar_reports(df):
    filter_madar = df["Summary"].str.contains("MADAR Node")
    madar_reports = df[filter_madar]
    clean_reports = df[~filter_madar]
    return clean_reports, madar_reports


def clean_duration_get_min(df):
    """
    Cleans the duration section by dropping all values, which are more than a week
    Cleans the time formats and converts all of the to 'min'
    By cleaning the data we are left with 86% of the intial data,
    Which is reasonable for us, as initially there were about 10000 different
    Time formats
    Returns:
        --cleaned series with updated durations in min
    """
    df_dummy = df.Duration.copy()
    df_dummy = df_dummy.to_frame()
    df_dummy.Duration = df_dummy.Duration.str.lower()
    df_dummy = df_dummy.dropna()
    df_dummy['time_format'] = df_dummy.Duration
    hr_time = df_dummy.copy()
    hr_time.Duration = hr_time.Duration[hr_time.Duration.str.contains('1 hr')]
    hr_time = hr_time.dropna()
    hr_time.Duration = 60
    hr_time.time_format = 'min'
    hrs_time = df_dummy.copy()
    hrs_time.Duration = hrs_time.Duration[hrs_time.Duration.str.contains('hrs')]
    hrs_time = hrs_time.dropna()
    hrs_time.Duration = hrs_time.Duration.str.replace('[:-]', '.')
    hrs_time.Duration = hrs_time.Duration.str.replace(' 1/2', '.5')
    hrs_time.Duration = hrs_time.Duration.str.replace('/', '.')
    repl = lambda m: m.group('one')
    hrs_time.Duration = hrs_time.Duration.str.replace(r"(?P<one>.*)hrs.*", repl, regex=True)
    hrs_time.Duration = hrs_time.Duration.str.replace(r"[^0-9]*(?P<one>[0-9][0-9 \.]*)[\w\. ]*", repl, regex=True)
    hrs_time.Duration = hrs_time.Duration.str.replace('[+a-z ]', '')
    hrs_time.time_format = 'hour'
    manual_drop_hrs = [111938, 97125, 92361, 87440, 110228, 45333, 80653, 58194, 55810, 
                       54939, 110807, 54694, 30841, 57254]
    hrs_time = hrs_time.drop(manual_drop_hrs)
    hrs_time.Duration = hrs_time.Duration[~(hrs_time.Duration == '')]
    hrs_time = hrs_time.dropna()
    hrs_time.Duration = hrs_time.Duration.astype(float)
    hrs_time.Duration = hrs_time.Duration*60
    hrs_time.time_format = 'min'
    hour_time = df_dummy.copy()
    hour_time.Duration = hour_time.Duration[hour_time.Duration.str.contains('hour')]
    hour_time = hour_time.dropna()
    hour_time.Duration = hour_time.Duration.str.replace('[:-]', '.')
    hour_time.Duration = hour_time.Duration.str.replace(' 1/2', '.5')
    hour_time.Duration = hour_time.Duration.str.replace('/', '.')
    hour_time.Duration = hour_time.Duration.str.replace(r"(?P<one>.*)hour.*", repl, regex=True)
    hour_time.Duration = hour_time.Duration.str.replace(r"[^0-9]*(?P<one>[0-9][0-9 \.]*)[\w\. ]*", repl, regex=True)
    hour_time.Duration = hour_time.Duration.str.replace('[+a-z ?\(\)&"`,!>;]', '')
    hour_time.Duration = hour_time.Duration.str.replace('([.]{2,})', '')
    manual_drop_hours = [109182, 102324, 96844, 93487, 93353, 80915, 88291, 78633,
                         63452, 66319, 67243, 44816, 22126, 30095, 68130, 91121, 
                        80095, 71731, 61714, 38278, 24674, 107114, 111918]
    hour_time = hour_time.drop(manual_drop_hours)
    hour_time.Duration = hour_time.Duration.str.replace('\.$', '')
    hour_time.time_format = 'hour'
    hour_time.Duration = hour_time.Duration[~(hour_time.Duration == '')]
    hour_time = hour_time.dropna()
    hour_time.Duration = hour_time.Duration.astype(float)
    hour_time.Duration = hour_time.Duration*60
    hour_time.time_format = 'min'
    minutes_time = df_dummy.copy()
    minutes_time.Duration = minutes_time.Duration.dropna()[minutes_time.Duration.dropna().str.contains('min')]
    minutes_time.time_format = 'min'
    minutes_time = minutes_time.dropna()
    minutes_time.Duration = minutes_time.Duration.str.replace(' 1/2', '.5')
    minutes_time.Duration = minutes_time.Duration.str.replace('to', '-')
    minutes_time.Duration = minutes_time.Duration.str.replace('or', '-')
    minutes_time.Duration = minutes_time.Duration.str.replace('[/:]', '.')
    minutes_time['Duration'] = minutes_time.Duration.str.replace(r"(?P<one>.*)hour.*", repl, regex=True)
    minutes_time['Duration'] = minutes_time.Duration.str.replace(r"[^0-9]*(?P<one>[0-9][0-9 -\.]*)[\w\. ]*", repl, regex=True)
    minutes_time['Duration'] = minutes_time.Duration.str.replace('[+a-z ?±*\(\)½!<>\\\\=~&"á`,\'!>;\[\]@]', '')
    minutes_time['Duration'] = minutes_time.Duration.str.replace('([.]{2,})', '')
    minutes_time['Duration'] = minutes_time.Duration.str.replace('([-]{2,})', '')
    minutes_manual_drop = [2708, 7632, 17491, 26323, 17743, 19051, 21642, 25011,
                           27849, 28293, 35538, 39992, 75636, 78172, 82754, 93849,
                           95787, 4126, 24350, 95915, 102106, 4627, 85033, 85683, 
                           14141, 16443, 69234, 77029, 101165, 42895, 19145, 56129, 
                          75795, 115300, 113583, 112874, 105620, 88135, 87478, 75795, 
                          60077, 55454, 78279, 113942, 43457, 4597, 6962, 9217, 19169, 
                           32546, 41128, 61391, 63575, 82235, 101547, 32357, 89937]
    minutes_time = minutes_time.drop(minutes_manual_drop)
    minutes_time['Duration'] = minutes_time.Duration.str.replace('\-$', '')
    minutes_time.Duration = minutes_time.Duration.str.replace('\.$', '')
    minutes_time.Duration = minutes_time.Duration.str.replace('\.-$', '')
    minutes_time.Duration = minutes_time.Duration[~(minutes_time.Duration == '')]
    minutes_time = minutes_time.dropna()
    extended_duration = minutes_time[minutes_time.Duration.str.contains('-')]
    seperated_duration = extended_duration.Duration.str.split('-')
    seperated_duration = seperated_duration[~(seperated_duration.str[0] == '')]
    seperated_duration = seperated_duration[~(seperated_duration.str[1] == '')]
    calculated_averages_of_durations = (seperated_duration.str[0].astype(float)+seperated_duration.str[1].astype(float))/2
    minutes_time.update(calculated_averages_of_durations)
    minutes_time.Duration = minutes_time.Duration.astype(str).str.replace('[-]', '')
    minutes_time.Duration = minutes_time.Duration[~(minutes_time.Duration == '')]
    minutes_time = minutes_time.dropna()
    minutes_time.Duration = minutes_time.Duration.astype(float)

    sec_time = df_dummy.copy()
    sec_time.Duration = sec_time.Duration.dropna()[sec_time.Duration.dropna().str.contains('sec')]
    sec_time.time_format = 'sec'
    sec_time = sec_time.dropna()
    sec_time.Duration = sec_time.Duration.str.replace(' 1/2', '.5')
    sec_time.Duration = sec_time.Duration.str.replace('to', '-')
    sec_time.Duration = sec_time.Duration.str.replace('or', '-')
    sec_time.Duration = sec_time.Duration.str.replace('[/:]', '.')
    repl = lambda m: m.group('one')
    sec_time['Duration'] = sec_time.Duration.str.replace(r"(?P<one>.*)sec.*", repl, regex=True)
    sec_time['Duration'] = sec_time.Duration.str.replace(r"[^0-9]*(?P<one>[0-9][0-9 -\.]*)[\w\. ]*", repl, regex=True)
    sec_time['Duration'] = sec_time.Duration.str.replace('[+a-z ?±*\(\)½!<>\\\\=~&"á`,\'!>;\[\]@]', '')
    sec_time['Duration'] = sec_time.Duration.str.replace('([.]{2,})', '')
    sec_time['Duration'] = sec_time.Duration.str.replace('([-]{2,})', '')
    sec_time['Duration'] = sec_time.Duration.str.replace('\-$', '')
    sec_manual_drop = [17067, 42074, 21247]
    sec_time = sec_time.drop(sec_manual_drop)
    sec_time.Duration = sec_time.Duration.str.replace('\.$', '')
    sec_time.Duration = sec_time.Duration.str.replace('\.-$', '')
    sec_time.Duration = sec_time.Duration[~(sec_time.Duration == '')]
    sec_time = sec_time.dropna()

    sec_extended_duration = sec_time[sec_time.Duration.str.contains('-')]
    sec_seperated_duration = sec_extended_duration.Duration.str.split('-')
    sec_seperated_duration = sec_seperated_duration[~(sec_seperated_duration.str[0] == '')]
    sec_seperated_duration = sec_seperated_duration[~(sec_seperated_duration.str[1] == '')]
    sec_calculated_averages_of_durations = (sec_seperated_duration.str[0].astype(float) + 
                                        sec_seperated_duration.str[1].astype(float))/2

    sec_time.update(sec_calculated_averages_of_durations)
    sec_time.Duration = sec_time.Duration.astype(str).str.replace('[-]', '')
    sec_time.Duration = sec_time.Duration[~(sec_time.Duration == '')]
    sec_time = sec_time.dropna()
    sec_time.Duration = sec_time.Duration.astype(float)
    sec_time.Duration = sec_time.Duration/60
    sec_time.time_format = 'min'

    duration_list = [sec_time, minutes_time, hr_time, hrs_time, hour_time]
    duration = pd.concat(duration_list).sort_index()
    duration = duration.Duration
    
    return duration

def get_time_of_occurrence(data):
    """
    Takes the input of the whole dataframe
    Return:
       - Time and date of occurrance and report
       - Year of occurrance
    """
    occur_report = data[['Occurred', 'Reported']].copy()
    df_time_occur_report = occur_report.assign(Occurred=occur_report.Occurred.str.split('(',n=1).str[0])
    df_time_occur_report.Reported = pd.DataFrame(pd.to_datetime(occur_report.Reported))
    #Create new column for years
    #df_time_occur_report['year'] = np.nan
    df_time_occur_report.Occurred = df_time_occur_report.Occurred.str.strip()
    converted_time = to_datetime_add_year(df_time_occur_report.Occurred)
    df_time_occur_report.Occurred = converted_time
    #Assigns years of occurance to the column
    #for i in range(len(df_time_occur_report.Occurred)):
     #   df_time_occur_report.year[i] = df_time_occur_report.Occurred[i].year
    data.Occurred = df_time_occur_report.Occurred
    data.Reported = df_time_occur_report.Reported
    return data

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

# call all cleaning functions from here
def clean_data(df):
    #A
    df_clean = post_process(df)
    #B
    df_clean = split_summary(df_clean)
    #C
    df_clean, df_madar_reports = seperate_madar_reports(df_clean)
    
    df_clean = get_time_of_occurrence(df_clean)
    # ADD TIME HERE ONE
    return df_clean, df_madar_reports
    