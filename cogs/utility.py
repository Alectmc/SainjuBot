# Author: Alec Creasy
# File Name: utility.py
# Description: Creates a Cog for the utility commands: /help and /ping.

import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # # Adds the /ping command. The ping command simply responds to the user with the ping to the server.
    @app_commands.command(name="ping", description="Replies with latency to server")
    async def ping(self, interaction):
        embed = discord.Embed(title="Pong!", description=f"{round(self.bot.latency * 1000)}ms", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Adds the /help command. Responds to the user with a list of commands.
    @app_commands.command(name="help", description="Displays the list of commands")
    async def help(self, interaction):
        help_message = ("Available Commands:\n\n"
                        "/help: Displays a list of commands.\n"
                        "/ping: Replies with latency to server.\n"
                        "/faq: Displays the FAQ.\n"
                        "/redeem_token: Redeems a token for a role.")

        # If the user is an administrator, display additional commands they can use.
        is_admin = interaction.user.guild_permissions.administrator
        if is_admin:
            help_message += (f"\n\nAdministrator Commands:\n\n"
                             "/generate_tokens: Generates a given number of tokens to be used to assign roles.\n"
                             "/clear_tokens: Clears tokens from the database.\n"
                             "/remove_roles: Remove the given role from all users.\n"
                             "/clear_chat: Removes all messages from the current channel.")

        embed = discord.Embed(title="Help", description=help_message, colour=discord.Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Set up the cog to be used for the bot.
async def setup(bot):
    await bot.add_cog(Utility(bot))