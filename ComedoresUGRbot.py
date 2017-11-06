#!/usr/bin/python3
import telebot
import urllib
import time
import datetime

import os
import subprocess
import threading
import sys
import signal
import logging

url_pdf = 'http://scu.ugr.es/?theme=pdf'
pdf_filename = 'menu.pdf'

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

@bot.message_handler(commands=['lunes','martes','miercoles','jueves','viernes','sabado'])
def print_menu(message):
	chat_id = message.chat.id

	if (message.text.startswith("/lunes")):
		send_menu_image(chat_id, 'monday')
	if (message.text.startswith("/martes")):
		send_menu_image(chat_id, 'tuesday')
	if (message.text.startswith("/miercoles")):
		send_menu_image(chat_id, 'wednesday')
	if (message.text.startswith("/jueves")):
		send_menu_image(chat_id, 'thursday')
	if (message.text.startswith("/viernes")):
		send_menu_image(chat_id, 'friday')
	if (message.text.startswith("/sabado")):
		send_menu_image(chat_id, 'saturday')

	log_command(message)

@bot.message_handler(commands=['hoy'])
def print_menu_today(message):
	chat_id = message.chat.id
	week_day_str = datetime.date.today().strftime("%A").lower()
	send_menu_image(chat_id, week_day_str)
	log_command(message)

@bot.message_handler(commands=['pdf'])
def send_pdf(message):
	try:
		doc = open(pdf_filename, 'rb')
		bot.send_document(message.chat.id, doc)
		doc.close()
		log_command(message)
	except IOError as e:
		logging.error('Exception while opening file: ' + pdf_filename, e)

def send_menu_image(chat_id, day_of_week):
	try:
		img = open('images/' + day_of_week + '.png', 'rb')
		bot.send_photo(chat_id, img)
		img.close()
	except IOError as e:
		logging.error('Exception while opening file: ' + day_of_week + '.png')

def log_command(message):
	logging.info('Received command ' + message.text + '. Data: ' + str(message))

def download_pdf():
	try:
		f = open(pdf_filename,'wb')
		f.write(urllib.request.urlopen(url_pdf).read())
		f.close()
	except IOError as e:
		os.remove(pdf_filename)
		sys.exit(e)
	except urllib.error.HTTPError as e:
		os.remove(pdf_filename)
		error_message = "Error %s HTTP." % e.code
		sys.exit(error_message)

RENDERER_TIMER = None

# Call CasperJS every hour to generate menu images
def render_images():
	try:
		global RENDERER_TIMER
		RENDERER_TIMER = threading.Timer(3600, render_images)
		RENDERER_TIMER.start()
		subprocess.check_call(['casperjs', 'renderer.js'])
		logging.info('Menu images have been rendered successfully')
	except Exception as e:
		logging.error('Renderer error', e)

def main():
	logging.basicConfig(level=logging.INFO,
		format='%(asctime)s %(levelname)s %(message)s',
		filename='comedores_ugr.log')

	render_images()
	download_pdf()

	signal.signal(signal.SIGINT, signal_handler)

	while True:
		try:
			logging.info('Starting bot polling...')
			bot.polling(none_stop=True)
		except Exception as e:
			logging.error('Bot polling error', e)
			time.sleep(15)

def signal_handler(signal_number, frame):
	print('Received signal ' + str(signal_number)
		+ '. Trying to end tasks and exit...')
	bot.stop_polling()
	if (RENDERER_TIMER is not None):
		RENDERER_TIMER.cancel()

	sys.exit(0)

if __name__ == "__main__":
	main()
