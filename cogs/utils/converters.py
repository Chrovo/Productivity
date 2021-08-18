import datetime
import re

import discord
from discord.ext import commands

class TimeConverter(commands.Converter):
    
    async def convert(self, ctx:commands.Context, argument:str) -> datetime.datetime:
        try:

            if re.search(r"[0-9]+(s|m|h|d)", argument):
                timedict = {'s':1, 'm':60, 'h':3600, 'd':86400}
                time_nums = int(argument[:-1])
                sign = timedict[argument[-1]]
                time = sign*time_nums # total time in seconds
                utcnow_posix = int(datetime.datetime.utcnow().timestamp())

                return datetime.datetime.fromtimestamp(utcnow_posix + time)

            elif re.search(r"<t:[0-9]+:(F|t|T|d|D|f|R)>", argument):
                return datetime.datetime.utcfromtimestamp(int(argument[3:-3]))
            
            else:
                raise AttributeError # will be caught in try/except.

        except Exception:
            raise commands.BadArgument("Argument failed to convert into 'datetime.datetime' object")
