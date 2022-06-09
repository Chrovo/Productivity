import discord
from discord.ext import commands

from cogs.utils.pagination import Pagination # type: ignore


class ProductivityHelp(commands.HelpCommand):
  def __init__(self) -> None:
    super().__init__(
      command_attrs={
        'description':'A command that sends help and information about the other commands!', 
        'cooldown':commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
        }
      )

  async def send_bot_help(self, mapping):
    ctx = self.context
    self.embeds = [self._create_embed_list(cog) for cog in ctx.bot.cogs.values()]
    owner = (await ctx.bot.application_info()).owner

    embed = discord.Embed(title="Help Command", description="Do pr!help [command or category] for help on a specific category or command!")
    embed.set_author(name="Chrovo#9488", icon_url=owner.default_avatar.url)
    embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.default_avatar.url)
    embed.set_thumbnail(url=ctx.me.default_avatar.url)
    embed.add_field(name="Categories", value='\n'.join(["❱ "+cog.emoji+cog.qualified_name for cog in ctx.bot.cogs.values()]))

    self.embeds.insert(0, embed)

    m = Pagination(self.context, messages=self.embeds)
    await m.start(self.context)

  def _create_embed_list(self, cog:commands.Cog) -> discord.Embed:
    embed = discord.Embed(title=cog.qualified_name, description=cog.description)
  
    embed.add_field(
        name=f"{cog.qualified_name} Commands Help!", 
        value="```yaml\n"+
        '\n'.join(['pr!'+command.name+f" {command.signature}" for command in cog.walk_commands()])
        +"```"
      )

    embed.set_author(name="Chrovo#9488", icon_url="https://cdn.discordapp.com/avatars/615975131881144333/7d3bc639d2da754cc83b00412500e0cd.webp?size=1024") #shush
    embed.set_thumbnail(url=self.context.me.default_avatar.url)
    embed.set_footer(text=f"Requested by: {self.context.author}", icon_url=self.context.author.default_avatar.url)
    return embed
  
  async def send_cog_help(self, cog):
    owner = (await self.context.bot.application_info()).owner

    embed = discord.Embed(title=cog.qualified_name, description=cog.description)

    embed.add_field(
        name=f"{cog.qualified_name} Commands Help!", 
        value="```yaml\n"
        +'\n'.join(['- '+command.name for command in cog.walk_commands()])
        +"```"
      )
  
    embed.set_author(name="Chrovo#9488", icon_url=owner.default_avatar.url)
    embed.set_thumbnail(url=self.context.me.default_avatar.url)
    embed.set_footer(text=f"Requested by: {self.context.author}", icon_url=self.context.author.default_avatar.url)

    return await self.context.send(embed=embed)

  async def send_command_help(self, command):
    embed = discord.Embed(title=f"Command '{command.name}' Help!", description=f"__**Command Description**__\n{command.description}")
    embed.add_field(name="Command Usage", value=f"```{self.get_command_signature(command)}```")

    if command.aliases:
      embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
    
    embed.set_footer(text="[] means that the part is optional, and <> means that it is required!", icon_url=self.context.me.default_avatar.url)

    return await self.context.send(embed=embed)

  async def send_group_help(self, group):
    embed = discord.Embed(title=group.qualified_name, description=f"Help for the group of '{group.qualified_name}' commands!")

    for cmd in group.commands:
      embed.add_field(name=self.get_command_signature(cmd), value=cmd.description, inline=False)
    
    await self.context.send(embed=embed)
