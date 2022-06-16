from io import BytesIO

import discord
from discord.ext import commands
from matplotlib import pyplot as plt # type: ignore
from rply import LexingError, ParsingError # type: ignore

from .utils.lexer import l # type: ignore
from .utils.parsers_ import parser # type: ignore

class Math(commands.Cog):
    """Math commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🔢" # create custom emojis later I guess.

    def save_plt(self, _plt, name: str) -> discord.File:
        _bytes = BytesIO()
        _plt.savefig(_bytes)
        _plt.close()
        img = discord.File(_bytes, name)
        _bytes.seek(0)
        return img      

    @commands.command(description="Graph a linear function!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def linear(self, ctx, slope: float, y_intercept: float):
        x = list(range(-10, 11))
        y = [(slope*x_val)+y_intercept for x_val in x]

        plt.plot(x, y, linestyle='-')
        plt.grid()

        img = self.save_plt(plt, "linear.png")

        await ctx.send(file=img)

    @commands.command(description="Graph a quadratic function!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quadratic(self, ctx, a:float, b:float, c:float):
        x = list(range(-10, 11))
        y = [a*x_val**2 + b*x_val + c for x_val in x]

        plt.plot(x, y, linestyle='-')
        plt.grid()

        img = self.save_plt(plt, "quadratic.png")
        
        await ctx.send(file=img)

    @commands.command(description="Graph a exponential function")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def exponential(self, ctx, a: float, b: float):
        x = list(range(-10, 11))
        y = [a*b**x_val for x_val in x]

        plt.plot(x, y, linestyle='-')
        plt.grid()

        img = self.save_plt(plt, "exponential.png")

        await ctx.send(file=img)

    @commands.command(description="Graph and expression!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def expr(self, ctx, *, expr: str):
        pass

    @commands.command(description="Calculate an expression!", aliases=["calculate", "calculator"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def calc(self, ctx, *, expr: str):
        try:
            results = parser.parse(l.lex(expr))._eval()
            return await ctx.send(results)
        except (LexingError, ParsingError):
            return await ctx.send("Invalid Equation!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Math(bot))