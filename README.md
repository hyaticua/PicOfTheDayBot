# Picture of the Day Bot

#### Setting up the bot
1. Install Python
2. `pip install -r requirements.txt`
3. Open config.json
    - set image directory (relative or absolute, create directory if it doesn't exist!)
    - post time in 24hr HH:MM:SS format
    - configure API key, see section below
4. Once configured, run bot with `python potdbot.py`

#### Getting an API key
1. Navigate to [Discord Developer Portal](https://discord.com/developers/)
2. On the *Application* tab, click **New Application**
3. Pick a name for the Bot
4. Once you're on the Bot settings page, navigate to the section called *Bot* and click the button **Add Bot** and the follow up button **Yes**
5. After the page refreshes, you should see a section that says **Click to Reveal Token**, copy the token and paste it into the bot config.json in the appropriate spot. 

#### Adding the bot to a server
1. Navigate to [Discord Developer Portal](https://discord.com/developers/) if you're not already there and select your bot under the *My Applications* section
2. Navigate to the section *OAuth2* and on the table at the bottom, click the checkbox that says **bot**, this should make another table below that visible.
3. On the table below, select the permissions **Send Messages** and **Attach Files**
4. After the options are selected, copy the Oath2 URL that it generated.
5. Open a new browser tab and paste the URL into your browser address bar. This should bring up a page where you can select a Discord server for the bot to join if you have permissions to invite bots.
