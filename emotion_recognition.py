from fer import FER
import matplotlib.pyplot as plt

def emotion_from_photo(src):
    test_image_one = plt.imread(src)
    emo_detector = FER(mtcnn=True)

    captured_emotions = emo_detector.detect_emotions(test_image_one)
    print(captured_emotions)

    plt.imshow(test_image_one)
    dominant_emotion, emotion_score = emo_detector.top_emotion(test_image_one)
    print(dominant_emotion, emotion_score)
    return dominant_emotion
