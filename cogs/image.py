import wand, wand.color, wand.drawing, wand.image
import requests
import discord
import math
import json
from typing import Optional
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

    def _getimage(self, url: str):
        data = requests.get(url, stream=True).raw
        img = wand.image.Image(file=data)
        return img

    def _changecolor(self, img: wand.image.BaseImage, value :int = 2, gamma: int = 0.7, channel: str = 'red'):
        img.evaluate(operator='leftshift', value=value, channel=channel)
        img.level(gamma=gamma)
        return img

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

    def _zoomblur(self, url: str, a:int, e:bool):
        a = 2 if a >= 2 else a
        data = requests.get(url, stream=True).raw
        with wand.image.Image(file=data) as img:
            it = int((a-1) * math.hypot(img.width / 2, img.height / 2))
            w = img.width if not e else math.floor(img.width * a)
            h = img.height if not e else math.floor(img.height * a)
            imga = img.clone()
            for i in range(it):
                n = 1 / (i+2)
                o = 1 - n
                s = 1 + ((a-1) * (i + 1) / it)
                imgb = imga.clone()
                imgb.resize(int(imga.width * s), int(imga.height * s))
                imgb.crop(0, 0, width=w, height=h, gravity='center')
                imgb.composite(imga, operator='blend', arguments=str(o) + "x" + str(n), gravity='center')
                imga = imgb.clone()
            return img.clone()

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


    @commands.command()
    async def radial(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10):
        img = self._polarblur(url, strength, None)
        await self._postimage(ctx, img)

    @commands.command()
    async def radialred(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10):
        img = self._polarblur(url, strength, None)
        img = self._changecolor(img)
        await self._postimage(ctx, img)

    @commands.command()
    async def angular(self, ctx, url: str = "https://cataas.com/cat", angle: float = 30):
        img = self._polarblur(url, None, angle)
        await self._postimage(ctx, img)

    @commands.command()
    async def angularred(self, ctx, url: str = "https://cataas.com/cat", angle: float = 30):
        img = self._polarblur(url, None, angle)
        img = self._changecolor(img)
        await self._postimage(ctx, img)

    @commands.command()
    async def polar(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10, angle: int = 30):
        img = self._polarblur(url, strength, angle)
        await self._postimage(ctx, img)

    @commands.command()
    async def polarred(self, ctx, url: str = "https://cataas.com/cat", strength: float = 10, angle: int = 30):
        img = self._polarblur(url, strength, angle)
        img = self._changecolor(img)
        await self._postimage(ctx, img)

    @commands.command()
    async def zoomblur(self, ctx, url:str, a:int, e:bool):
        img = self._zoomblur(url, a, e)
        await self._postimage(ctx, img)

    @commands.command()
    async def zoomblurred(self, ctx, url: str, a: int, e: bool):
        img = self._zoomblur(url, a, e)
        img = self._changecolor(img)
        await self._postimage(ctx, img)

    @commands.command()
    async def eye(self, ctx, url: str):
        eyes = self._geteye(url)
        img = self._getimage(url)
        img = self._draweye(img, eyes)
        await self._postimage(ctx, img)
