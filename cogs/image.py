import wand, wand.color, wand.drawing, wand.image
import requests
import discord
from typing import Optional
from io import BytesIO
from discord.ext import commands

# TODO eyes
# TODO lupe
# TODO zoomtext
# TODO Tshirt

class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _postimage(self,ctx: commands.Context, img: wand.image.BaseImage):
        tmp = BytesIO(img.make_blob('jpg'))
        tmp.seek(0)
        await ctx.message.delete()
        await ctx.send(file=discord.File(tmp, str(ctx.message.id) + ".jpg"))

    def _polarblur(self,url: str, strength: Optional[float] = None, angle: Optional[float] = None):
        data = requests.get(url, stream=True).raw
        with wand.image.Image(file=data) as img:
            img.virtual_pixel = 'tile'
            img.distort('depolar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            if strength is not None:
                img.morphology('convolve', 'blur:0x' + str(strength) + ',90')
            if angle is not None:
                img.morphology('convolve', 'blur:0x' + str(360 / img.width * angle / 5))
            img.background_color = 'black'
            img.distort('polar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
            return img.clone()

    @commands.command()
    async def radial(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10):
        img = self._polarblur(url, strength, None)
        await self._postimage(ctx, img)

    @commands.command()
    async def radialred(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10):
        img = self._polarblur(url, strength, None)
        img.evaluate(operator='leftshift', value=2, channel='red')
        img.level(gamma=0.8)
        await self._postimage(ctx, img)

    @commands.command()
    async def angular(self, ctx, url: str = "https://cataas.com/cat", angle: float = 30):
        img = self._polarblur(url, None, angle)
        await self._postimage(ctx, img)

    @commands.command()
    async def angularred(self, ctx, url: str = "https://cataas.com/cat", angle: float = 30):
        img = self._polarblur(url, None, angle)
        img.evaluate(operator='leftshift', value=2, channel='red')
        img.level(gamma=0.8)
        await self._postimage(ctx, img)

    @commands.command()
    async def polar(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10, angle: int = 30):
        img = self._polarblur(url, strength, angle)
        await self._postimage(ctx, img)

    @commands.command()
    async def polarred(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10, angle: int = 30):
        img = self._polarblur(url, strength, angle)
        img.evaluate(operator='leftshift', value=2, channel='red')
        img.level(gamma=0.8)
        await self._postimage(ctx, img)