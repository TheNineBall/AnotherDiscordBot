import wand, wand.color, wand.drawing, wand.image
import requests
import discord
from io import BytesIO
from discord.ext import commands


class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _postimage(self,ctx: commands.Context, img: wand.image.BaseImage):
        tmp = BytesIO(img.make_blob('jpg'))
        tmp.seek(0)
        await ctx.message.delete()
        await ctx.send(file=discord.File(tmp, str(ctx.message.id) + ".jpg"))

    @commands.command()
    async def radial(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10):
        data = requests.get(url, stream=True).raw
        with wand.image.Image(file=data) as img:
            img.virtual_pixel = 'edge'
            img.distort('depolar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            img.morphology('convolve', 'blur:0x' + str(strength) + ',90')
            img.virtual_pixel = 'horizontal_tile'
            img.background_color = 'black'
            img.distort('polar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            await self._postimage(ctx, img)

    @commands.command()
    async def radialred(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10):
        data = requests.get(url, stream=True).raw
        with wand.image.Image(file=data) as img:
            img.virtual_pixel = 'edge'
            img.distort('depolar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            img.morphology('convolve', 'blur:0x' + str(strength) + ',90')
            img.virtual_pixel = 'horizontal_tile'
            img.background_color = 'black'
            img.distort('polar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            img.evaluate(operator='leftshift', value=2, channel='red')
            await self._postimage(ctx, img)


    @commands.command()
    async def angular(self, ctx, url: str = "https://cataas.com/cat", angle: float = 30):
        data = requests.get(url, stream=True).raw
        with wand.image.Image(file=data) as img:
            img.virtual_pixel = 'tile'
            img.distort('depolar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            img.morphology('convolve', 'blur:0x0' + str((360 / img.width) * angle / 5))
            img.background_color = 'black'
            img.distort('polar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            await self._postimage(ctx, img)


    @commands.command()
    async def angularred(self, ctx, url: str = "https://cataas.com/cat", angle: float = 30):
        data = requests.get(url, stream=True).raw
        with wand.image.Image(file=data) as img:
            img.virtual_pixel = 'tile'
            img.distort('depolar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            img.morphology('convolve', 'blur:0x0' + str((360 / img.width) * angle / 5))
            img.background_color = 'black'
            img.distort('polar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            img.evaluate(operator='leftshift', value=2, channel='red')
            img.level(gamma=0.8)
            await self._postimage(ctx, img)


    @commands.command()
    async def polar(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10, angle: int = 30):
        data = requests.get(url, stream=True).raw
        with wand.image.Image(file=data) as img:
            img.virtual_pixel = 'tile'
            img.distort('depolar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            img.morphology('convolve', 'blur:0x' + str(strength) + ',90')
            img.morphology('convolve', 'blur:0x0' + str(360 / img.width * angle / 5))
            img.background_color = 'black'
            img.distort('polar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            await self._postimage(ctx, img)
