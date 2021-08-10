import discord
from discord.ext import commands, tasks, menus

class MyMenu(menus.Menu):

    def __init__(self, ctx:commands.Context) -> None:
      super().__init__()
      self.ctx = ctx
      self.embeds = [self._create_embed_list(cog) for cog in self.ctx.bot.cogs.values()]
      self.index = 0

    def _create_embed_list(self, cog:commands.Cog) -> discord.Embed:
      embed = discord.Embed(title=cog.qualified_name, description=cog.description)
      embed.add_field(name=f"{cog.qualified_name} Commands Help!", value="```yaml\n"+'\n'.join(['pr!'+command.name+f" {command.signature}" for command in cog.walk_commands()])+"```")
      embed.set_author(name="Chrovo#9488", icon_url="https://cdn.discordapp.com/avatars/615975131881144333/7d3bc639d2da754cc83b00412500e0cd.webp?size=1024") #shush
      embed.set_thumbnail(url=self.ctx.me.avatar_url)
      embed.set_footer(text=f"Requested by: {self.ctx.author}", icon_url=self.ctx.author.avatar_url)
      return embed

    async def send_initial_message(self, ctx, channel):
      embed = discord.Embed(title="Help Command", description="Do pr!help [command or category] for help on a specific category or command!")
      embed.set_author(name="Chrovo#9488", icon_url="https://cdn.discordapp.com/avatars/615975131881144333/7d3bc639d2da754cc83b00412500e0cd.webp?size=1024") #dont talk about this
      embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
      embed.set_thumbnail(url=ctx.me.avatar_url)
      embed.add_field(name="Categories", value='\n'.join(["❱ "+cog.emoji+cog.qualified_name for cog in ctx.bot.cogs.values()]))
      self.embeds.insert(0, embed)
      return await channel.send(embed=embed)
    
    @menus.button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def on_back_press(self, payload):
        embed = self.embeds[0]
        self.index = 0
        await self.message.edit(embed=embed)

    @menus.button('\N{BLACK LEFT-POINTING TRIANGLE}')
    async def on_left_press(self, payload):
        if self.index-1 >= 0:
          self.index -= 1
        embed = self.embeds[self.index]
        await self.message.edit(embed=embed)

    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}')
    async def on_right_press(self, payload):
        if self.index+1 < len(self.embeds):
          self.index+=1
        embed = self.embeds[self.index]
        await self.message.edit(embed=embed)
    
    @menus.button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}')
    async def on_fast_forward_press(self, payload):
        embed = self.embeds[-1]
        self.index = len(self.embeds)
        await self.message.edit(embed=embed)

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        self.stop()
        await self.message.delete()

class ProductivityHelp(commands.HelpCommand):
  def __init__(self) -> None:
    super().__init__(
      command_attrs={
        'description':'A command that sends help and information about the other commands!', 
        'cooldown':commands.Cooldown(1, 5, commands.BucketType.user),
      }
    )

  async def send_bot_help(self, mapping):
    m = MyMenu(self.context)
    await m.start(self.context)
  
  async def send_cog_help(self, cog):
    embed = discord.Embed(title=cog.qualified_name, description=cog.description)
    embed.add_field(name=f"{cog.qualified_name} Commands Help!", value="```yaml\n"+'\n'.join(['- '+command.name for command in cog.walk_commands()])+"```")
    embed.set_author(name="Chrovo#9488", icon_url="https://cdn.discordapp.com/avatars/615975131881144333/7d3bc639d2da754cc83b00412500e0cd.webp?size=1024")
    embed.set_thumbnail(url=self.context.me.avatar_url)
    embed.set_footer(text=f"Requested by: {self.context.author}", icon_url=self.context.author.avatar_url)
    return await self.context.send(embed=embed)

  async def send_command_help(self, command):
    embed = discord.Embed(title=f"Command '{command.name}' Help!", description=f"__**Command Description**__\n{command.description}")
    embed.add_field(name="Command Usage", value=f"```{self.get_command_signature(command)}```")
    if command.aliases:
      embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
    embed.set_footer(text="[] means that the part is optional, and <> means that it is required!", icon_url=self.context.me.avatar_url)
    return await self.context.send(embed=embed)
