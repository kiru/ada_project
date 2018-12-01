import pandas as pd
    
import matplotlib.pyplot as plt
import numpy as np

def get_reports_having_n_notes(df_with_noforc_notes, n):
    res = df_with_noforc_notes[df_with_noforc_notes["nuforc_note"].str.len() == n]
    return res

def get_noforc_note_count_distribution(df):
    dist = df["nuforc_note"].str.len().value_counts()
    return dist

def plot_distribution_of_notes(df):
    dist = get_noforc_note_count_distribution(df)
    plt.figure(figsize=((15,10)))
    ax = plt.subplot()
    ax.set_yscale("log")
    plt.title("Distribution of count of NUFORC Notes")
    plt.xlabel("count")
    plt.ylabel("Occurences")
    plt.xticks(np.arange(10))
    plt.bar(dist.index, dist.values)
    plt.show()

