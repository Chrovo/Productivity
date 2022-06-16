from discord.ext import commands

class History(commands.Cog):
    """History commands."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🗺️" # create custom emojis later I guess.

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(History(bot))