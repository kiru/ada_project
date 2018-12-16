import cv2
from sklearn.cluster import KMeans

from PIL import Image
import numpy as np
import os
import math
import pandas as pd


img_path = "img/yt/"

# calculate the dominant color of a picture using K-Means
def dominantColors(img_path, clusters):
    #read image
    img = cv2.imread(img_path)

    #convert to rgb from bgr
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #reshaping to a list of pixels
    img = img.reshape((img.shape[0] * img.shape[1], 3))

    #save image after operations
    img_path = img

    #using k-means to cluster pixels
    kmeans = KMeans(n_clusters = clusters)
    kmeans.fit(img)

    #the cluster centers are our dominant colors.
    colors = kmeans.cluster_centers_

    #save labels
    labels = kmeans.labels_

    #returning after converting to integer from float
    return colors.astype(int)

# ploting the images
def plot_image_grid(images, max_horiz=np.iinfo(int).max):
    n_images = len(images)
    n_horiz = min(n_images, max_horiz)
    h_sizes, v_sizes = [0] * n_horiz, [0] * (n_images // n_horiz)
    
    for i, im in enumerate(images):
        h, v = i % n_horiz, i // n_horiz
        h_sizes[h] = max(h_sizes[h], im.size[0])
        v_sizes[v] = max(v_sizes[v], im.size[1])
    h_sizes, v_sizes = np.cumsum([0] + h_sizes), np.cumsum([0] + v_sizes)
    im_grid = Image.new('RGB', (h_sizes[-1], v_sizes[-1]), color='white')
    
    for i, im in enumerate(images):
        im_grid.paste(im, (h_sizes[i % n_horiz], v_sizes[i // n_horiz]))
    return im_grid

# returns luminance
def lum (r,g,b):
    return math.sqrt( .241 * r + .691 * g + .068 * b )

# returns df of images and
def plot_sorted_images():
    img_list = os.listdir(img_path)

    # load images from os
    images = [Image.open(img_path+img) for img in img_list if img.endswith(".jpg")]

    # calculate rgb on images
    dom_cols = [dominantColors(img_path+img, 1) for img in img_list if img.endswith(".jpg")]

    # put both into a df
    df_img = pd.DataFrame({"color":dom_cols, "img":images})

    # calculate luminosity for each row
    luminance = df_img['color'].apply(lambda rgb: lum(rgb[0][0],rgb[0][1],rgb[0][2]))
    df_img["lum"] = luminance

    # sort dataframe by luminosity
    df_img = df_img.sort_values(by=['lum'])

    # plot images
    images = df_img["img"]

    if df_img.shape[0]%2 is not 0:
        images = df_img["img"]
        images = images[0:df_img.shape[0]-1]

    grid_image = plot_image_grid(images, int(len(images)/4))
    return grid_image, df_img
