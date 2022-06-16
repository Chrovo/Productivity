import inspect
import pydoc
import re
import time
import zlib
from io import BytesIO
from typing import Optional

import discord
from discord.ext import commands

from .utils.request import Requests # type: ignore
from .utils.converters import CodeblockConverter # type: ignore

class Writeable:
    def __init__(self) -> None:
        self.str = ''
    def write(self, writing) -> None:
        self.str += discord.utils.escape_markdown(writing)


class ComputerScience(commands.Cog):
    """Computer Science/Programming/Coding commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = "💻" # create custom emojis later I guess.

    @commands.command(aliases=("src",), description="This will return the source code of Productivity")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def source(self, ctx: commands.Context, command: Optional[str] = None):
        if not command:
            await ctx.send("Here is the GitHub repository: https://github.com/Chrovo/Productivity")

        elif command.lower() == "help":
            return await ctx.send("https://github.com/Chrovo/Productivity/blob/main/help.py#L69-L117")

        else:
            base_url = "https://github.com/Chrovo/Productivity/blob/main"
            cmd = self.bot.get_command(command)

            if not cmd:
                await ctx.send(f'No command called "{command}" found.')

            path = inspect.getsourcefile(cmd.callback.__code__)
            srcfile = path[38:].replace(r'\\', '/')
            codelines, starterline = inspect.getsourcelines(cmd.callback.__code__)
            base_url+=f"{srcfile}#L{starterline}-L{len(codelines)+starterline}"

            await ctx.send(base_url)

    @commands.command(description="Search through documentations!", aliases=('docs', 'documentation', 'rtfd',))
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rtfm(self, ctx: commands.Context, lib: str, search: str): # cache stuff later
        ALL_LIBS = {
            'python':'https://docs.python.org/3/objects.inv',
            'dpy':'https://discordpy.readthedocs.io/en/latest/objects.inv',
            'requests':'https://docs.python-requests.org/en/latest/objects.inv',
            'pygame':'https://www.pygame.org/docs/objects.inv',
            'lark':'https://lark-parser.readthedocs.io/en/latest/objects.inv',
            'aiohttp':'https://docs.aiohttp.org/en/stable/objects.inv',
            'numpy':'https://numpy.org/doc/1.20/objects.inv',
            'matplotlib':'https://matplotlib.org/stable/objects.inv',
            'pandas':'https://pandas.pydata.org/pandas-docs/stable/objects.inv',
            'asyncpg':'https://magicstack.github.io/asyncpg/current/objects.inv',
            'pillow':'https://pillow.readthedocs.io/en/stable/objects.inv',
            'pros':'https://pros.cs.purdue.edu/v5/objects.inv',
        }

        lib = ALL_LIBS.get(lib.lower())

        if not lib:
            return await ctx.send(
                f'That library is not supported yet! Try these instead\n{", ".join(ALL_LIBS.keys())}'
            )

        search = re.escape(search)
        async with self.bot.session.get(lib) as r:
            data = BytesIO(await r.read())
            decobj = zlib.decompressobj()

            for i in range(4):
                data.readline()

            info = data.read()
            decompressed = str(decobj.decompress(info)).split('\\n')
            sug = [line for line in decompressed if re.search(search, line)]

            if not sug:
                return await ctx.send("Could not find anything.")

            embed = discord.Embed(title=f"Documentation search!", description="")

            num_sug = len(sug) if len(sug) < 10 else 10
            
            for j in range(num_sug):
                line = sug[j].split()
                if lib == 'https://pros.cs.purdue.edu/v5/objects.inv':
                    embed.description+=f"[`{line[0]}`]({lib[:-11]}{line[3]})\n"
                else:
                    embed.description+=f"[`{line[0]}`]({lib[:-11]}{line[-2][:-1]}{line[0]})\n"

            return await ctx.send(embed=embed)


    @commands.command(aliases=('gitsearch',), description="Search for a user on GitHub!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def github(self, ctx: commands.Context, *, user: str):
        user = user.split()
        link = f"https://api.github.com/users/{'-'.join(user)}"

        data = await Requests.get(self.bot.session, link)

        em = discord.Embed(title=f"Github Search for: {data['login']}")
        em.add_field(name="Id", value=f"{data['id']}", inline=False)
        em.set_thumbnail(url=data['avatar_url'])
        em.add_field(name="Link", value=f"{data['html_url']}", inline=False)
        em.add_field(name="Repos", value=f"{data['repos_url']}", inline=False)
        em.add_field(name="Created At", value=data['created_at'], inline=False)
        em.add_field(name="Node ID", value=data['node_id'], inline=False)

        return await ctx.send(embed=em)

    @commands.command(aliases=("PyPi",), description="Search for something on PyPi")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pypi(self, ctx: commands.Context, *, lib: str):
        lib = lib.replace(" ", "-")
        pypilink = f"https://pypi.org/pypi/{lib}/json"
        data = await Requests.get(self.bot.session, pypilink)

        if not data:
            return await ctx.send("Could not find that library.")

        libinfo = data['info']
        author = libinfo['author'] or "Unknown"
        email = libinfo['author_email'] or "Unknown"
        lisc = libinfo['license'] or "Unknown"
        desc = libinfo["description"] or "Unknown"
        num = len(desc) if len(desc) < 200 else 200

        em = discord.Embed(title = "Pypi search results", description = f"Searches {lib}")
        em.set_thumbnail(url="https://1.bp.blogspot.com/-3vjua3XTKXY/XA-QFPCIdII/AAAAAAAAVAg/i3Gpp6O3gyYO4hNW25DJ4lGy2nSc3R_6wCLcBGAs/s1600/pypi.png")
        em.add_field(name="Author", value=author, inline=False)
        em.add_field(name="Author Email", value=email, inline=False)
        em.add_field(name="License", value=lisc, inline=False)
        em.add_field(name="Description", value=f"{desc[0:num]}...", inline=False)

        return await ctx.send(embed=em)

    @commands.command(aliases=("eval", "run",), description="Run a piece of code!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _eval(self, ctx, language: str, *, code: CodeblockConverter):
        lang_data = await Requests.get(self.bot.session, "https://emkc.org/api/v2/piston/runtimes")
        ALL_LANGS = [lang['language'] for lang in lang_data]

        start = time.perf_counter()

        data = await Requests.post(
            self.bot.session, 
            "https://emkc.org/api/v1/piston/execute", 
            data={"source":code, "language":language,},
            )

        end = time.perf_counter()

        output = data.get('output', f'That language is not supported yet! Try these instead: {", ".join(ALL_LANGS)}')

        return await ctx.send(
            f"```{output}```", 
            embed=discord.Embed(
                description=f"""Executed in: `{(end - start):.2f}` seconds
                \nLanguage: `{data.get('language', "N/A")} version {data.get('version', 'N/A')}`"""
                )
            )

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def python(self, ctx: commands.Context, query: str):
        helper = pydoc.Helper(output=Writeable())
        helper.help(query)
        output = helper.output.str

        if output == '\n':
            return await ctx.send('Nothing was found')

        elif len(output) >= 2000:
            output = output[0:1995]
        
        await ctx.send(output)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ComputerScience(bot))
