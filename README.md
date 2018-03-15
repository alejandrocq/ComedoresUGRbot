# ComedoresUGRbot
<img src="ugrlogo.png" width="256px" align="right"/>

<img src="telegramlogo.png" width="16px"/> http://telegram.me/ComedoresUGRbot

Telegram bot to check the menu of Universidad de Granada dining hall. It works
thanks to [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI/) and [puppeteer](https://github.com/GoogleChrome/puppeteer/).

**Puppeteer is used to launch a headless Chrome browser, find menu tables and save them as png images.** This implementation can be maintained more easily, because scu.ugr.es DOM has been changing a lot and parse the data in the tables seems to be more problematic. I made a request to them in order to get a simple JSON API for developers and they answered that they would consider it, but for the moment it's necessary to parse scu.ugr.es DOM one way or another.

## Installation

First of all, **you need Python 3 correctly installed on your machine**. Then, run:

> pip install -r requirements.txt

**In some environments, you have to use pip3 instead of pip** in order to install the packages for Python 3.

Also, you need to **install all the necessary node dependencies to run the renderer**. To do that, run:

> npm install

In order to test the renderer, run the following command and be sure that all menu tables are being saved in `./images-new` folder:

> node renderer.js

Once you have installed all the dependencies, add your bot token in `BOT_TOKEN` environment variable. Optionally, you can configure a custom chromium browser path in `BROWSER_PATH` environment variable if you don't want to use the chromium browser bundled with puppeteer npm package.

When everything is properly configured, run the bot script:

> python3 ComedoresUGRbot.py

All should work okay. **Menu images are updated every hour**.

Code licensed under GPLv3. See LICENSE file for more information.
