import random
from discord.ext import commands


class Various(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, text: str = ""):
        """say text"""
        await ctx.send(text)

    async def cog_after_invoke(self, ctx):
        await ctx.message.delete()
