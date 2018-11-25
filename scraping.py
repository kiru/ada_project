# -*- coding: utf-8 -*-

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from tqdm import tnrange, tqdm_notebook
from multiprocessing import Pool

url = 'http://www.nuforc.org/webreports/'

def fetch_shape_urls():
    shape_request = requests.get('http://www.nuforc.org/webreports/ndxshape.html')
    shoup_shape = BeautifulSoup(shape_request.text, 'html.parser')
    shape_urls_find = shoup_shape.find('tbody')
    
    shape_urls = []
    for row in shape_urls_find.findAll('tr'):
        cells = row.findAll('td')
        shape_urls.append(cells[0].find('a')['href'])
    return shape_urls

def to_url(html):
    list_of_urls = []
    m = requests.get(url + html)
    soup_url = BeautifulSoup(m.text, 'html.parser')
    find_urls = soup_url.find('tbody')
    for row in find_urls.findAll('tr'):
        cells = row.findAll('td')
        list_of_urls.append(cells[0].find('a')['href'])
    return list_of_urls

def fetch_all_sighting_urls(shape_urls):
    with Pool(4) as pool:
        list_of_urls = []
        for each in tqdm_notebook(pool.imap(to_url, shape_urls), total=len(shape_urls)):
            list_of_urls.extend(each)
        return list_of_urls

def store_to_json(all_reporting_urls, file_name):
    urls = pd.DataFrame({ 'url': [all_reporting_urls] })
    urls.to_json(path_or_buf=file_name)

''' 
return single report as dictionary
    Occurred
    Reported
    Posted
    Location
    Shape
    Duration
    > Summary
'''
def getSingleReport(ufo_sightings):
    dd = {}
    td_list=ufo_sightings.findAll("td")

    # first td
    row_ = td_list[0].findAll(text=True)
    for item in row_:            
        splitvals = item.split(':', 1)
        if len(splitvals) == 2:
            dd[splitvals[0]] = splitvals[1]
    
    # second td      
    row_ = str(td_list[1].findAll(text=True))
    dd["Summary"] = row_
    return dd

def do_one_process(each_url):
    #progress.update(1)
    #pbar.update(1)
    sighting_url = url + each_url
    r = requests.get(sighting_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    ufo_report = soup.find('tbody')
    try:
        dict_data_single_report = getSingleReport(ufo_report)
        dict_data_single_report["url"] = sighting_url
        return dict_data_single_report
    except:
        print("Could not fetch ", sighting_url)
        return {"url": sighting_url}


# return dataframe of dictionaries of reports
def build_report_dataframe(random_urls):
    
    df_reports_ = pd.DataFrame()
    
    with Pool(500) as pool:
        #result = pool.imap(do_one_process, random_urls)
        for each in tqdm_notebook(pool.imap(do_one_process, random_urls), total=len(random_urls)):
            df_reports_ = df_reports_.append(each, ignore_index=True)
            #print(each)
        #print(result)
    return df_reports_
