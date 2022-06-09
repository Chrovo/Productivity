import asyncio
from typing import Optional

import asyncpg
import discord
from discord.ext import commands

from .utils.converters import TimeConverter
from .utils.pagination import create_paginated_embed


class GeneralStudy(commands.Cog):
    """General commands and Study commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🧠" # create custom emojis later I guess.

    @commands.command(aliases=('remindme', 'remind',), description="Set a reminder for something!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reminder(self, ctx: commands.Context,time: TimeConverter, *, task: str):
        await discord.utils.sleep_until(time)
        await ctx.send(f"**Reminder**\n{ctx.author.mention}\nTask: {task}")

    @commands.command(aliases=('pomo',), description="Set a pomodoro timer!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pomodoro(self, ctx: commands.Context,times_repeated:int=1):
        num = times_repeated if times_repeated > 0 else 1
        
        if num > 5:
            return await ctx.send("Number of times repeated is too big!")
        
        for i in range(num):
            await asyncio.sleep(60*25)
            await ctx.send(f"{ctx.author.mention}! Your work time is done. Take a 5 minute break")
            await asyncio.sleep(60*5)
            await ctx.send(f"""Your five minute break is done! Back to work {ctx.author.mention}!
            \nThis work and break loop will repeat `{i}` more times!"""
            )

        return await ctx.send("Your pomodoro timer loop has ended! Good luck for whatever you were studying for!")
    
    async def _get_studyset_id(self, name: str, user_id: int) -> int:
        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                query = """
                SELECT * FROM studyset
                WHERE user_id = $1 AND studyset_name = $2;
                """
                output = await connection.fetchrow(query, user_id, name)
                _id = output['studyset_id']
                return _id

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def flashcards(self, ctx: commands.Context):
        """A flashcard system to study with!"""
        pass

    @flashcards.command(description="Add a flashcard to a studyset")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def add(self, ctx: commands.Context,studyset:str, *, flashcard:str):
        try:
            name, content = flashcard.split("|")
        except ValueError:
            return await ctx.send("You must seperate your flashcard's name and flashcard's content with a `|`")
 
        query = """
        INSERT INTO flashcards (studyset_id, flashcard_name, flashcard_content)
        VALUES ($1, $2, $3);
        """
        studyset_id = await self._get_studyset_id(studyset, ctx.author.id)
        await self.bot.db.execute(query, studyset_id, name, content)
        await ctx.send(f"Flashcard `{name}` with content `{content}` successfully created!")
    
    @flashcards.command(description="Remove a flashcard from a studyset")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx: commands.Context,studyset: str, *, flashcard: str):
        query = """
        DELETE FROM flashcards
        WHERE flashcard_name = $1 AND studyset_id = $2;
        """
        studyset_id = await self._get_studyset_id(studyset, ctx.author.id)
        await self.bot.db.execute(query, flashcard, studyset_id)
        await ctx.send(f"Flashcard {flashcard} successfully removed!")

    @flashcards.command(description="All of the flascards you have!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def all(self, ctx):
        pass

    @flashcards.command(description="Delete a study set!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete(self, ctx: commands.Context,studyset: str):
        query = """
        DELETE FROM studyset 
        WHERE studyset_name = $1 AND user_id = $2; 
        """
        await self.bot.db.execute(query, studyset, ctx.author.id)
        await ctx.send("Successfully deleted studyset!")

    @flashcards.command(description="Create a studyset!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def create(self, ctx: commands.Context, studyset: str):
        query = """
            INSERT INTO studyset (user_id, studyset_name)
            VALUES ($1, $2);
            """
        await self.bot.db.execute(query, ctx.author.id, studyset)
        await ctx.send(f"Studyset '{studyset}' created!")

    @flashcards.command(description="Study your cards! This uses active recall to help you study efficiently!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def study(self, ctx: commands.Context, studyset: str):
        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                studyset_id = await self._get_studyset_id(studyset, ctx.author.id)
                query = """
                SELECT * FROM flashcards
                WHERE studyset_id = $1;
                """
                output = await connection.fetch(query, studyset_id)

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in REACTIONS

                good:list[asyncpg.Record] = []
                ok:list[asyncpg.Record] = []
                bad:list[asyncpg.Record] = []
                REACTIONS = ['❌', '🤷', '✅', '⏹️']
                CONVERSIONS = {'❌':bad, '🤷':ok, '✅':good}
                index = 0
                
                message = await ctx.send(f"{output[index]['flashcard_name']} ||{output[index]['flashcard_content']}||")

                for react in REACTIONS:
                    await message.add_reaction(react)

                while ok != 0 or bad != 0 or output != 0:
                    latest_list = output if output else bad or ok

                    reaction, user = await self.bot.wait_for("reaction_add", check=check)

                    try:
                        await message.remove_reaction(reaction, user)
                    except discord.Forbidden:
                        pass

                    if str(reaction.emoji) == '⏹️':
                        return await message.delete()
                    try:
                        CONVERSIONS[str(reaction.emoji)].append(latest_list[index])
                    except IndexError:
                        break
                    
                    latest_list.pop(index)

                    latest_list = output if output else bad or ok
                    try:
                        name = latest_list[index]['flashcard_name']
                        content = latest_list[index]['flashcard_content']
                    except IndexError:
                        pass

                    await message.edit(content=f"{name} ||{content}||")
                
                return await message.edit(content=f"Nice! You studied {len(good)} flashcards!")

    @flashcards.command(description="Start your use of flashcard commands.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def start(self, ctx: commands.Context):
        query = """
            INSERT INTO users (user_id, username)
            VALUES ($1, $2);
            """

        try:
            await self.bot.db.execute(query, ctx.author.id, ctx.author.name)
            return await ctx.send("You have successfully started your use of flashcard commands!")
        except asyncpg.exceptions.UniqueViolationError:
            return await ctx.send("You have already started your use of flashcard commands earlier!")

    @flashcards.command(description="All of the studysets a user can own.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def studysets(self, ctx: commands.Context, member: Optional[commands.MemberConverter] = None):
        member = member or ctx.author

        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                query = """
                SELECT studyset_name FROM studyset
                WHERE studyset.user_id = $1;
                """
                studysets = await connection.fetch(query, (member.id))

                paginated_list = create_paginated_embed(
                    ctx,
                    studysets, 
                    "studyset_name", 
                    f"{member}'s studysets!", 
                    member.avatar.url, member
                    )

                await paginated_list.start(ctx)

    @flashcards.command(description="Update a studyset's name!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def edit(self, ctx: commands.Context, studyset: str, new_name: str):
        query = """
        UPDATE studyset
        SET studyset_name = $1
        WHERE user_id = $2 AND studyset_name = $3;
        """
        await self.bot.db.execute(query, new_name, ctx.author.id, studyset)
        return await ctx.send(f"Successfully updated studyset '{studyset}'! It's new name is '{new_name}'!")

    @flashcards.command(description="Update a flashcard!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def update(self, ctx: commands.Context,studyset:str, *, flashcard:str):
        try:
            before_name, after = flashcard.split(",")
            name, content = after.split("|")
        except ValueError:
            return await ctx.send(
                """
                You must seperate your old flashcard's name and new flashcard details with a `,`.
                Additionally, you must split your updated flashcard's details with a `|`\n
                For example: 
                pr!flashcards update studyset_name old_flashcard_name,new_flashcard_name|new_flashcard_content
                """
            )
        
        query = """
        UPDATE flashcards
        SET flashcard_name = $1, flashcard_content = $2
        WHERE studyset_id = $3 AND flashcard_name = $4;
        """
        studyset_id = await self._get_studyset_id(studyset, ctx.author.id)
        await self.bot.db.execute(query, name, content, studyset_id, before_name)
        return await ctx.send("Successfully updated flashcard!")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralStudy(bot))
