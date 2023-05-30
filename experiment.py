import numpy as np

def laplas(mimic,voice):
    laplas_criteria = {}
    for key in mimic.keys():
        if key in voice:
            laplas_criteria[key] = np.mean(mimic[key] + voice[key])
    dominant_emo = max(laplas_criteria, key=laplas_criteria.get)
    return dominant_emo


mimic =  {'angry': 0.09, 'disgust': 0.0, 'fear': 0.03, 'happy': 0.25, 'sad': 0.22, 'surprise': 0.0, 'neutral': 0.41}
voice =  {'angry': 0.03, 'disgust': 0.74, 'fear': 0.14, 'happy': 0.01, 'sad': 0.07, 'surprise': 0.0, 'neutral': 0.0}



result = laplas(mimic,voice)
print(result)