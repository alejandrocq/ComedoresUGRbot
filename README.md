# ComedoresUGRbot
Telegram bot to check the menu of Universidad de Granada dining hall. It works
thanks to [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI/).

**Bot is working again**. I have applied a new strategy using CasperJS to render menu tables and save them as png images. This implementation can be maintained more easily, because scu.ugr.es DOM has been changing a lot and
maintain a parser seems to be more problematic.

I made a request to them in order to get a simple JSON API for developers and they answered that they would consider it, but for the moment it's necessary to
parse scu.ugr.es DOM one way or another.

This bot is available at: http://telegram.me/ComedoresUGRbot

## Installation:

First of all, **you need Python 3 correctly installed on your machine.** Then, run:

> pip install -r requirements.txt

**In some distributions, you have to use pip3 instead of pip** in order to install the packages for Python 3.

Also, you need to install [PhantomJS](http://phantomjs.org/) and [CasperJS](http://casperjs.org/). See how to do that in your operating system looking at their documentation.

Once you have installed all the requirements, then add your bot token as 'BOT_TOKEN' environment variable and run:

> python3 ComedoresUGRbot.py

All should work okay. **Menu images are updated every hour**.

Code licensed under GPLv3. See LICENSE file for more information.
