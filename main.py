import telebot
import pandas as pd
import requests as rq

bot = telebot.TeleBot('5634384319:AAFABGyux5ZnSQS7ETGap56dWpEjjJgIfvE')
modem_id = ''
per_page = ''
mes_date = ''
red_mes = dict
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.114 '
                  'YaBrowser/22.9.1.1110 (beta) Yowser/2.5 Safari/537.36',
    'authorization': 'Bearer v2.company.m4LRRk48jmKB6R75AjTRdiOEC73lXpvJ',
}

url = ''


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/power":
        bot.send_message(message.from_user.id, "Введите номер счетчика")
        bot.register_next_step_handler(message, get_modem_id)  # следующий шаг – функция get_name
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "/power - получение показаний")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help для помощи")


def get_modem_id(message):  # Номер счетчика
    global modem_id
    modem_id = message.text
    bot.send_message(message.from_user.id, 'Введите количество сообщений')
    bot.register_next_step_handler(message, get_per_page)
    # print(modem_id, per_page)


def get_per_page(message):  # Количество сообщений
    global per_page
    per_page = message.text
    bot.send_message(message.from_user.id, 'Введите дату паказаний в формате гггг-мм-дд')
    bot.register_next_step_handler(message, get_url)
    # print(per_page)


def get_url(message):  # Создание url
    global url
    global mes_date
    mes_date = message.text
    if message:
        url = 'https://backend.luch-system.ru/v1/messages?modemId=' \
              + modem_id + \
              '&perPage=' \
              + per_page + \
              '&noDupes=true'
        bot.register_next_step_handler(message, get_messages)
        print(url)


def get_messages(message):
    global red_mes
    if message:
        raw_messages = rq.get(url, headers=headers)
        messages = raw_messages.json()
        for item in messages:
            if int(item['decodedPayload'][0:2]) == 10:
                red_mes = {
                    'energy': {
                        'id': item['decodedPayload'][0:2],
                        'date': str(pd.to_datetime(int(item['decodedPayload'][2:10], 16), unit='s'))[0:10],
                        't_sum': str(int(item['decodedPayload'][10:18], 16)),
                    },
                    'Save_date': item['timeSaved'][0:10]
                }
                print(red_mes)
    if mes_date == red_mes['Save_date']:
        bot.send_message(message.from_user.id, f'Дата сохранения  {red_mes["Save_date"]}\n '
                                               f'Дата в сообщении {red_mes["energy"]["date"][0:10]}\n '
                                               f'Суммарная энергия = {red_mes["energy"]["t_sum"][:-3]}.'
                                               f'{red_mes["energy"]["t_sum"][-3:]}')
    else:
        bot.send_message(message.from_user.id, f'В запрошенном количестве сообщений нет показаний на {mes_date}')


bot.polling(none_stop=True, interval=0)
