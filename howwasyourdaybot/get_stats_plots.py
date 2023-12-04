# usage
# python get_stats_plots.py --range 7d --complex-range="now"

import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
import numpy as np
import pandas as pd
from emotions import emotions_list
from phrases_multilang import plot_words, emotions_translations

import locale

lang_dict = {
    "en": "en_AU",
    "ru": "ru_RU"
}

from config import (
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
    DEFAULT_LANG
)


# influxdb imports
import influxdb_client

client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()


def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):
    """
    https://matplotlib.org/stable/gallery/statistics/confidence_ellipse.html#sphx-glr-gallery-statistics-confidence-ellipse-py
    
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


def generate_stats_plot(chat_id, range_start='none', range_stop='now()', quick_range='7d', lang=DEFAULT_LANG):
    # Set the desired language for date and time formatting
    desired_language = lang_dict.get(lang, ""])
    locale.setlocale(locale.LC_ALL, desired_language)

    if range_start == 'none':
        range_start = '-' + quick_range


    def get_arousal_and_valence(query):
        result = query_api.query(query=query)

        N_records = len(result[0].records)

        mean_arousal = np.zeros(N_records)
        mean_valence = np.zeros(N_records)
        timestamps = []

        for i in range(N_records):
            mean_arousal[i] = result[0].records[i].get_value()
            mean_valence[i] = result[1].records[i].get_value()
            timestamps.append(result[1].records[i].get_time())
            
        timestamps_numeric = date2num(timestamps)
        
        return timestamps, timestamps_numeric, mean_arousal, mean_valence
    
    def get_mood_score(query):
        result_mood_score = query_api.query(query=query)
        N_records_mood_score = len(result_mood_score[0].records)

        mood_score = np.zeros(N_records_mood_score)
        timestamps_mood_score = []

        for i in range(N_records_mood_score):
            mood_score[i] = result_mood_score[0].records[i].get_value()
            timestamps_mood_score.append(result_mood_score[0].records[i].get_time()) 
            
        timestamps_numeric_mood_score = date2num(timestamps_mood_score)
        
        return timestamps_mood_score, timestamps_numeric_mood_score, mood_score

    query = f"""from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: {range_start}, stop: {range_stop})
    |> filter(fn: (r) => r["_measurement"] == "emotion_measurement")
    |> filter(fn: (r) => r["_field"] == "mean_arousal" or r["_field"] == "mean_valence")
    |> filter(fn: (r) => r["user"] == "{chat_id}")
    """
    query_average = f"""from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: {range_start}, stop: {range_stop})
    |> filter(fn: (r) => r["_measurement"] == "emotion_measurement")
    |> filter(fn: (r) => r["_field"] == "mean_arousal" or r["_field"] == "mean_valence")
    |> filter(fn: (r) => r["user"] == "{chat_id}")
    |> timedMovingAverage(every: 5h, period: 2d)
    """
    
    timestamps, timestamps_numeric, mean_arousal, mean_valence = get_arousal_and_valence(query)
    timestamps_average, timestamps_numeric_average, mean_arousal_average, mean_valence_average = get_arousal_and_valence(query_average)

    query_mood_score = f"""from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: {range_start}, stop: {range_stop})
    |> filter(fn: (r) => r["_measurement"] == "emotion_measurement")
    |> filter(fn: (r) => r["_field"] == "mood_score")
    |> filter(fn: (r) => r["user"] == "{chat_id}")
    """ 
    query_mood_score_all = f"""from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: -10y)
    |> filter(fn: (r) => r["_measurement"] == "emotion_measurement")
    |> filter(fn: (r) => r["_field"] == "mood_score")
    |> filter(fn: (r) => r["user"] == "{chat_id}")
    """ 
    
    timestamps_mood_score, timestamps_numeric_mood_score, mood_score = get_mood_score(query_mood_score)
    timestamps_mood_score_all, timestamps_numeric_mood_score_all, mood_score_all = get_mood_score(query_mood_score_all)
    
    #####################
    ##### PLOTTING ######
    #####################

    x = mean_valence
    y = mean_arousal


    fig, axs = plt.subplot_mosaic(
        """
        D
        C
        A
        B
        B
        """, figsize=(5, 10), dpi=300
    )
    myFmt = DateFormatter('%d %b')


    ####################
    ### MOOD SCORE   ###
    ####################

    axs['D'].scatter(timestamps_mood_score, mood_score, s=10, alpha=0.4, edgecolor='none')

    # moving average
    df = pd.DataFrame({'timestamps': timestamps_mood_score, 'mood_score': mood_score})

    # Convert timestamps to days
    df['days'] = date2num(df['timestamps'])
    df['days'] = (df['timestamps'] - df['timestamps'].min()) / pd.Timedelta(days=1)
    window_size = 5  # in days
    df['mood_score_smooth'] = df['mood_score'].rolling(window=window_size, min_periods=1).mean()
    df['mood_score_std'] = df['mood_score'].rolling(window=int(window_size), min_periods=1).std()

    # Plot the smooth rolling average
    axs['D'].plot(df['timestamps'], df['mood_score_smooth'], color='C0')
    axs['D'].fill_between(df['timestamps'], df['mood_score_smooth'] - df['mood_score_std'], df['mood_score_smooth'] + df['mood_score_std'], color='C0', alpha=0.3, edgecolor='none')


    axs['D'].margins(x=0)
    axs['D'].tick_params(axis='x', rotation=45)
    axs['D'].xaxis.set_major_formatter(myFmt)
    axs['D'].set_ylim(-10, 10)
    axs['D'].set_ylabel('Mood score')

    ####################
    ### MOOD HIST    ###
    ####################

    axs['C'].hist(mood_score, alpha=0.5, range=(-10, 10), density=True, rwidth=0.6, bins=21, zorder=10, label=plot_words["requested"][lang])
    axs['C'].hist(mood_score_all, alpha=0.5, range=(-10, 10), density=True, rwidth=1, bins=21, label=plot_words["all_time"][lang])
    axs['C'].legend()
    axs['C'].set_xlabel(plot_words["mood_score"][lang])
    axs['C'].set_yticks([])

    ####################
    ### EMOTIONS     ###
    ####################

    axs['A'].scatter(timestamps, mean_valence, s=10, alpha=0.4, edgecolor='none')
    axs['A'].scatter(timestamps, mean_arousal, s=10, alpha=0.4, edgecolor='none')

    axs['A'].plot(timestamps_average, mean_valence_average, lw=2, label=plot_words["valence"][lang])
    axs['A'].plot(timestamps_average, mean_arousal_average, lw=2, label=plot_words["arousal"][lang])

    axs['A'].legend()

    axs['A'].set_ylim(-1, 1)
    axs['A'].set_yticks([-1, 0, 1])
    axs['A'].xaxis.set_major_formatter(myFmt)
    axs['A'].margins(x=0)
    axs['A'].tick_params(axis='x', rotation=45)

    ####################
    ### RUSSELL MAP  ###
    ####################

    color = 'lightsteelblue'
    confidence_ellipse(x, y, axs['B'], n_std=1,
                    label=r'$1\sigma$', edgecolor='none', facecolor=color, alpha=0.3)
    confidence_ellipse(x, y, axs['B'], n_std=2,
                    label=r'$2\sigma$', edgecolor='none', linestyle='--', facecolor=color, alpha=0.2)
    confidence_ellipse(x, y, axs['B'], n_std=3,
                    label=r'$3\sigma$', edgecolor='none', linestyle=':', facecolor=color, alpha=0.1)


    axs['B'].scatter(x, y, c='royalblue', s=20, alpha=0.2, edgecolors='none')

    emotions = list(emotions_list.keys())
    valence = [emotion_data["valence"] for emotion_data in emotions_list.values()]
    arousal = [emotion_data["arousal"] for emotion_data in emotions_list.values()]

    for i, emotion in enumerate(emotions):
        #axs['B'].annotate(emotion, (valence[i], arousal[i]), textcoords="offset points", xytext=(0, 10), ha='center', color='gray')
        axs['B'].annotate(emotions_translations[emotion][lang], (valence[i], arousal[i]), textcoords="offset points", xytext=(0, 10), ha='center', color='gray')

    axs['B'].set_xlim(-1.2, 1.2)
    axs['B'].set_ylim(-1.2, 1.2)
    axs['B'].set_xticks([-1, 0, 1], [plot_words["negative"][lang], plot_words["neutral"][lang], plot_words["positive"][lang])
    axs['B'].set_yticks([-1, 0, 1], [plot_words["weak"][lang], plot_words["neutral"][lang], plot_words["strong"][lang]])
    #plt.gca().set_aspect('equal', adjustable='box')

    axs['B'].set_xlabel(plot_words["valence"][lang], weight='bold')
    axs['B'].set_ylabel(plot_words["arousal"][lang], weight='bold')

    plt.tight_layout()
    filename = f'stats_{chat_id}.png'
    plt.savefig(filename)

    return filename

if __name__ == "__main__":
    chat_id = 63688320
    generate_stats_plot(
        chat_id, 
        range_start='none', 
        range_stop='now()', 
        quick_range='10d'
    )
