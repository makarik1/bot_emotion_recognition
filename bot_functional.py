import telebot
from pathlib import Path
from telebot import types
import config
from emotion_recognition import emotion_from_photo

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def start (message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_send_photo = "Отправить фото"
    btn_send_audio = "Отправить голосовое"
    btn_report = "Получить отчет"
    markup.add(btn_send_photo, btn_send_audio, btn_report)
    send_mess = f"<b>Привет, {message.from_user.first_name}</b>!\nДавай знакомиться. Я - твой дневник эмоций. Я помогу тебе определять твои эмоции. Выбери действие"
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['sendphoto'])
def sendphoto (message):
    markup = telebot.types.ReplyKeyboardRemove()
    send_mess = "Отправь своё фото, а я определю твою эмоцию"
    bot.send_message(message.chat.id, send_mess, reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    markup = telebot.types.ReplyKeyboardRemove()

    # создадим папку если её нет
    Path(f'files_from_user/{message.chat.id}/photos').mkdir(parents=True, exist_ok=True)

    # сохраним изображение
    file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
    print(len(message.photo))
    downloaded_file = bot.download_file(file_info.file_path)
    src = f'files_from_user/{message.chat.id}/' + file_info.file_path
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    print(src)

    # Обработка полученного фото
    dominant_emotion = emotion_from_photo(src)

    if (dominant_emotion == "angry"):
        send_mess = "Вижу, что ты сейчас злишься. Напиши, что произошло?"
    elif (dominant_emotion == "disgust"):
        send_mess = "Ты чувствуешь отвращение? Почему?"
    elif (dominant_emotion == "fear"):
        send_mess = "Опиши ситуацию, которая тебя напугала. Я могу тебя выслушать."
    elif (dominant_emotion == "happy"):
        send_mess = "Вижу твою радость. Готов разделить её с тобой. Поделись"
    elif (dominant_emotion == "sad"):
        send_mess = "Поделись, что вызвало у тебя грусть? Я могу тебя выслушать."
    elif (dominant_emotion == "surprise"):
        send_mess = "Вау, вижу удивление на твоем лице. Что его вызвало?"
    elif (dominant_emotion == "neutral"):
        send_mess = "Рад тебя видеть! К сожалению, я не смог определить твою эмоцию. Попробуй прислать другую фотографию"
    else:
        send_mess = "На фотографии отсутствует лицо. Пришли другое фото"
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_situation(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = "Вернуться в начало"
    if message.text == "Записать":
        send_mess = "Я всё записал. Спасибо, что делишься!"
        btn_more = "Отправить еще фото"
        markup.add(btn_more, btn_back)
        bot.send_message(message.from_user.id, send_mess, reply_markup=markup)

    elif message.text == "Не надо":
        send_mess = "Хорошо, записывать не буду"
        markup.add(btn_back)
        bot.send_message(message.from_user.id, send_mess, reply_markup=markup)

    elif message.text == "Вернуться в начало":
        start(message)

    elif message.text == "Отправить еще фото" or message.text =="Отправить фото":
        sendphoto(message)

    elif message.text == "Отправить голосовое" or message.text == "Получить отчет":
        send_mess = "Эта функция в разработке. Возвращайся позднее."
        markup.add(btn_back)
        bot.send_message(message.from_user.id, send_mess, reply_markup=markup)

    else:
        send_mess = "Давай запишем это в дневнике?"
        btn_yes = types.KeyboardButton("Записать")
        btn_no = types.KeyboardButton("Не надо")
        markup.add(btn_yes, btn_no)
        bot.send_message(message.chat.id, send_mess, reply_markup=markup)

bot.infinity_polling()