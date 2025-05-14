# Author: Alec Creasy
# File Name: rolebot.py
# Description: Creates a Cog for the assignment of roles in the server.

import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import secrets
from configparser import ConfigParser

# Creates a cog for the Role Bot portion of SainjuBot.
# Creates the cog for the bot, a ConfigParser to read the config.ini file
# which then reads in the tokens file, the channel name the rolebot portion
# will redeem tokens in, and the number of bytes for the tokens to be.
# The tokens are then loaded in and saved to the instance's "tokens" variable.
class Rolebot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigParser()
        self.config.read("./config.ini")
        self.TOKENS_FILE = self.config.get("Rolebot", "TOKENS_FILE", fallback="./data/tokens.json")
        self.ROLE_CHANNEL_NAME = self.config.get("Rolebot", "ROLE_CHANNEL_NAME", fallback="rolebot")
        self.NUM_BYTES = int(self.config.get("Rolebot", "NUM_BYTES", fallback=16))
        self.tokens = self.load_tokens()

    # Helper function to load the tokens from the tokens JSON file.
    # If the file does not exist, create one in the directory specified in config.ini.
    def load_tokens(self):
        if not os.path.exists(self.TOKENS_FILE):
            os.makedirs(os.path.dirname(self.TOKENS_FILE), exist_ok=True)
            with open(self.TOKENS_FILE, "w") as file:
                json.dump({}, file)
        with open(self.TOKENS_FILE, "r") as file:
            return json.load(file)

    # Helper function to save the tokens to memory. Dumps the current tokens to the tokens JSON file.
    def save_tokens(self):
        with open(self.TOKENS_FILE, "w") as file:
            json.dump(self.tokens, file)

    # Creates a list of unique hexadecimal tokens for the number specified. Used when generating tokens.
    def generate_unique_tokens(self, count):
        return [secrets.token_hex(self.NUM_BYTES) for _ in range(count)]

    # Helper function that will return the roles of the server aside from any managed roles (typically reserved
    # for bots) and the @everyone role.
    @staticmethod
    def get_roles(server_roles):
        roles = [role for role in server_roles if not role.managed and role.name != "@everyone"]

        if not roles:
            return None

        return roles

    # This command will allow any administrator to generate the specified number of unique tokens to be used
    # to claim a role in the server.
    @app_commands.command(name="generate_tokens", description="Generate tokens to be redeemed for roles. (ADMINISTATOR ONLY)")
    @app_commands.describe(number="The token to be redeemed form a role.")
    @app_commands.checks.has_permissions(administrator=True)
    async def generate_tokens(self, interaction: discord.Interaction, number: int):
        # Ensure the user has entered a valid number of tokens to generate (greater than 0).
        if number <= 0:
            embed = discord.Embed(title="Role Bot", description="Invalid number of tokens to generate",
                                  color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # Get the list of roles.
        roles = self.get_roles(interaction.guild.roles)

        # Create a class to create the buttons to be used when choosing which role to generate tokens for.
        class RoleButton(discord.ui.Button):
            # Constructor calls the discord.ui.Button constructor and sets the button style to the primary
            # style, and assigns the instance's role variable to the role passed to the constructor.
            def __init__(self, role, label):
                super().__init__(label=label, style=discord.ButtonStyle.primary)
                self.role = role

            # Callback method will trigger when the administrator clicks on a role button. In this case,
            # a list of tokens are generated using the helper function generate_unique_tokens and the tokens
            # in the instance of the cog are either added to the current list of tokens for that role or, if none
            # exist yet, are created and added to the dictionary. The tokens are then saved to the tokens JSON file
            # and a message with the tokens is sent to the administrator that used the command.
            async def callback(self, button_interaction: discord.Interaction):
                tokens = self.view.cog.generate_unique_tokens(number)
                self.view.cog.tokens.setdefault(self.role.name, []).extend(tokens)
                self.view.cog.save_tokens()
                embed_button = discord.Embed(title="Role Bot", description=f"Tokens for {self.role.name}:\n" + "\n".join(tokens), color=discord.Color.green())
                await button_interaction.response.send_message(embed=embed_button, ephemeral=True)
                self.view.stop()

        # Creates a view for the buttons to appear.
        class RoleView(discord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=None)
                self.cog = cog
                for role in roles:
                    self.add_item(RoleButton(role, role.name))

        # Send a message asking for which role to generate tokens for, and list all available roles using the RoleView
        # abd RoleButtons.
        embed = discord.Embed(title="Role Bot", description="Select the role to generate tokens for:", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, view=RoleView(self), ephemeral=True)

    # This command allows a user to redeem a token.
    @app_commands.command(name="redeem_token", description="Redeems a token for a role.")
    @app_commands.describe(token="The token to redeem")
    async def redeem_token(self, interaction: discord.Interaction, token: str):
        # If the user is not currently in the role bot channel, let them know they must be in the correct channel and return.
        if interaction.channel.name != self.ROLE_CHANNEL_NAME:
            channel = discord.utils.get(interaction.guild.text_channels, name=self.ROLE_CHANNEL_NAME)
            if channel:
                embed = discord.Embed(title="Role Bot",
                                      description=f"Please use the {channel.mention} channel to redeem the token for a role!",
                                      color=discord.Color.red())
            else:
                embed = discord.Embed(title="Role Bot",
                                      description=f"#{self.ROLE_CHANNEL_NAME} not found! Please ensure you have a #{self.ROLE_CHANNEL_NAME} text channel setup!",
                                      color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get the role associated with the redeemed token. If the user already has the role, report this to them
        # and return. Otherwise, add the role to them, notify them, and return.
        for role_name, token_list in self.tokens.items():
            if token in token_list:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    if role in interaction.user.roles:
                        embed = discord.Embed(title="Role Bot", description=f"You already have the **{role_name}** role! The token has not been redeemed.", color=discord.Color.red())
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return

                    await interaction.user.add_roles(role)
                    self.tokens[role_name].remove(token)
                    self.save_tokens()
                    embed = discord.Embed(title= "Role Bot", description=f"Token redeemed! I've assigned you to the **{role_name}** role!", color=discord.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

        # If the token is invalid, report this to the user and do not add any roles.
        embed = discord.Embed(title="Role Bot", description=f"I'm sorry, but that token is invalid. Please ensure you have entered it correctly. If the issue persists, please see a server administrator.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # This command clears all token from the tokens JSON file and the tokens dictionary in the instance.
    @app_commands.command(name="clear_tokens", description="Clears all tokens from the database.")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_tokens(self, interaction: discord.Interaction):
        # Create the buttons to confirm if the administrator wants to remove all tokens.
        class ConfirmButton(discord.ui.Button):
            def __init__(self, label, style, confirmed):
                super().__init__(label=label, style=style)
                self.confirmed = confirmed

            # The callback method will remove all tokens if the user confirmed the operation,
            # otherwise do not clear the tokens.
            async def callback(self, button_interaction: discord.Interaction):
                if self.confirmed:
                    self.view.cog.tokens.clear()
                    self.view.cog.save_tokens()
                    embed = discord.Embed(title="Role Bot", description=f"All tokens have been removed!", color=discord.Color.green())
                else:
                    embed = discord.Embed(title="Role Bot", description=f"Tokens have not been cleared.", color=discord.Color.red())

                await button_interaction.response.send_message(embed=embed, ephemeral=True)
                self.view.stop()

        # Creates a view for the buttons.
        class ConfirmView(discord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=None)
                self.cog = cog
                self.add_item(ConfirmButton("Yes", discord.ButtonStyle.danger, True))
                self.add_item(ConfirmButton("No", discord.ButtonStyle.secondary, False))

        # Prompt the user to confirm the operation.
        embed = discord.Embed(title="Role Bot", description="This will remove all role tokens. This cannot be undone. Are you sure you wish to continue?", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=ConfirmView(self), ephemeral=True)

    # This command removes a specified role from all users in the server.
    @app_commands.command(name="remove_role", description="Removes a role from all users in the server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_role(self, interaction: discord.Interaction):
        # Get the roles
        roles = self.get_roles(interaction.guild.roles)

        # Create buttons to remove the roles.
        class RemoveRoleButton(discord.ui.Button):
            def __init__(self, role):
                super().__init__(label=role.name, style=discord.ButtonStyle.danger)
                self.role = role

            # The callback method will iterate through all the server members and remove the role if they
            # have the role specified.
            async def callback(self, button_interaction: discord.Interaction):
                members = [member for member in button_interaction.guild.members if self.role in member.roles]
                for member in members:
                    await member.remove_roles(self.role)

                # Report that the role has been removed from all users.
                embed = discord.Embed(title="Role Bot", description=f"{self.role.name} removed from all users!", color=discord.Color.green())
                await button_interaction.response.send_message(embed=embed, ephemeral=True)
                self.view.stop()

        # Create a view for the buttons.
        class RemoveRoleView(discord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=None)
                self.cog = cog
                for role in roles:
                    self.add_item(RemoveRoleButton(role))

        # Prompt the administrator for the role to remove from all users.
        embed = discord.Embed(title="Role Bot", description="Choose the role to remove from all users.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, view=RemoveRoleView(self), ephemeral=True)

# Set up the cog to be used for the bot.
async def setup(bot):
    await bot.add_cog(Rolebot(bot))