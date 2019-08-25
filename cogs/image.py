import wand, wand.color, wand.drawing, wand.image
import requests
import discord
import math
import json
from typing import Optional
from io import BytesIO
from discord.ext import commands


class Image(commands.Cog):
    """Add 'eye' for red eye overlay or 'red','gray','cyan','green','magenta','blue','yellow','black'
    for color enhancement after a command"""

    def __init__(self, bot):
        self.bot = bot
        self.colors = ['red','gray','cyan','green','magenta','blue','yellow','black']
        self.gamma = 0.6
        self.value = 1

    async def _postimage(self, ctx: commands.Context, img: wand.image.BaseImage):
        tmp = BytesIO(img.make_blob('jpg'))
        tmp.seek(0)
        await ctx.message.delete()
        await ctx.send(file=discord.File(tmp, str(ctx.message.id) + ".jpg"))

    def _getimage(self, url: str):
        try:
            data = requests.get(url, stream=True).raw
            img = wand.image.Image(file=data)
        except Exception:
            data = requests.get("https://cataas.com/cat", stream=True).raw
            img = wand.image.Image(file=data)
        return img

    def _changecolor(self, img: wand.image.BaseImage, channel: Optional[str] = 'red'):
        img.evaluate(operator='leftshift', value=self.value, channel=channel)
        img.level(gamma=self.gamma)
        return img

    def _polarblur(self, img: wand.image.BaseImage, strength: Optional[float] = None, angle: Optional[float] = None):
        img.virtual_pixel = 'tile'
        img.distort('depolar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
        if strength is not None:
            img.morphology('convolve', 'blur:0x' + str(strength) + ',90')
        if angle is not None:
            img.morphology('convolve', 'blur:0x' + str(360 / img.width * angle / 5))
        img.background_color = 'black'
        img.distort('polar', (-1, 0, img.width / 2, img.height / 2, 0, 0))
        return img.clone()

    def _zoomblur(self, img: wand.image.BaseImage, zoom: float = 1.2, keep: bool = True):
        zoom = 2 if zoom >= 2 else zoom
        it = int((zoom - 1) * math.hypot(img.width / 2, img.height / 2))
        w = img.width if not keep else math.floor(img.width * zoom)
        h = img.height if not keep else math.floor(img.height * zoom)
        imga = img.clone()
        for i in range(it):
            n = 1 / (i+2)
            o = 1 - n
            s = 1 + ((zoom - 1) * (i + 1) / it)
            imgb = imga.clone()
            imgb.resize(int(imga.width * s), int(imga.height * s))
            imgb.crop(0, 0, width=w, height=h, gravity='center')
            imgb.composite(imga, operator='blend', arguments=str(o) + "x" + str(n), gravity='center')
            imga = imgb.clone()
        return imga.clone()

    def _geteye(self, url):
        face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
        headers = {'Ocp-Apim-Subscription-Key': self.bot.key_azur}
        params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'true',
        }
        response = requests.post(face_api_url, params=params, headers=headers, json={"url": url})
        res = []
        for r in response.json():
            j = ('{"width": "' + str(r['faceRectangle']['width']) + '",' +
                 '"left": {"x": ' + str(r['faceLandmarks']['pupilLeft']["x"]) + ", " +
                          '"y": ' + str(r['faceLandmarks']['pupilLeft']["y"]) + "}, " +
                 '"right": {"x": ' + str(r['faceLandmarks']['pupilRight']["x"]) + ", " +
                           '"y": ' + str(r['faceLandmarks']['pupilRight']["y"]) + "}}")
            res.append(json.loads(j))
        return res

    def _draweye(self, img: wand.image.Image, res):
        with wand.image.Image(filename="./" + self.bot.resources + "eye1.png") as eye:
            for r in res:
                facew = int(r['width'])
                rs = (facew / eye.width) * 4
                eye.resize(int(eye.width * rs), int(eye.height * rs))
                x1 = int(r['left']["x"]) - eye.width / 2
                y1 = int(r['left']["y"]) - eye.height / 2
                x2 = int(r['right']["x"]) - eye.width / 2
                y2 = int(r['right']["y"]) - eye.height / 2
                img.composite(eye, left=int(x1), top=int(y1))
                img.composite(eye, left=int(x2), top=int(y2))
            return img.clone()

    def _handleargs(self, img: wand.image.Image, url: str,  args):
        if "eye" in args:
            eyes = self._geteye(url)
            img = self._draweye(img, eyes)
        for c in self.colors:
            if c in args:
                print("colo: " + c)
                self._changecolor(img, c)
        return img

    @commands.command()
    async def radial(self, ctx, url: str = "", strength: Optional[float] = 10, *args):
        """image filter: url, strength[optional]"""
        img = self._getimage(url)
        img = self._polarblur(img, strength, None)
        img = self._handleargs(img, url, args)
        await self._postimage(ctx, img)

    @commands.command()
    async def angular(self, ctx, url: str = "", angle: Optional[float] = 30, *args):
        """image filter: url, angle[optional]"""
        img = self._getimage(url)
        img = self._polarblur(img, None, angle)
        img = self._handleargs(img, url, args)
        await self._postimage(ctx, img)

    @commands.command()
    async def polar(self, ctx, url: str = "", strength: Optional[float] = 10, angle: Optional[int] = 30, *args):
        """image filter: url, strength[optional], angle[optional]"""
        img = self._getimage(url)
        img = self._polarblur(img, strength, angle)
        img = self._handleargs(img, url, args)
        await self._postimage(ctx, img)

    @commands.command()
    async def zoomblur(self, ctx, url: str = "", zoom: Optional[float] = 1.2, keep: Optional[bool] = True, *args):
        """image filter: url, zoom[optional], keep size[optional]"""
        img = self._getimage(url)
        img = self._zoomblur(img, zoom, keep)
        img = self._handleargs(img, url, args)
        await self._postimage(ctx, img)

    @commands.command()
    async def eye(self, ctx, url: str = "", *args):
        """adds red eyes: url"""
        img = self._getimage(url)
        args = args + ("eye",)
        img = self._handleargs(img, url, args)
        await self._postimage(ctx, img)
