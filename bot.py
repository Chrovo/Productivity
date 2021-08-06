import discord
import os
import json
from discord.ext import commands, tasks

with open("config.json", "r") as f:
    config = json.load(f)

class Productivity(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or('pr!'), 
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
            ) # Add more stuff later
        self.db = None # Update later lol
    
    async def on_ready(self) -> None:
        print("Bot is ready for use.")

bot = Productivity()

bot.run(config["TOKEN"])