#!/usr/bin/python3
import os
import subprocess
import threading
import sys
import signal
import logging
import telebot
import urllib
import time
import re
import locale
from datetime import date, timedelta
from unidecode import unidecode

IMAGES_PATH = 'images/'
PDF_FILENAME = 'menu.pdf'

DATA_TIMER = None

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

# Set yout bot token as an environment variable
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def welcome_message(message):
	msg = "¡Ya estamos listos para empezar! Escribe /lunes , /martes , ... o /hoy para obtener el menú correspondiente. También puedes obtener el menú semanal en pdf usando /pdf. Si necesitas ayuda, usa /help."
	log_command(message)
	bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['help'])
def help_message(message):
	msg = "Si deseas obtener el menú de un día concreto, usa /lunes, /martes... o /hoy . Además, escribiendo /pdf puedes obtener el documento pdf con el menú semanal completo."
	log_command(message)
	bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['lunes','martes','miercoles','jueves',
	'viernes','sabado'])
def send_menu(message):
	# Parse command correctly (avoid content after @)
	regex = re.compile('\/\w*')
	command = regex.search(message.text).group(0)

	log_command(message)
	send_menu_image(message, command.replace("/", ""))

@bot.message_handler(commands=['hoy'])
def send_menu_today(message):
	week_day_str = unidecode(date.today().strftime("%A"))
	log_command(message)
	send_menu_image(message, week_day_str)

@bot.message_handler(commands=['pdf'])
def send_pdf(message):
	log_command(message)
	try:
		doc = open(PDF_FILENAME, 'rb')
		bot.send_document(message.chat.id, doc)
		doc.close()
	except IOError as e:
		logging.error('Exception while opening file: ' + PDF_FILENAME, e)

def send_menu_image(message, day_of_week):
	try:
		target_files = [file for file in os.listdir(IMAGES_PATH)
			if file.startswith(day_of_week.upper())]
		for file in target_files:
			img = open(IMAGES_PATH + file, 'rb')
			bot.send_photo(message.chat.id, img)
			img.close()
			logging.info(file + ' has been sent')
	except IOError as e:
		logging.error('Exception trying to send menu images', e)

def log_command(message):
	logging.info('Received command ' + message.text)

# Call CasperJS every hour to generate menu images
def data_timer():
	try:
		global DATA_TIMER
		DATA_TIMER = threading.Timer(3600, data_timer)
		DATA_TIMER.start()

		for filename in os.listdir(IMAGES_PATH):
			os.remove(IMAGES_PATH + filename)

		subprocess.check_call(['casperjs', 'renderer.js'])

		for filename in os.listdir(IMAGES_PATH):
			os.rename(IMAGES_PATH + filename,
				IMAGES_PATH + unidecode(filename).replace(" ", ""))

		logging.info('Menu images have been rendered successfully')
		download_pdf()
	except Exception as e:
		logging.error('Renderer error', e)

def download_pdf():
	try:
		f = open(PDF_FILENAME,'wb')
		f.write(urllib.request.urlopen('http://scu.ugr.es/?theme=pdf').read())
		f.close()
		logging.info(PDF_FILENAME + ' downloaded successfully')
	except Exception as e:
		os.remove(PDF_FILENAME)
		logging.error("Can't download pdf file", e)

def main():
	logging.basicConfig(level=logging.INFO,
		format='%(asctime)s %(levelname)s %(message)s')

	data_timer()
	signal.signal(signal.SIGINT, signal_handler)

	while True:
		try:
			logging.info('Starting bot polling...')
			bot.polling()
		except Exception as err:
			logging.error("Bot polling error: {0}".format(err))
			time.sleep(30)

def signal_handler(signal_number, frame):
	print('Received signal ' + str(signal_number)
		+ '. Trying to end tasks and exit...')
	bot.stop_polling()
	DATA_TIMER.cancel()
	sys.exit(0)

if __name__ == "__main__":
	main()
