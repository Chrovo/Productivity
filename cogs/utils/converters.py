import datetime
import re

import discord
from discord.ext import commands

__all__ = (
    'TimeConverter',
    'CodeblockConverter',
)

class TimeConverter(commands.Converter):
    
    async def convert(self, ctx:commands.Context, argument:str) -> datetime.datetime:
        try:

            if re.search(r"[0-9]+(s|m|h|d)", argument): # eg.) 5s
                timedict = {'s':1, 'm':60, 'h':3600, 'd':86400}
                time_nums = int(argument[:-1])
                sign = timedict[argument[-1]]
                time = sign*time_nums # total time in seconds
                utcnow_posix = int(datetime.datetime.utcnow().timestamp())

                return datetime.datetime.fromtimestamp(utcnow_posix + time)

            elif re.search(r"<t:[0-9]+:(F|t|T|d|D|f|R)>", argument): # eg.) <t:0:t>
                return datetime.datetime.utcfromtimestamp(int(argument[3:-3]))
            
            else:
                raise AttributeError # will be caught in try/except.

        except Exception:
            raise commands.BadArgument("Argument failed to convert into 'datetime.datetime' object")


class CodeblockConverter(commands.Converter):

    async def convert(self, ctx:commands.Context, argument:str) -> str:
        if not argument.startswith("`"): # no codeblock
            return argument

        elif argument.startswith("```\n") and argument.endswith("```"): # no language chosen
            return argument[3:-3]

        elif argument.startswith('`') and argument.endswith('`') and argument[1] != '`': # 1 tic codeblock
            return argument[1:-1]

        elif '\n' not in argument and argument.startswith('```') and argument.endswith('```'): # one line codeblock
            return argument[3:-3]

        elif re.search("^```[a-zA-Z]+\n", argument): # codeblock with language
            arg = ((argument.replace("```", "")).split('\n'))[1:]
            return "\n".join(arg)
