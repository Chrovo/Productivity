import discord
from discord.ext import commands, tasks

class History(commands.Cog):
    """History commands."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🗺️" # create custom emojis later I guess.

def setup(bot):
    bot.add_cog(History(bot))