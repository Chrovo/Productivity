import discord
import os
import json
from discord.ext import commands, tasks
from help import MyMenu, ProductivityHelp

with open("config.json", "r") as f:
    config = json.load(f)

class Productivity(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or('pr!'), 
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
            help_command=ProductivityHelp()
            ) # Add more stuff later
        self.db = None # Update later lol
    
    async def on_ready(self) -> None:
        print("Bot is ready for use.")
    
    async def on_command_error(self, context, exception):
        embed = discord.Embed(colour = discord.Colour.red())
        if isinstance(exception, commands.CommandOnCooldown):
            await context.send(f"You are on cooldown! Please wait `{round(exception.retry_after)}` seconds!")
        elif isinstance(exception, commands.MissingRequiredArgument):
            embed.title = "Missing Required Argument"
            embed.description = f"""
            You are missing the '{exception.param}' parameter!\n
            **Usage**: pr!{context.command.qualified_name} {context.command.signature}
            """
            await context.send(embed=embed) # Add more stuff later
        elif isinstance(exception, commands.CommandNotFound):
            pass
        else:
            raise exception

bot = Productivity()

if __name__ == '__main__':
  for e in ["cogs."+e[:-3] for e in os.listdir("./cogs") if e.endswith(".py")]:
    bot.load_extension(e)

bot.run(config["TOKEN"])