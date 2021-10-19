from discord.ext import commands


class Cat(commands.Cog):
    """Cat picture commands"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def cat(self, ctx):
        """returns a random cat"""
        await ctx.message.delete()
        await ctx.send("https://cataas.com/cat")


    @commands.command()
    async def catgif(self, ctx):
        """returns a random cat gif"""
        await ctx.message.delete()
        await ctx.send("https://cataas.com/cat/gif")


    @commands.command()
    async def catsay(self, ctx, text: str = "", color: str = ""):
        """returns a cat with: text, textcolor"""
        await ctx.message.delete()
        cat = "https://cataas.com/c/s/" + (text + '?s=50' + ("&c=" + color) if color != "" else "") if text != "" else ""
        await ctx.send(cat)

    @commands.command()
    async def catfilter(self, ctx, msg: str = ""):
        """add one of 'blur', 'mono', 'sepia', 'negative', 'paint', 'pixel'"""
        filter = ['blur', 'mono', 'sepia', 'negative', 'paint', 'pixel']
        if msg in filter:
            await ctx.message.delete()
            cat = "https://cataas.com/cat?filter=" + msg
            await ctx.send(cat)
        else:
            await ctx.send("possible filters are: ".join(filter))
