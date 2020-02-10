import re
import requests
import discord

def get_images(msg: discord.message.Message):
    imgs = []
    for x in re.finditer("(?P<url>https?://[^\s]+)", msg.content):
        if x.group().endswith(('.jpg', '.png', '.jpeg', '.gif')):
            data = requests.get(x.group()).content
            imgs.append(data)
    for x in msg.attachments:
        if x.group().endswith(('.jpg', '.png', '.jpeg', '.gif')):
            data = requests.get(x.group()).content
            imgs.append(data)
    return imgs


    # async def _check_perm(self, ctx, rank: int):
    #     if ctx.message.author.server_permission.administrator:
    #         return True
    #     if ctx.message.author in [res[1] for res in await self.bot.db.getu()]:
    #         return True
    #     return False