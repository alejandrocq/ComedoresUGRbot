# This code is written on Python 3, so make sure you are running that version.
# The menu needs to be updated every week, so it's neccesary to restart it
# manually or use cron tasks on Linux, for example.

# Import all the neccesary stuff.

from bs4 import BeautifulSoup
import telebot
import urllib
import os
import datetime
import sys

# Initialize the bot with its token. Remember to replace bot_token_here with
# your bot token. You need to talk to @BotFather to get one.

bot = telebot.TeleBot("BOT_TOKEN_HERE")

# URLs and filename that we need to work.
url = 'http://scu.ugr.es/'
url_pdf = 'http://scu.ugr.es/?theme=pdf'
pdf_filename = 'menu_comedores.pdf'

# Download the pdf and save it to a file.
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

# Download the web page and save the table we need. Then we create a list of strings.
try:
	page = BeautifulSoup(urllib.request.urlopen(url), "html.parser")
	data = page.find("table").find_all("td")
except urllib.error.HTTPError as e:
	error_message = "Error %s HTTP." % e.code
	sys.exit(error_message)

menu_list = [elem.get_text() for elem in data]

# Create several lists for every day and parse the data for each one.

index = 0
monday = []
tuesday = []
wednesday = []
thursday = []
friday = []
saturday = []

while ("MARTES" not in menu_list[index]):
	monday.append(menu_list[index])
	index += 1
while ("MIÉRCOLES" not in menu_list[index]):
	tuesday.append(menu_list[index])
	index += 1
while ("JUEVES" not in menu_list[index]):
	wednesday.append(menu_list[index])
	index += 1
while ("VIERNES" not in menu_list[index]):
	thursday.append(menu_list[index])
	index += 1
while ("SÁBADO" not in menu_list[index]):
	friday.append(menu_list[index])
	index += 1
while (index < len(menu_list)):
	saturday.append(menu_list[index])
	index += 1

def print_monday(chat_id):
	for menu in monday:
		bot.send_message(chat_id, menu)
def print_tuesday(chat_id):
	for menu in tuesday:
		bot.send_message(chat_id, menu)
def print_wednesday(chat_id):
	for menu in wednesday:
		bot.send_message(chat_id, menu)
def print_thursday(chat_id):
	for menu in thursday:
		bot.send_message(chat_id, menu)
def print_friday(chat_id):
	for menu in friday:
		bot.send_message(chat_id, menu)
def print_saturday(chat_id):
	for menu in saturday:
		bot.send_message(chat_id, menu)


# Handler for command start. It returns a welcome message to the chat.

@bot.message_handler(commands=['start'])
def welcome_message(message):
	msg = '¡Ya estamos listos para empezar! Escribe /diadelasemana o /hoy para obtener el menú correspondiente. También puedes obtener el menú semanal en pdf usando /pdf. Si necesitas ayuda, usa /help.'
	bot.send_message(message.chat.id, msg)

# Handler for help command. It returns some help to the user.

@bot.message_handler(commands=['help'])
def help_message(message):
	msg = 'Si deseas obtener el menú de un día concreto, usa /lunes, /martes... o /hoy . Además, escribiendo /pdf puedes obtener el documento pdf con el menú semanal completo.'
	bot.send_message(message.chat.id, msg)

# Handler for every day commands. It prints the menu of the day the user asked for.

@bot.message_handler(commands=['lunes','martes','miercoles','jueves','viernes','sabado'])
def print_menu(message):
	chat_id = message.chat.id
	
	if (message.text.startswith("/lunes")):
		print_monday(chat_id)
	if (message.text.startswith("/martes")):
		print_tuesday(chat_id)
	if (message.text.startswith("/miercoles")):
		print_wednesday(chat_id)
	if (message.text.startswith("/jueves")):
		print_thursday(chat_id)
	if (message.text.startswith("/viernes")):
		print_friday(chat_id)
	if (message.text.startswith("/sabado")):
		print_saturday(chat_id)

# Handler for today command

@bot.message_handler(commands=['hoy'])
def print_menu_today(message):
	chat_id = message.chat.id
	week_day = datetime.date.today().weekday() # 0 is monday and 6 is sunday

	if (week_day == 0):
		print_monday(chat_id)
	if (week_day == 1):
		print_tuesday(chat_id)
	if (week_day == 2):
		print_wednesday(chat_id)
	if (week_day == 3):
		print_thursday(chat_id)
	if (week_day == 4):
		print_friday(chat_id)
	if (week_day == 5):
		print_saturday(chat_id)

# Handler for pdf command. It downloads the document with the full menu and
# returns it to the user chat.

@bot.message_handler(commands=['pdf'])
def send_pdf(message):
	try:
		doc = open(pdf_filename, 'rb')
		bot.send_document(message.chat.id, doc)
		doc.close()
	except IOError as e:
		sys.exit(e)
		os.remove(pdf_filename)

# This function keeps the connection to the Telegram Bot API alive and does all
# the neccesary operations to send the data. none_stop=True prevents the script
# from crashing if API errors occur.

bot.polling(none_stop=True)
