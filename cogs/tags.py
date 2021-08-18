import discord
import asyncpg
from discord.ext import commands

class Tags(commands.Cog):
    """Productivity's tag system."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🏷️ "

def setup(bot:commands.Bot):
    bot.add_cog(Tags(bot))