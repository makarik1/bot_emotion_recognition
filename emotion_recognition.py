from fer import FER
import matplotlib.pyplot as plt

import librosa
import numpy as np
from tensorflow.keras.models import load_model
import scipy
import joblib
import speech_recognition as sr
import pandas as pd

def emotion_from_photo(src):
    test_image_one = plt.imread(src)
    emo_detector = FER(mtcnn=True)

    mimic_result = emo_detector.detect_emotions(test_image_one)
    print(mimic_result)

    dominant_emotion, emotion_score = emo_detector.top_emotion(test_image_one)

    if len(mimic_result) == 0:
        return mimic_result
    else:
        print(mimic_result[0].get("emotions"))
        print(dominant_emotion, emotion_score)
        return mimic_result[0].get("emotions")

def recognition_speech(src):
    r = sr.Recognizer()

    with sr.AudioFile(src) as source:
        audio = r.record(source)

    # Распознавание речи
    try:
        text = r.recognize_google(audio, language="ru-RU")
        print("Вы сказали: {}".format(text))
    except sr.UnknownValueError:
        text = None
        print("Голос не распознан")
    except sr.RequestError as e:
        text = None
        print("Ошибка сервиса {0}".format(e))

def emotion_from_voice(src):
    # Загрузка модели нейросети
    model = load_model('best_model_cnn_mp_en_tess_ravdess_savee.h5')
    model.load_weights('weights_tess_ravdess_savee.h5')

    #Загрузка настроек нормализации данных
    scaler = joblib.load('scaler.pkl')

    # Загрузка звукового файла
    y, sr = librosa.load(src)

    rs = recognition_speech(src)
    if rs is None:
        voice_result = {}
        return voice_result
    else:
        to_append = ''
        # Извлечение признаков из аудио
        chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
        rms = librosa.feature.rms(y=y)
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(y)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        log_power = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        fourier = np.abs(librosa.stft(y))
        tempogram = librosa.feature.tempogram(y=y, sr=sr)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        to_append = f'{np.mean(chroma_stft)},{np.mean(rms)},{np.mean(spec_cent)},{np.std(spec_cent)},{scipy.stats.skew(spec_cent, axis=1)[0]},{np.mean(spec_bw)},{np.mean(rolloff)},{np.std(rolloff)},{scipy.stats.skew(rolloff, axis=1)[0]},{np.mean(zcr)},{np.mean(tonnetz)},{np.mean(log_power)},{np.mean(fourier)},{np.mean(tempogram)}'
        mean_mfcc, std_mfcc = '', ''
        for e in mfcc:
            mean_mfcc += f',{np.mean(e)}'
            std_mfcc += f',{np.std(e)}'
        to_append = to_append + mean_mfcc + std_mfcc

        array_parameters = [float(item) for item in to_append.split(',')]
        array_parameters = np.array([array_parameters])
        array_parameters = scaler.transform(array_parameters)

        # Предсказание класса звука
        emo = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        pred = model.predict(array_parameters)

        voice_result = dict(zip(emo, [round(num, 2) for num in pred[0]]))
        return voice_result

def laplas(mimic,voice):
    laplas_criteria = {}
    for key in mimic.keys():
        if key in voice:
            laplas_criteria[key] = np.mean(mimic[key] + voice[key])
    dominant_emo = max(laplas_criteria, key=laplas_criteria.get)
    return dominant_emo