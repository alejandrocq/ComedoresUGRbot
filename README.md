# ComedoresUGRbot
<img src="doc-images/ugrlogo.png" width="256px" align="right"/>

<img src="doc-images/telegramlogo.png" width="16px"/> http://telegram.me/ComedoresUGRbot

Telegram bot to check the menu of Universidad de Granada dining hall. It works
thanks to [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI/) and [puppeteer](https://github.com/GoogleChrome/puppeteer/).

**Puppeteer is used to launch a headless Chrome browser, find menu tables and save them as png images.** This implementation can be maintained more easily, because scu.ugr.es DOM has been changing a lot and parse the data in the tables seems to be more problematic. I made a request to them in order to get a simple JSON API for developers and they answered that they would consider it, but for the moment it's necessary to parse scu.ugr.es DOM one way or another.

## Installation

### Option 1: Docker (Recommended)

The easiest way to run the bot is using Docker. This handles all dependencies automatically:

1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your bot token and the UGR dining hall URL:
   ```bash
   BOT_TOKEN=your_bot_token_here
   COMEDORES_URL=https://scu.ugr.es/pages/menu/comedor
   ```

3. Create the data directory:
   ```bash
   mkdir -p data
   ```

4. Start the bot:
   ```bash
   docker-compose up -d
   ```

**Useful commands:**
- View logs: `docker-compose logs -f`
- Stop bot: `docker-compose down`
- Restart bot: `docker-compose restart`
- Rebuild after changes: `docker-compose up -d --build`

### Option 2: Manual Installation

First of all, **you need Python 3 correctly installed on your machine**.

1. **Create and activate a virtual environment:**

   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate it (Linux/macOS)
   source venv/bin/activate
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

4. **Test the renderer** (optional):

   ```bash
   node renderer.js
   ```

   Verify that menu tables are being saved in `./images-new` folder.

5. **Configure environment variables:**

   Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

   Edit it with your configuration:
   ```bash
   BOT_TOKEN=your_bot_token_here
   COMEDORES_URL=https://scu.ugr.es/
   ```

6. **Run the bot:**

   ```bash
   python3 bot.py
   ```

All should work okay. **Menu images are updated every hour**.

## License

Code licensed under GPLv3. See LICENSE file for more information.
