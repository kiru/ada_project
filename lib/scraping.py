# -*- coding: utf-8 -*-
'''
This file contains all functions related to getting the data from
the NUFORC web page.
'''

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from tqdm import tnrange, tqdm_notebook
from multiprocessing import Pool

url = 'http://www.nuforc.org/webreports/'

def fetch_shape_urls():
    '''
    The NUFORC lists the reports by shape.
    The shape pages contains the links to the reports of that shape.

    This functions scrapes all the shapes from that pages and returns
    them as a list.

    :return: a list of shape_urls
    '''
    shape_request = requests.get('http://www.nuforc.org/webreports/ndxshape.html')
    shoup_shape = BeautifulSoup(shape_request.text, 'html.parser')
    shape_urls_find = shoup_shape.find('tbody')
    
    shape_urls = []
    for row in shape_urls_find.findAll('tr'):
        cells = row.findAll('td')
        link = cells[0].find('a')['href']
        shape_urls.append(link)
    return shape_urls

def to_url(reports_page):
    '''
    Extracts all report urls from given html page.

    :param reports_page: html of the pages with reports
    :return: list of urls of the reports
    '''
    list_of_urls = []
    request_page = requests.get(url + reports_page)

    soup_url = BeautifulSoup(request_page.text, 'html.parser')
    find_urls = soup_url.find('tbody')
    for row in find_urls.findAll('tr'):
        cells = row.findAll('td')
        link = cells[0].find('a')['href']
        list_of_urls.append(link)

    return list_of_urls

def fetch_all_sighting_urls(shape_urls):
    '''
    :param shape_urls: list of pages which contains a list of reports
    :return: the list of reports from all the given urls
    '''

    # We parallelize here to make the whole scraping faster
    with Pool(4) as pool:
        list_of_urls = []
        for each in tqdm_notebook(pool.imap(to_url, shape_urls), total=len(shape_urls)):
            list_of_urls.extend(each)
        return list_of_urls

def store_to_json(all_reporting_urls, file_name):
    urls = pd.DataFrame({ 'url': [all_reporting_urls] })
    urls.to_json(path_or_buf=file_name)

def get_single_report(ufo_sighting_page):
    '''
    :param ufo_sighting_page:
    the html page of a single report

    :return:
    single report as dictionary with the keys being:
     - Occurred
     - Reported
     - Posted
     - Location
     - Shape
     - Duration
     - Summary

    '''
    report_as_dict = {}
    td_list = ufo_sighting_page.findAll("td")

    # first td
    rows = td_list[0].findAll(text=True)
    for each_row in rows:
        splitvals = each_row.split(':', 1)

        # is a valid info we want to extract
        if len(splitvals) == 2:
            report_as_dict[splitvals[0]] = splitvals[1]
    
    # second td
    rows = td_list[1].text
    report_as_dict["Summary"] = rows

    return report_as_dict

def request_one_report(one_report_url):
    '''
    Scrape information from given page url

    :param one_report_url:
    :return:  the information of the report as dictionary
    '''

    sighting_url = url + one_report_url
    request_url = requests.get(sighting_url)
    soup = BeautifulSoup(request_url.text, 'html.parser')

    ufo_report = soup.find('tbody')
    try:
        dict_data_single_report = get_single_report(ufo_report)
        dict_data_single_report["url"] = sighting_url
        return dict_data_single_report
    except:
        # In case the page is not found
        print("Could not fetch ", sighting_url)
        return {"url": sighting_url}

def build_report_dataframe(list_of_report_urls):
    '''
    return dataframe of dictionaries of reports
    :param list_of_report_urls:
    :return:
    All the scraped reports as pandas data frame.
    '''

    df_reports = pd.DataFrame()
    
    with Pool(500) as pool:

        for each in tqdm_notebook(pool.imap(request_one_report, list_of_report_urls),
                                  total=len(list_of_report_urls)):
            df_reports = df_reports.append(each, ignore_index=True)
    return df_reports
