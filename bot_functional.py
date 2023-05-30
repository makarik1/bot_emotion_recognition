import librosa
import telebot
from pathlib import Path
from telebot import types
import config
from emotion_recognition import emotion_from_photo, emotion_from_voice, laplas
import soundfile as sf

emotions_from_photo = {}
dialog_states = {}
bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def start (message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    send_mess = f"<b>Привет, {message.from_user.first_name}</b>!\nПришли свое фото!"
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)
    dialog_states[message.chat.id] = {'state': 'waiting_photo'}


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    if dialog_states[message.chat.id]['state'] != 'waiting_photo':
        if dialog_states[message.chat.id]['state'] == 'waiting_voice':
            bot.send_message(message.chat.id, 'Отправь голосовое сообщение!')
    else:
        markup = telebot.types.ReplyKeyboardRemove()
        # создадим папку если её нет
        Path(f'files_from_user/{message.chat.id}/photos').mkdir(parents=True, exist_ok=True)

        # сохраним изображение
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        print(file_info)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'files_from_user/{message.chat.id}/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        print(src)

        # Обработка полученного фото
        emotions_from_photo = emotion_from_photo(src)
        if len(emotions_from_photo) == 0:
            bot.send_message(message.chat.id, 'На фото отсутствует лицо! Пришли другое фото')
        else:
            bot.send_message(message.chat.id, 'Спасибо за фото! Запиши голосовое сообщение', parse_mode='html', reply_markup=markup)
            dialog_states[message.chat.id] = {'state': 'waiting_voice', 'emotions_from_photo': emotions_from_photo}


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    if dialog_states[message.chat.id]['state'] != 'waiting_voice':
        if dialog_states[message.chat.id]['state'] == 'waiting_photo':
            bot.send_message(message.chat.id, 'Отправь фото!')
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # создать папку если её нет
        Path(f'files_from_user/{message.chat.id}/voice').mkdir(parents=True, exist_ok=True)

        file_info = bot.get_file(message.voice.file_id)
        print(file_info)
        downloaded_file = bot.download_file(file_info.file_path)

        src = f'files_from_user/{message.chat.id}/' + file_info.file_path

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        src_wav = f'{src.split(".")[0]}.wav'

        y, sr = librosa.load(src)
        sf.write(src_wav, y, sr)
        print(src)

        emo_by_voice = emotion_from_voice(src_wav)

        if len(emo_by_voice) == 0:
            bot.send_message(message.chat.id, 'Голос не распознан! Пришли другое голосовое сообщение')
        else:
            print('Мимика: ', dialog_states[message.chat.id]['emotions_from_photo'],' Голос: ', emo_by_voice)
            emo_by_voice_and_photo = laplas(dialog_states[message.chat.id]['emotions_from_photo'], emo_by_voice)
            print('Эмоция (мимика и голос):', emo_by_voice_and_photo)

            if emo_by_voice_and_photo == 'angry':
                emo = 'злость'
            elif emo_by_voice_and_photo == 'disgust':
                emo = 'отвращение'
            elif emo_by_voice_and_photo == 'fear':
                emo = 'страх'
            elif emo_by_voice_and_photo == 'happy':
                emo = 'радость'
            elif emo_by_voice_and_photo == 'sad':
                emo = 'грусть'
            elif emo_by_voice_and_photo == 'surprise':
                emo = 'удивление'
            elif emo_by_voice_and_photo == 'neutral':
                emo = 'нейтральная'

            dialog_states[message.chat.id] = {'state':'end'}
            btn_back = "Вернуться в начало"
            markup.add(btn_back)
            bot.send_message(message.chat.id, f'Определена эмоция - {emo}', parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_situation(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if dialog_states[message.chat.id]['state'] != 'end':
        if dialog_states[message.chat.id]['state'] == 'waiting_photo':
            bot.send_message(message.chat.id, 'Отправь фото!')
        elif dialog_states[message.chat.id]['state'] == 'waiting_voice':
            bot.send_message(message.chat.id, 'Отправь голосовое сообщение!')
    else:
        if message.text == "Вернуться в начало":
            start(message)
        else:
            bot.send_message(message.chat.id, 'Чтобы начать заново, введите команду /start')

bot.infinity_polling()