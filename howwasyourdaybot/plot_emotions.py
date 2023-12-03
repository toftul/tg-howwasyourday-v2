import matplotlib.pyplot as plt
import numpy as np
from emotions import emotions_list

 
def plot_emotions():
    emotions = list(emotions_list.keys())
    valence = [emotion_data["valence"] for emotion_data in emotions_list.values()]
    arousal = [emotion_data["arousal"] for emotion_data in emotions_list.values()]

    plt.figure(figsize=(10, 6))
    plt.scatter(valence, arousal, marker='o', s=80, c=np.arctan2(valence, arousal), cmap='hsv', label='Emotions')

    for i, emotion in enumerate(emotions):
        plt.annotate(emotion, (valence[i], arousal[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    #plt.gca().set_aspect('equal', adjustable='box')

    plt.xlabel('Valence', weight='bold')
    plt.ylabel('Arousal', weight='bold')

    plt.title('Emotions')
    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    plt.tick_params(direction='in')

    plt.xticks([-1, 0, 1], ['Negative', 'Neutral', 'Positive'])
    plt.yticks([-1, 0, 1], ['Weak', 'Neutral', 'Strong'])
    #plt.grid(True, linestyle='--', alpha=0.6)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.savefig('emotions.png')
    #plt.show()
    

if __name__ == "__main__":
    plot_emotions()