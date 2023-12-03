import matplotlib.pyplot as plt
import numpy as np
from emotions import emotions_list
# get translations
from phrases_multilang import emotions_translations, plot_words
 
def plot_emotions(base_filename='emotions', lang='en'):
    emotions = list(emotions_list.keys())
    valence = [emotion_data["valence"] for emotion_data in emotions_list.values()]
    arousal = [emotion_data["arousal"] for emotion_data in emotions_list.values()]

    plt.figure(figsize=(10, 6))
    plt.scatter(valence, arousal, marker='o', s=80, c=np.arctan2(valence, arousal), cmap='hsv', label='Emotions')

    for i, emotion in enumerate(emotions):
        #plt.annotate(emotion, (valence[i], arousal[i]), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.annotate(emotions_translations[emotion][lang], (valence[i], arousal[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    #plt.gca().set_aspect('equal', adjustable='box')

    plt.xlabel(plot_words['valence'][lang], weight='bold')
    plt.ylabel(plot_words['arousal'][lang], weight='bold')

    plt.title(plot_words['emotions'][lang])
    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    plt.tick_params(direction='in')

    plt.xticks([-1, 0, 1], [plot_words['negative'][lang], plot_words['neutral'][lang], plot_words['positive'][lang]])
    plt.yticks([-1, 0, 1], [plot_words['weak'][lang], plot_words['neutral'][lang], plot_words['strong'][lang]])
    #plt.grid(True, linestyle='--', alpha=0.6)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()

    filename = base_filename + '_' + lang + '.png'
    plt.savefig(filename)
    return filename
    #plt.show()
    

if __name__ == "__main__":
    plot_emotions()