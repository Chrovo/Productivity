import discord
from discord.ext import commands, tasks
from typing import Optional

class ComputerScience(commands.Cog):
    """Computer Science/Programming/Coding commands."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "💻" # create custom emojis later I guess.

    @commands.command(aliases=["src"], description="This will return the source code of Productivity")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def source(self, ctx, command:Optional[str]=None):
        if not command:
            await ctx.send("https://github.com/Chrovo/Productivity/tree/master")
        else:
            pass # add stuff later
    
    @commands.command()
    async def test(self, ctx, m):
        pass

def setup(bot):
    bot.add_cog(ComputerScience(bot))