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
import locale
from datetime import date, timedelta
from unidecode import unidecode

PDF_FILENAME = 'menu.pdf'

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

# Set yout bot token as an environment variable
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def welcome_message(message):
	msg = "¡Ya estamos listos para empezar! Escribe /lunes , /martes , ... o /hoy para obtener el menú correspondiente. También puedes obtener el menú semanal en pdf usando /pdf. Si necesitas ayuda, usa /help."
	bot.send_message(message.chat.id, msg)
	log_command(message)

@bot.message_handler(commands=['help'])
def help_message(message):
	msg = "Si deseas obtener el menú de un día concreto, usa /lunes, /martes... o /hoy . Además, escribiendo /pdf puedes obtener el documento pdf con el menú semanal completo."
	bot.send_message(message.chat.id, msg)
	log_command(message)

@bot.message_handler(commands=['lunes','martes','miercoles','jueves',
	'viernes','sabado'])
def print_menu(message):
	send_menu_image(message.chat.id, message.text.replace("/", ""))
	log_command(message)

@bot.message_handler(commands=['hoy'])
def print_menu_today(message):
	week_day_str = unidecode(date.today().strftime("%A"))
	send_menu_image(message.chat.id, week_day_str)
	log_command(message)

@bot.message_handler(commands=['pdf'])
def send_pdf(message):
	try:
		doc = open(PDF_FILENAME, 'rb')
		bot.send_document(message.chat.id, doc)
		doc.close()
		log_command(message)
	except IOError as e:
		logging.error('Exception while opening file: ' + PDF_FILENAME, e)

def send_menu_image(chat_id, day_of_week):
	try:
		target_files = [file for file in os.listdir('images/')
			if unidecode(file).startswith(day_of_week.upper())]
		for file in target_files:
			img = open('images/' + file, 'rb')
			bot.send_photo(chat_id, img)
			img.close()
	except IOError as e:
		logging.error('Exception trying to send menu images', e)

def log_command(message):
	logging.info('Received command ' + message.text)

DATA_TIMER = None

# Call CasperJS every hour to generate menu images
def data_timer():
	try:
		global DATA_TIMER
		DATA_TIMER = threading.Timer(3600, data_timer)
		DATA_TIMER.start()

		subprocess.check_call(['casperjs', 'renderer.js'])
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
