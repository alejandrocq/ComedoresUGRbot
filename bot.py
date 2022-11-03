#!/usr/bin/python3
import locale
import logging as log
import os
import re
import signal
import subprocess
import sys
import threading
import time
import urllib
from datetime import datetime, date, timedelta

import telebot
from unidecode import unidecode

IMAGES_PATH = 'images/'
NEW_IMAGES_PATH = 'images-new/'
PDF_FILENAME = 'menu.pdf'

data_timer = None
sub_timer = None
subscriptions = []

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

# Get bot token from environment variable BOT_TOKEN
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'), threaded=False)


@bot.message_handler(commands=['start'])
def welcome_message(message):
    msg = "¡Ya estamos listos para empezar! Escribe /lunes , /martes , ... o /hoy para obtener el menú correspondiente. También puedes obtener el menú semanal en pdf usando /pdf o suscribirte al menú diario usando /suscripcion . Si necesitas ayuda, usa /help."
    log_command(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['help'])
def help_message(message):
    msg = "Si deseas obtener el menú de un día concreto, usa /lunes, /martes... o /hoy . Además, escribiendo /pdf puedes obtener el documento pdf con el menú semanal completo o suscribirte al menú diario usando /suscripcion"
    log_command(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['lunes', 'martes', 'miercoles', 'jueves',
                               'viernes', 'sabado'])
def send_menu(message):
    # Parse command correctly (avoid content after @)
    regex = re.compile('\/\w*')
    command = regex.search(message.text).group(0)
    log_command(message)
    send_menu_image(message.chat.id, command.replace("/", ""))


@bot.message_handler(commands=['hoy'])
def send_menu_today(message):
    log_command(message)

    suggest_subscription_msg = '*NOVEDAD*: Ahora puedes suscribirte y *recibir el menú diario automáticamente*. Para ello, utiliza el comando /suscripcion'
    bot.send_message(message.chat.id, suggest_subscription_msg,
                     parse_mode='markdown')

    week_day_str = '{today:%A},{today.day}'.format(today=date.today())
    send_menu_image(message.chat.id, unidecode(week_day_str))


@bot.message_handler(commands=['pdf'])
def send_pdf(message):
    log_command(message)
    try:
        doc = open(PDF_FILENAME, 'rb')
        bot.send_document(message.chat.id, doc)
        doc.close()
    except IOError as e:
        log.error('Exception while opening file: ' + PDF_FILENAME, e)


@bot.message_handler(commands=['suscripcion'])
def subscribe(message):
    log_command(message)

    if message.chat.id in subscriptions:
        msg = 'Ya estás suscrito. Recibirás el menú cada día a las *12:00 (hora española)*. Puedes cancelar la suscripcion usando /cancelarsuscripcion'
        bot.send_message(message.chat.id, msg, parse_mode='markdown')
        return

    subscriptions.append(message.chat.id)
    persist_subscriptions()

    msg = '¡Suscrito con éxito!. Recibirás el menú cada día a las *12:00 (hora española)*. Puedes cancelar la suscripcion usando /cancelarsuscripcion'
    bot.send_message(message.chat.id, msg, parse_mode='markdown')


@bot.message_handler(commands=['cancelarsuscripcion'])
def unsubscribe(message):
    log_command(message)

    if message.chat.id in subscriptions:
        subscriptions.remove(message.chat.id)
        persist_subscriptions()

    msg = '¡Suscripción cancelada!. Puedes volver a suscribirte en cualquier momento usando el comando /suscripcion'
    bot.send_message(message.chat.id, msg)


def send_menu_image(chat_id, day_of_week):
    try:
        target_files = [file for file in os.listdir(IMAGES_PATH)
                        if file.startswith(day_of_week)]
        if not target_files:
            msg = "No hay ningún menú disponible para el día indicado. Es posible que el comedor esté cerrado o que no haya datos aún. Consulta http://scu.ugr.es para más información."
            bot.send_message(chat_id, msg)
            log.info('No data available for requested day')
        else:
            for file in target_files:
                img = open(IMAGES_PATH + file, 'rb')
                bot.send_photo(chat_id, img)
                img.close()
                log.info(file + ' has been sent')
    except Exception as e:
        log.error('Exception trying to send menu images to chat id {}: {}'
                  .format(str(chat_id), str(e)))


