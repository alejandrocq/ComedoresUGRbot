from bs4 import BeautifulSoup
import telebot
import urllib
import os
import sys

bot = telebot.TeleBot("195056032:AAEZxD9yunZkbusxM512B6oddGuawxATWVk")
url = 'http://scu.ugr.es/'
try:
    page = BeautifulSoup(urllib.request.urlopen(url), "html.parser")
    data = page.find("table").find_all("td")
except urllib.error.HTTPError as e:
    error_message = "Error %s HTTP." % e.code
    sys.exit(error_message)

menu_list = [elem.get_text() for elem in data]

index = 0
lunes = []
martes = []
miercoles = []
jueves = []
viernes = []
sabado = []

while ("MARTES" not in menu_list[index]):
    lunes.append(menu_list[index])
    index += 1
while ("MIÉRCOLES" not in menu_list[index]):
    martes.append(menu_list[index])
    index += 1
while ("JUEVES" not in menu_list[index]):
    miercoles.append(menu_list[index])
    index += 1
while ("VIERNES" not in menu_list[index]):
    jueves.append(menu_list[index])
    index += 1
while ("SÁBADO" not in menu_list[index]):
    viernes.append(menu_list[index])
    index += 1
while (index < len(menu_list)):
    sabado.append(menu_list[index])
    index += 1

@bot.message_handler(commands=['start'])
def welcome_message(message):
    msg = '¡Ya estamos listos para empezar! Escribe /diadelasemana para obtener el menú correspondiente. También puedes obtener el menú semanal en pdf usando /pdf. Si necesitas ayuda, usa /help.'
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['help'])
def welcome_message(message):
    msg = 'Si deseas obtener el menú de un día concreto, usa /lunes, /martes... etc. Además, escribiendo /pdf puedes obtener el documento pdf con el menú semanal completo.'
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['lunes','martes','miercoles','jueves','viernes','sabado'])
def print_menu(message):
    if (message.text.startswith("/lunes")):
        for menu in lunes:
            bot.send_message(message.chat.id, menu)

    if (message.text.startswith("/martes")):
        for menu in martes:
            bot.send_message(message.chat.id, menu)

    if (message.text.startswith("/miercoles")):
        for menu in miercoles:
            bot.send_message(message.chat.id, menu)

    if (message.text.startswith("/jueves")):
        for menu in jueves:
            bot.send_message(message.chat.id, menu)

    if (message.text.startswith("/viernes")):
        for menu in viernes:
            bot.send_message(message.chat.id, menu)

    if (message.text.startswith("/sabado")):
        for menu in sabado:
            bot.send_message(message.chat.id, menu)

@bot.message_handler(commands=['pdf'])
def print_menu(message):
    try:
        url_pdf = 'http://scu.ugr.es/?theme=pdf'
        pdf_filename = 'menu_comedores.pdf'
        f = open(pdf_filename,'wb')
        f.write(urllib.request.urlopen(url_pdf).read())
        f.close()
        doc = open(pdf_filename, 'rb')
        bot.send_document(message.chat.id, doc)
        doc.close()
        os.remove(pdf_filename)
    except urllib.error.HTTPError as e:
        error_message = "Error %s. Prueba de nuevo en unos minutos." % e.code
        bot.send_message(message.chat.id, error_message)
        os.remove(pdf_filename)

bot.polling()
