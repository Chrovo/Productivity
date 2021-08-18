import asyncio
from typing import Optional

import asyncpg
import discord
from discord.ext import commands

from .utils.converters import TimeConverter


class GeneralStudy(commands.Cog):
    """General commands and Study commands."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🧠" # create custom emojis later I guess.

    @commands.command(aliases=['remindme', 'remind'], description="Set a reminder for something!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reminder(self, ctx, time:TimeConverter, *, task:str):
        await discord.utils.sleep_until(time)
        await ctx.send(f"**Reminder**\n{ctx.author.mention}\nTask: {task}")

    @commands.command(aliases=['pomo'], description="Set a pomodoro timer!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pomodoro(self, ctx, times_repeated:int=1):
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
    
    async def _get_studyset_id(self, name:str, user_id:int) -> int:
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
    async def flashcards(self, ctx):
        """A flashcard system to study with!"""
        pass

    @flashcards.command(description="Add a flashcard to a studyset")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def add(self, ctx, studyset:str, *, flashcard:str):
        try:
            name, content = flashcard.split("|")
        except ValueError:
            return await ctx.send("You must seperate your flashcard's name and flashcard's content with a `|`")
        # add something to get the studyset id later
        query = """
        INSERT INTO flashcards (studyset_id, flashcard_name, flashcard_content)
        VALUES ($1, $2, $3);
        """
        studyset_id = await self._get_studyset_id(studyset, ctx.author.id)
        await self.bot.db.execute(query, studyset_id, name, content)
        await ctx.send(f"Flashcard `{name}` with content `{content}` successfully created!")
    
    @flashcards.command(description="Remove a flashcard from a studyset")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx, studyset:str, *, flashcard:str):
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
    async def delete(self, ctx, studyset:str):
        query = """
        DELETE FROM studyset 
        WHERE studyset_name = $1 AND user_id = $2; 
        """
        await self.bot.db.execute(query, studyset, ctx.author.id)
        await ctx.send("Successfully deleted studyset!")

    @flashcards.command(description="Create a studyset!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def create(self, ctx, studyset:str):
        query = """
            INSERT INTO studyset (user_id, studyset_name)
            VALUES ($1, $2);
            """
        await self.bot.db.execute(query, ctx.author.id, studyset)
        await ctx.send(f"Studyset '{studyset}' created!")

    @flashcards.command(description="Study your cards!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def study(self, ctx, studyset:str):
        pass

    @flashcards.command(description="Start your use of flashcard commands.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def start(self, ctx):
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
    async def studysets(self, ctx, member:Optional[commands.MemberConverter]=None):
        member = member or ctx.author

        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                query = """
                SELECT studyset_name FROM studyset
                WHERE studyset.user_id = $1;
                """
                studysets = await connection.fetch(query, (member.id))

                embed = discord.Embed(title=f"{member}'s studysets!")
                embed.description = f"{member} has {len(studysets)} studysets!\n"
                for match in studysets:
                    embed.description+=f"- `{match['studyset_name']}`\n"
                
                return await ctx.send(embed=embed)

    @flashcards.command(description="Update a studyset's name!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def edit(self, ctx, studyset:str, new_name:str):
        query = """
        UPDATE studyset
        SET studyset_name = $1
        WHERE user_id = $2 AND studyset_name = $3;
        """
        await self.bot.db.execute(query, new_name, ctx.author.id, studyset)
        return await ctx.send(f"Successfully updated studyset '{studyset}'! It's new name is '{new_name}'!")

def setup(bot):
    bot.add_cog(GeneralStudy(bot))
