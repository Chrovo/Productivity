import os
import json

import discord
import aiohttp
import asyncpg # type: ignore
from discord.ext import commands # type: ignore

from help import ProductivityHelp

# fmt: off
__all__ = (
    'Productivity',
)
# fmt: on


with open("config.json", "r") as f:
    config = json.load(f)


class Productivity(commands.Bot):
    __slots__ = (
        "db",
        "session",
    )

    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or("pr!"),
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True
            ),
            help_command=ProductivityHelp(),
        )

    async def setup_hook(self) -> None:
        self.db = await asyncpg.create_pool(
            database="productivity",
            password=config["POSTGRES_PASSWORD"],
            user="postgres",
        )
        self.session = aiohttp.ClientSession()

        for e in [f"cogs.{e[:-3]}" for e in os.listdir("./cogs") if e.endswith(".py")]:
            await super().load_extension(e)

    async def on_ready(self) -> None:
        print("Bot is ready for use.")

    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        embed = discord.Embed(colour=discord.Colour.red())
        if isinstance(exception, commands.CommandOnCooldown):
            await ctx.send(
                f"You are on cooldown! Please wait `{round(exception.retry_after)}` seconds!"
            )
        elif isinstance(exception, commands.MissingRequiredArgument):
            embed.title = "Missing Required Argument"
            embed.description = f"""
            You are missing the '{exception.param}' parameter!\n
            **Usage**: pr!{ctx.command.qualified_name} {ctx.command.signature}
            """
            await ctx.send(embed=embed)
        elif isinstance(exception, commands.BadArgument):
            embed.title = "Bad Argument"
            embed.description = "Please send a valid argument!"
            await ctx.send(embed=embed)
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.NotOwner):
            await ctx.send(
                "You are not the owner of this bot! This command is an owner only command!"
            )
        else:
            raise exception


bot = Productivity()


@bot.command(aliases=("r",))
@commands.is_owner()
async def reload(ctx: commands.Context, ext: str):
    bot.reload_extension(f"cogs.{ext}")
    await ctx.send(f"Cog {ext} has been reloaded")

bot.run(config["TOKEN"])
