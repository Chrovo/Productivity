import asyncpg
import discord
from discord.ext import commands

from .utils.pagination import create_paginated_embed

class Todo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.emoji = '📝'

    async def _get_last_priority(self, user_id:int) -> int:
        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                query = """
                SELECT * FROM todo
                WHERE user_id = $1;
                """
                results = await connection.fetch(query, user_id)
    
                if results:
                    return results[len(results)-1]['priority'] + 1

                return 1
    
    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def todo(self, ctx):
        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                query = """
                SELECT * FROM todo
                WHERE user_id = $1;
                """
                todo_list = await connection.fetch(query, ctx.author.id)
                
                paginated = create_paginated_embed(
                    ctx, 
                    todo_list, 
                    "todo_content", 
                    f"{ctx.author}'s todo list!", 
                    ctx.author.avatar_url, 
                    ctx.author,
                    )
                await paginated.start(ctx)

    @todo.command(description="Start your usage of the todo commands!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def start(self, ctx):
        query = """
        INSERT INTO todo_users (user_id, username)
        VALUES ($1, $2);
        """
        try:
            await self.bot.db.execute(query, ctx.author.id, ctx.author.name)
            return await ctx.send("Successfully registered!")
        except Exception:
            return await ctx.send("An error has occurred, not successfully registered your account.")

    @todo.command(description="Add a task to the end of your todo list!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def add(self, ctx, *, task:str):
        query = """
        INSERT INTO todo (user_id, todo_content, priority)
        VALUES ($1, $2, $3);
        """
        try:

            priority = await self._get_last_priority(ctx.author.id)
            await self.bot.db.execute(query, ctx.author.id, task, priority)

            return await ctx.send("Successfully added that to your todo list!")

        except Exception:
            return await ctx.send("Could not successfully add that to your todo list!")

    @todo.command(description="Delete a task from your todo list!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete(self, ctx, priority:int):
        query = """
        DELETE FROM todo
        WHERE user_id = $1 AND priority = $2;
        """
        try:
            await self.bot.db.execute(query, ctx.author.id, priority)
            return await ctx.send("Successfully deleted that task!")
        except Exception:
            return await ctx.send("Could not delete that.")

    @todo.command(description="Update a task on your todo list!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def edit(self, ctx, priority:int, *, task:str):
        query = """
        UPDATE todo
        SET priority = $1, todo_content = $2
        WHERE user_id = $3 AND priority = $1;
        """
        try:
            await self.bot.db.execute(query, priority, task, ctx.author.id)
            return await ctx.send("Successfully updated your todo list!")
        except Exception:
            return await ctx.send("Could not update that.")

    @todo.command(description="Edit the priority of a task on your todolist!", aliases=['priority'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def change_priority(self, ctx, old_priority:int, new_priority:int):
        query = """
        UPDATE todo
        SET priority = $1
        WHERE user_id = $2 AND priority = $3;
        """
        try:
            await self.bot.db.execute(query, new_priority, ctx.author.id, old_priority)
            return await ctx.send("Successfully changed priority")
        except Exception:
            return await ctx.send("Could not update the priority.")

def setup(bot):
    bot.add_cog(Todo(bot))