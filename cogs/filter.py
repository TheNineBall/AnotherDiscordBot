import requests
import zlib
import re
import discord
from typing import Optional
from discord.ext import commands


class Filter(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rremove(self, ctx, num: Optional[int] = 1, emoji: Optional[str] = u'🐴'):
        await ctx.message.delete()
        if num > 10:
            send = await ctx.send("are you sure? this action is not reversible. (yes/no)")
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            await send.delete()
            await msg.delete()
            if msg.content != "yes":
                return
        async for m in ctx.channel.history(limit=num):
            for e in m.reactions:
                if str(emoji) == str(e.emoji):
                    await e.clear()
