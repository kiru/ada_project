import pandas as pd
    
import matplotlib.pyplot as plt
import numpy as np

# get reports with n features [note | link]
def get_reports_having_n_elements(df_with_noforc_notes, n, feature):
    res = df_with_noforc_notes[df_with_noforc_notes[feature].str.len() == n]
    return res

def get_noforc_note_count_distribution(df, feature):
    dist = df[feature].str.len().value_counts()
    return dist

def plot_distribution_of_notes(df, feature):
    dist = get_noforc_note_count_distribution(df, feature)
    plt.figure(figsize=((15,10)))
    ax = plt.subplot()
    ax.set_yscale("log")
    plt.title("Distribution of count of "+feature)
    plt.xlabel("count")
    plt.ylabel("Occurences")
    plt.xticks(np.arange(10))
    plt.bar(dist.index, dist.values)
    plt.show()

