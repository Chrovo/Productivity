import discord
from discord.ext import commands

class WorldLanguage(commands.Cog): #might remove this cog
    """World Language commands."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🗣️" # create custom emojis later I guess.

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WorldLanguage(bot))
