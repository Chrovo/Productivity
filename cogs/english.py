import discord
from discord.ext import commands, tasks

from .utils.request import Requests

class English(commands.Cog):
    """English/Writing/Reading commands."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "📚" # create custom emojis later I guess.

    @commands.command(description="Search up a definition for a word", aliases=['defi'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def definition(self, ctx, word:str):
        pass # do later

def setup(bot):
    bot.add_cog(English(bot))