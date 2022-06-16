from typing import Optional

import discord
from discord.ext import commands

from .utils.pagination import create_paginated_embed # type: ignore

class Tags(commands.Cog):
    """Productivity's tag system."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🏷️ "

    async def delete_check(self, ctx:commands.Context, tag_name) -> bool:
        query = """
        SELECT * FROM tags
        WHERE tag_name = $1 AND guild_id = $2;
        """
        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                fetched = await connection.fetchrow(query, tag_name, ctx.guild.id)
                return fetched['user_id'] == ctx.author or ctx.author.guild_permissions.manage_messages

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tag(self, ctx, *, tag:str):
        """A tag system!"""
        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                try:
                    query = """
                    SELECT * FROM tags
                    WHERE tag_name = $1 AND guild_id = $2;
                    """
                    tag = await connection.fetchrow(query, tag, ctx.guild.id)
                    return await ctx.send(tag['tag_content'])
                except TypeError:
                    return await ctx.send("Tag not found.")

    @tag.command(description="Create a tag!", aliases=['add'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def create(self, ctx, name, *, content):
        try:
            query = """
            INSERT INTO tags (user_id, guild_id, tag_name, tag_content)
            VALUES ($1, $2, $3, $4);
            """
            await self.bot.db.execute(query, ctx.author.id, ctx.guild.id, name, content)
            await ctx.send("Succesfully created the tag!")
        except Exception as e:
            await ctx.send(e)
            await ctx.send("An error has occurred whilst creating the tag")

    @tag.command(description="Start your use of creating tags")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def start(self, ctx):
        try:
            query = """
            INSERT INTO tag_users (user_id, username)
            VALUES ($1, $2);
            """
            await self.bot.db.execute(query, ctx.author.id, ctx.author.name)
            await ctx.send("Successfully started your use of our tag system!")
        except Exception:
            await ctx.send("You are already in our database!")

    @tag.command(description="Delete a tag!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete(self, ctx, *, tag:str):
        check = await self.delete_check(ctx, tag)

        if check:
            try:
                query = """
                DELETE FROM tags
                WHERE tag_name = $1 AND guild_id = $2;
                """
                await self.bot.db.execute(query, tag, ctx.guild.id)
    
                await ctx.send("Successfully deleted tag!")
            except:
                await ctx.send("An error has occurred while attempting to delete the tag.")
        else:
            await ctx.send("You do not have permission to delete this tag!")

    @commands.command(description="Look at all of the tags a member has!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tags(self, ctx, member:Optional[discord.Member]=None):
        member = member or ctx.author

        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                query = """
                SELECT * FROM tags
                WHERE user_id = $1 AND guild_id = $2;
                """
                tags = await connection.fetch(query, member.id, ctx.guild.id)

                if not tags:
                    return await ctx.send('User has no tags!')

                paginate = create_paginated_embed(ctx, tags, 'tag_name', f"{member}'s tags", member.avatar.url, member.name)
                await paginate.start(ctx)

    @tag.command(description="Edit a tag!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def edit(self, ctx, old_tag, new_name, *, new_content):
        query = """
        UPDATE tags
        SET tag_name = $1, tag_content = $2
        WHERE user_id = $3 AND tag_name = $4 AND guild_id = $5;
        """
        try:
            await self.bot.db.execute(query, new_name, new_content, ctx.author.id, old_tag, ctx.guild.id)
            return await ctx.send("Successfully edited tag!")
        except Exception:
            return await ctx.send(
                """
                An error occurred while editing the tag, 
                this is likely because u dont own this tag or it doesnt exist.
                """
                )

    @tag.command(description="View information about a tag!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx, *, tag:str):
        async with self.bot.db.acquire() as connection:
            async with connection.transaction():
                query = """
                SELECT * FROM tags
                WHERE guild_id = $1 AND tag_name = $2;
                """
                try:
                    tag_info = await connection.fetchrow(query, ctx.guild.id, tag)

                    owner = ctx.guild.get_member(tag_info['user_id'])

                    embed = discord.Embed(title=tag_info['tag_name'])
                    embed.add_field(name="Owner", value=owner.mention)
                    embed.set_author(name=owner, icon_url=owner.avatar.url)

                    return await ctx.send(embed=embed)

                except TypeError:
                    return await ctx.send("Tag not found.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tags(bot))