def log_command(message):
    log.info('Command {} has been received. Chat data: {}'
             .format(message.text, str(message.chat)))


def load_data():
    """Call puppeteer every hour to generate menu images"""
    global data_timer
    data_timer = threading.Timer(3600, load_data)
    data_timer.start()

    try:
        if not os.path.exists(IMAGES_PATH):
            os.makedirs(IMAGES_PATH)

        if not os.path.exists(NEW_IMAGES_PATH):
            os.makedirs(NEW_IMAGES_PATH)

        for filename in os.listdir(NEW_IMAGES_PATH):
            os.remove(NEW_IMAGES_PATH + filename)

        subprocess.run(['node', 'renderer.js'], timeout=60)

        # Remove old images and move new images to images path
        for filename in os.listdir(IMAGES_PATH):
            os.remove(IMAGES_PATH + filename)
        for filename in os.listdir(NEW_IMAGES_PATH):
            os.rename(NEW_IMAGES_PATH + filename,
                      IMAGES_PATH + unidecode(filename))

        log.info('Menu images have been rendered successfully')
    except Exception as err:
        log.error('Renderer error: {0}'.format(str(err)))

    # Download menu pdf
    try:
        f = open(PDF_FILENAME, 'wb')
        f.write(urllib.request.urlopen('https://scu.ugr.es/pages/menu/comedor?theme=pdf')
                .read())
        f.close()
        log.info(PDF_FILENAME + ' downloaded successfully')
    except Exception as err:
        os.remove(PDF_FILENAME)
        log.error("Can't download pdf file: {0}".format(err.args))


def load_subscriptions():
    global subscriptions
    if os.path.exists('subscriptions.txt'):
        file = open('subscriptions.txt', 'r')
        for sub in file.readlines():
            subscriptions.append(int(sub.replace('\n', '')))


def persist_subscriptions():
    file = open('subscriptions.txt', 'w')
    for sub in subscriptions:
        file.write(str(sub) + '\n')
    file.close()


def process_subscriptions():
    week_day_str = unidecode(
        '{today:%A},{today.day}'.format(today=date.today()))

    target_files = [file for file in os.listdir(IMAGES_PATH)
                    if file.startswith(week_day_str)]
    for sub in subscriptions:
        if target_files:
            send_menu_image(sub, week_day_str)

    schedule_subscription_processing()


def schedule_subscription_processing():
    """Send menu every day at 12:00 (local date)"""
    global sub_timer

    now = datetime.now()
    next = now

    if now.hour < 12:
        next = now.replace(hour=12, minute=0)
    elif now.hour >= 12:
        next = now + timedelta(days=1)
        next = next.replace(hour=12, minute=0)

    if next.weekday() == 6:
        # Dining hall closed on sundays, so schedule to next monday
        next = next + timedelta(days=1)

    delta = next.timestamp() - now.timestamp()
    log.info('Subscriptions processing delta: ' + str(delta / 3600) + ' hours')
    sub_timer = threading.Timer(delta, process_subscriptions)
    sub_timer.start()


def main():
    log.basicConfig(level=log.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

    load_data()
    load_subscriptions()
    schedule_subscription_processing()

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            log.info('Starting bot polling...')
            bot.polling()
        except Exception as err:
            log.error("Bot polling error: {0}".format(err.args))
            bot.stop_polling()
            time.sleep(30)


def signal_handler(signal_number, frame):
    print('Received signal ' + str(signal_number)
          + '. Trying to end tasks and exit...')
    bot.stop_polling()
    data_timer.cancel()
    sub_timer.cancel()
    sys.exit(0)


if __name__ == "__main__":
    main()
