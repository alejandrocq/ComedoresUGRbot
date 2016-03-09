# ComedoresUGRbot
Telegram bot to check the menu of Universidad de Granada dining hall. It works
thanks to <a href="https://github.com/eternnoir/pyTelegramBotAPI/">pyTelegramBotAPI</a>
and <a href="http://www.crummy.com/software/BeautifulSoup/">BeautifulSoup</a>.

This bot is available at: http://telegram.me/ComedoresUGRbot

## Installation:

First of all, **you need Python 3 correctly installed on your machine.** Then, run:

> pip install -r requirements.txt

**In some distributions, you have to use pip3 instead of pip** in order to install the packages for Python 3.

**pyTelegramBotAPI is not included in requirements.txt**, because it has been uploaded to this repository. If you want to install it in your system anyway, run:

> pip install pyTelegramBotAPI

Once you have installed all the requirements with pip, then add your bot token to the file ComedoresUGRbot.py and run:

> python3 ComedoresUGRbot.py

All should work okay. **This bot has to be restarted manually every week**, once
the menu is updated on http://scu.ugr.es.

Code licensed under GPLv3. See LICENSE file for more information.
