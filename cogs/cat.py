import discord
from discord.ext import commands


class Cat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def cat(self, ctx):
        await ctx.message.delete()
        await ctx.send("https://cataas.com/cat")


    @commands.command()
    async def catgif(self, ctx):
        await ctx.message.delete()
        await ctx.send("https://cataas.com/cat/gif")


    @commands.command()
    async def catsay(self, ctx, text: str = "", color: str = ""):
        await ctx.message.delete()
        cat = "https://cataas.com/c/s/" + (text + ("&c=" + color) if color != "" else "") if text != "" else ""
        await ctx.send(cat)

    @commands.command()
    async def catfilter(ctx, msg: str = ""):
        filter = ['blur', 'mono', 'sepia', 'negative', 'paint', 'pixel']
        if msg in filter:
            await ctx.message.delete()
            cat = "https://cataas.com/cat?filter=" + msg
            await ctx.send(cat)
        else:
            await ctx.send("possible filters are: ".join(filter))
