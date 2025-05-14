# Author: Alec Creasy
# File Name: admin.py
# Description: Creates a few commands for the server Administrators.

import discord
from discord import app_commands
from discord.ext import commands

# Create a cog for the administrator commands that are separate from the rolebot and faq commands.
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Creates a command to clear all messages from the current channel.
    @app_commands.command(name="clear_chat", description="Clears all messages from the current channel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_chat(self, interaction: discord.Interaction):

        # Defers the response until after all messages are removed.
        await interaction.response.defer(ephemeral=True)

        # Purges the channel of all content
        await interaction.channel.purge()

        # Reports that the operation was successful.
        await interaction.followup.send(f"All messages in #{interaction.channel.mention} have been cleared.", ephemeral=True)

# Set up the cog to be used for the bot.
async def setup(bot):
    await bot.add_cog(Admin(bot))