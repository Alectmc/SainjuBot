# Author: Alec Creasy
# File Name: bot.py
# Description: Creates a discord bot to be used in Dr. Sainju's Discord Server(s).
import sys

from discord import Intents, Game, app_commands
import discord.ext.commands as commands
import dotenv
from typing import Final
import os
import logging

# Create the logs directory if it doesn't exist.
os.makedirs("logs", exist_ok=True)

# Configure logging.
logging.basicConfig(level=logging.INFO,
                    format='[{asctime}] - [{levelname}] {name}: {message}',
                    style="{",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler("logs/bot.log")])

# Silence noisy logs from discord.py
logging.getLogger("discord")

# Create the logger.
logger = logging.getLogger("bot")

# Load environment with token and store it in a constant.
dotenv.load_dotenv()
TOKEN: Final[str] = os.getenv("TOKEN")

# Set intents, as well as enable the members intent.
# We need these enabled to detect new users.
intents = Intents.default()
intents.members = True
intents.message_content = True

class SainjuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
        # Load cogs
        extensions = [
            "cogs.utility",
            "cogs.faq",
            "cogs.rolebot",
            "cogs.admin"
        ]
        for ext in extensions:
            await self.load_extension(ext)
            logger.info(f"Loaded extension: {ext}")

        # Sync application commands (slash commands)
        await self.tree.sync()
        logger.info("Commands synced!")

    # Log bot in and set activity to "playing /help"
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        activity = Game("/help")
        await self.change_presence(activity=activity)

# Create bot
bot = SainjuBot()

# Create error handling for when a user tries to access a command they do not have permission to use.
@bot.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permissions to use this command.", ephemeral=True)
        logger.warning(f"{interaction.user} tried to use '{interaction.command.name}' but they don't have permissions to use this command.")
    else:
        await interaction.response.send_message("An unexpected error occured...", ephemeral=True)
        logger.error(f"Unexpected error in command '{interaction.command.name}' with error: {error}", exc_info=True)
        raise error

# Run the bot using the token in .env.
bot.run(token=TOKEN)