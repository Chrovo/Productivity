from typing import Union, Optional, TYPE_CHECKING

import asyncpg
import discord
from discord.ext import commands, menus

class Pagination(menus.Menu):

    def __init__(
        self, 
        ctx:commands.Context, *, 
        messages:list[Union[discord.Message, discord.Embed]]
        ) -> None:
            super().__init__()
            self.ctx = ctx
            self.messages = messages
            self.index = 0

    async def _embed_or_message(
        self, *, 
        message:Union[discord.Message, discord.Embed], 
        action:str, 
        channel:discord.TextChannel
        ) -> None:
            ACTIONS = {"edit":self.message.edit, "send":channel.send,}

            if isinstance(message, discord.Embed):
                await ACTIONS[action.lower()](embed=message)

            elif isinstance(message, discord.Message):
                await ACTIONS[action.lower()](message)

    async def send_initial_message(self, ctx, channel):
        if isinstance(self.messages[0], discord.Message):
            return await ctx.send(self.messages[0])

        else:  
            return await channel.send(embed=self.messages[0])

    @menus.button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def on_back_press(self, payload):
        first_message = self.messages[0]
        self.index = 0
        await self._embed_or_message(message=first_message, action="edit", channel=self.message.channel)

    @menus.button('\N{BLACK LEFT-POINTING TRIANGLE}')
    async def on_left_press(self, payload):
        self.index = self.index-1 if self.index-1 >= 0 else self.index
        embed = self.messages[self.index]
        await self._embed_or_message(message=embed, action="edit", channel=self.message.channel)

    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}')
    async def on_right_press(self, payload):
        self.index = self.index+1 if self.index+1 < len(self.messages) else self.index
        embed = self.messages[self.index]
        await self._embed_or_message(message=embed, action="edit", channel=self.message.channel)
    
    @menus.button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}')
    async def on_fast_forward_press(self, payload):
        embed = self.messages[-1]
        self.index = len(self.messages)
        await self._embed_or_message(message=embed, action="edit", channel=self.message.channel)

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        self.stop()
        await self.message.delete()

def create_paginated_embed(
    ctx:commands.Context,
    records: list[asyncpg.Record], 
    value:str, 
    embed_title: str,
    av_url: Optional[str]=None,
    author: Optional[str]=None
    ) -> discord.Embed:

    embeds_list = []

    for index, rec in enumerate(records):
    
        if index%10 == 0:
    
            embed = discord.Embed(title=embed_title, description='')

            if av_url and author:
                embed.set_author(name=author, icon_url=av_url)

            embed.description+=f'{index+1}.) {rec[value]}\n'

            embeds_list.append(embed)

        else:
            embed = embeds_list[len(embeds_list)-1]
            embed.description+=f'{index+1}.) {rec[value]}\n'
    
    return Pagination(ctx, messages=embeds_list)

