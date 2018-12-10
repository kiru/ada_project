import pandas as pd
import requests
import re

# paths
path_img_jpg = "img/jpg/"
path_img_yt = "img/yt/"


############################ Any ############################

# function for scraping images, provide url and path to save to
def scrape_url_img(url, path, filename_set):
    #filename = url.split("/")[-1]
    filename = path+str(filename_set)

    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
    except requests.ConnectionError as e:
        print("Error: Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
        print(str(e))                    
    except requests.Timeout as e:
        print("Error: Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        print("Error: General Error")
        print(str(e))
    except KeyboardInterrupt:
        print("Error:  Someone closed the program")

# get dataframe without any zero links
def get_links_df(df):
    return df[df["link"].str.len() != 0]

# apply filter
def f(x, containing):    
    if containing in x[0]:
        return True
    else:
        return False

# return list of links with specified extension
def get_specific_links(df, containing=".jpg"):
    mask = df.link.apply(lambda x: f(x, containing))
    df_links = df[mask]
    res = list(df_links["link"])
    return res

# scrape images 
def scrape_any_images(df, extension=".jpg"):
    df_valid = get_links_df(df)
    res = get_specific_links(df_valid, extension)
    # filename is counter
    c=0
    print("collecting images..")
    for i in res:
        c+=1
        for j in i:
            scrape_url_img(j, path_img_jpg, str(c)+".jpg")
    print("done")

############################ YT ############################

yt_req = "https://img.youtube.com/vi/"
yt_img_quality = "/mqdefault.jpg"

# extract single youtube id from url
def extract_yt_id(url):
    regex = r"youtu(?:.*\/v\/|.*v\=|\.be\/)([A-Za-z0-9_\-]{11})"
    matches = re.search(regex, url)
    if matches:
        tmp_yt_id = matches.group(1)
        return tmp_yt_id

# scrape all youtube thumbnail img from df
def scrape_yt_images(df):
    df_only_yt = get_links_df(df)
    only_yt_links = get_specific_links(df_only_yt, "youtube")
    
    # filename is counter
    c = 0
    print("collecting yt images..")

    for i in only_yt_links:
        c+=1
        for j in i:
            tmp_id = extract_yt_id(j)
            if tmp_id != None:
                tmp_yt_url = yt_req+tmp_id+yt_img_quality
                scrape_url_img(tmp_yt_url, path_img_yt, str(c)+".jpg")
    print("done")