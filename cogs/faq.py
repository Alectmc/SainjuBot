# Author: Alec Creasy
# File Name: bot.py
# Description: Creates the FAQ command to display the frequently asked questions, as well as detect
# when a question is similar to a previously asked question using Cosine Similarity.

import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from sentence_transformers import SentenceTransformer, util
from configparser import ConfigParser

# Creates a cog for the FAQ portion of SainjuBot.
# Creates the cog for the bot, a ConfigParser to read the config.ini file
# which then reads in the questions and answers from the faq file and creates vectorized embeddings
# to be used to detecting similar questions asked.
class Faq(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigParser()
        self.config.read("./config.ini")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.FAQ_FILE = self.config.get("FAQ", "FAQ_FILE", fallback="./data/faq.json")
        self.faqs = self.load_faq()
        self.embeddings = self.embed_faqs()

    # Helper function to load all FAQ's from the JSON file. If it does not exist, it will be created.
    def load_faq(self):
        if not os.path.exists(self.FAQ_FILE):
            os.makedirs(os.path.dirname(self.FAQ_FILE), exist_ok=True)
            with open(self.FAQ_FILE, "w") as file:
                json.dump([], file)
        with open(self.FAQ_FILE) as file:
            return json.load(file)

    # Helper function to save all FAQ's to the JSON file.
    def save_faq(self):
        with open(self.FAQ_FILE, 'w') as file:
            json.dump(self.faqs, file, indent=4)

    # Helper function to create vectorized embeddings for all questions.
    def embed_faqs(self):
        questions = [faq["question"] for faq in self.faqs]
        return self.model.encode(questions, convert_to_tensor=True) if questions else []

    # This command will allow an administrator to add a FAQ to the list of FAQs.
    @app_commands.command(name="addfaq", description="Add a new FAQ question/answer pair. (ADMINISTRATOR ONLY)")
    @app_commands.describe(question="The question you wish to answer.", answer="The answer to the question.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_faq(self, interaction: discord.Interaction, question: str, answer: str):
        # Adds the FAQ to the list of FAQs and saves it to the JSON file as well as creates an embedding for the
        # question.
        self.faqs.append({"question": question, "answer": answer})
        self.save_faq()
        self.embeddings = self.embed_faqs()

        # Reports success to the command administrator.
        embed = discord.Embed(title="FAQ Entry Added!", description=f"FAQ Entry Added!\n\nQuestion: {question}\n\nAnswer: {answer}", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # This command will list all current FAQs.
    @app_commands.command(name="faq", description="Show the list of FAQ's")
    async def show_faq(self, interaction: discord.Interaction):
        # If there are no FAQs, report this to the user and return.
        if not self.faqs:
            embed = discord.Embed(title="Frequently Asked Questions", description="No FAQ entries found.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Display all the FAQs to the user in an embedded message.
        embed = discord.Embed(title="Frequently Asked Questions", color=discord.Color.green())
        for faq in self.faqs:
            embed.add_field(name=faq["question"], value=faq["answer"], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # This function sets up a listener for messages. It will be used to detect similar questions to the FAQ if one is
    # asked.
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # If the message author is the bot itself, return.
        if message.author == self.bot.user:
            return

        # If there are no embeddings (that is, there are no FAQs), return.
        if self.embeddings is None or len(self.embeddings) == 0:
            return

        # Get the message itself
        question = message.content

        # Create a vectorized embedding of the message and get the cosine similarity of each FAQ and current
        # message. After this, get the highest cosine similarity score.
        query_embedding = self.model.encode(question, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.embeddings)[0]
        best_index = scores.argmax().item()
        best_score = scores[best_index].item()

        # If the best cosine similarity score is greater than 75%, report to the user that this question
        # could be related to a FAQ.
        if best_score > 0.75:
            match = self.faqs[best_index]
            await message.reply(
                f"That sounds similar to an FAQ:\n**Q:** {match['question']}\n**A:** {match['answer']}"
            )

# Set up the cog to be used for the bot.
async def setup(bot):
    await bot.add_cog(Faq(bot))