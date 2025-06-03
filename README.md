# SainjuBot

### Author: Alec Creasy

## Overview

This is a Discord server management bot created for use at Middle Tennessee State University in Dr. Arpan Sainju's lab server.
The bot utilizes the Sentence Transformer from Hugging Face meant for detecting semantic similarities to be used to detect questions asked that are similar to FAQs.
The bot also comes equipped with a Role Bot, allowing administrators to assign and manage roles in the server. The intuition is that each
role will only see what is relevant to them, such as courses, visitors, and those in the research lab. This keeps the server from being confusing
and making sure each user only has access to what they need from the server.
Finally, there are easy-to-use administrator tools to clear the history from text channels, so as new semesters arise, each course text channel will
be a clean slate.

## How To Run It

### Required Software and Packages

You will need Python3 and pip installed to run the bot. The required packages are included in the requirements.txt.
Once you have Python installed, you will need to install the packages. Navigate to the directory where the repository is stored on your machine, and run the following command:
```
pip install -r requirements.txt
```

This will install the required packages needed to run the bot.

### Creating the Discord application

You need to create a Discord app within the Discord developer portal, which you can access [here](https://discord.com/developers).
Once you have logged in, you need to create a new application. You may use whatever settings you'd like, but be sure to enable the Presence Intent and the Server Members Intent. Without these intents enabled, if your bot becomes verified, it will not have permission to receive new member updates, which is required for the welcome message.

Once you have created the bot, go to the "Bot" tab within its settings and find "Token". Click "Reset Token" and copy the token for use later. **DO NOT PUBLISH THIS TOKEN ONLINE. THIS IS ESSENTIALLY THE USERNAME/PASSWORD FOR YOUR BOT.**

Next, navigate to the "Installation" tab. Under the "Default Install Settings" find "Guild Install". Under "Scopes", select "applications.commands" and "bot". A new dropdown called "Permissions" should appear. Select the following permissions:
- Add Reactions
- Manage Roles
- Mention Everyone
- Read Message History
- Send Messages
- Use Slash Commands
- View Channels

After this, copy the link found in "Install Link," and this should prompt you to add the bot to a server. Select the server in which the bot will reside. The bot will be offline to start. This is normal, as we haven't started the Python script to run the bot yet!

### Discord Bot Token

Once you have created the Discord app and have invited the bot to your server, you will now need to provide the token to be used for login. The script uses dotenv to read in the TOKEN from a ".env" file so that the token is not exposed in the main bot.py file.

Open the directory where the repository is stored, and create a new file ".env". **DO NOT NAME IT ANY OTHER WAY.** The dotenv package looks specifically for a file titled ".env", so it is critical that you name the file correctly.

Once you have created the .env file, open it with a text editor (For example, Notepad (Windows) or TextEdit (macOS)).

Copy the following line and save it to your .env file, replacing <YOUR_TOKEN_HERE> with the token we got earlier from the Discord developer portal earlier (If you lost it, you can get another one by going back to the "Bot" tab in the application settings on the developer portal).
```
TOKEN=<YOUR_TOKEN_HERE>
```
### Running the Bot

Now that we have all of the steps above done, we can now run the bot. Open a terminal window and navigate to the directory of the repository. Once there, type the following command:
```
python bot.py
```
If you receive an error that the "python" command is not found, try using "python3" instead. If you still receive an error, you may need to reinstall Python or ensure that it is in your system's PATH.

And that's it! The bot should now be online in the server you added it to!
