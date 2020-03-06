from discord.ext import commands
import requests
import argparse
import asyncio
import lxml.html
from typing import Optional
from requests_html import AsyncHTMLSession
from lxml.cssselect import CSSSelector
import discord
from collections import Counter

WEBSITE = "https://aniwatcher.com"

class Anime(commands.Cog):
    """Generate random Anime links"""

    def __init__(self, bot):
        self.bot = bot

    async def getVid(self, link):
        if not link.startswith("https://aniwatcher.com") and not link.startswith("http://aniwatcher.com"):
            link = WEBSITE + link
        print(link)
        session = AsyncHTMLSession()
        try:
            resp = await session.get(link)
        except:
            return "error"
        try:
            await resp.html.arender(timeout=30,wait=5)
        except:
            return "timeout : " + link
        dt = resp.html.find(".srcnopop", first=True)
        if (dt == None):
            dt = resp.html.find(".srcpop", first=True)
        if (dt == None):
            x = "error"
        else:
            x = dt.attrs['src']
            if not x.startswith("http"):
                x = "http:" + x
        return x

    async def random(self, aid, ctx):
        '''gets the video url from a random anime from aniwatcher.com'''
        data = requests.get("https://aniwatcher.com/random.php")
        url = data.url
        page = 1
        while True:
            lx = lxml.html.fromstring(data.content)
            title = lx.findtext('.//title')
            img = lx.find_class('imgseries')[0].find("img").get('src')
            ep1 = lxml.html.fromstring(data.content).find_class("ep")
            if len(ep1) <= 0:
                print("error")
            ep1 = WEBSITE + ep1[-1].get('href')
            if "episode-1" in ep1:
                break
            page += 1
            data = requests.get(url + "?page=" + str(page))
        embed = discord.Embed(title=title, description=data.url, color=0xeee657)
        embed.add_field(name="ID", value=aid, inline=True)
        embed.add_field(name="Votes", value="0", inline=True)
        embed.set_thumbnail(url=WEBSITE + img) #set_image
        msg = await ctx.send(embed=embed)
        data2 = requests.get(ep1)
        sel = CSSSelector('a')
        sources = sel(lxml.html.fromstring(data2.content).get_element_by_id("sources"))
        self.bot.var[ctx.message.guild.id]['anime_msg'][aid] = msg
        self.bot.var[ctx.message.guild.id]['anime'][aid] = sources

    async def repostList(self, ctx, votes):
        for idx, anime in self.bot.var[ctx.message.guild.id]['anime_msg'].items():
            await anime.delete()
            embed = anime.embeds[0]
            embed.clear_fields()
            embed.add_field(name="ID", value=idx, inline=True)
            print(votes)
            print(votes[idx])
            embed.add_field(name="Votes", value=votes[idx], inline=True)
            self.bot.var[ctx.message.guild.id]['anime_msg'][idx] = await ctx.send(embed=embed)

    def reset(self, guild):
        self.bot.var[guild]['vote'] = 0 #ammount of votes needed to auto end vote
        self.bot.var[guild]['voted'] = {} #vote of each user with user as key and id of show as value
        self.bot.var[guild]['anime'] = {} #video sources for each show
        self.bot.var[guild]['anime_msg'] = {} #discord message with embeds for each show

    @commands.command()
    async def ranime(self, ctx, num: Optional[int] = 1, votes: Optional[int] = 0):
        '''returns an embed with the given number of random anime from aniwatcher.com'''
        if num >= 1 and votes == 0:
            votes = 1
        self.reset(ctx.message.guild.id)
        await asyncio.gather(*[self.random(i, ctx) for i in range(0, num)])
        self.bot.var[ctx.message.guild.id]['vote'] = votes
        if votes == 0:
            await self.endvote(ctx)

    @commands.command()
    async def vote(self, ctx, num: Optional[int] = 0):
        if self.bot.var[ctx.message.guild.id]['vote'] == 0:
            await ctx.send("no vote")
            return
        self.bot.var[ctx.message.guild.id]['voted'][ctx.message.author.id] = num
        await self.repostList(ctx, Counter(self.bot.var[ctx.message.guild.id]['voted'].values()))
        if len(self.bot.var[ctx.message.guild.id]['voted']) >= self.bot.var[ctx.message.guild.id]['vote']:
            await self.endvote(ctx)

    @commands.command()
    async def endvote(self, ctx):
        await ctx.send("winner:")
        aid = list(Counter(self.bot.var[ctx.message.guild.id]['voted'].values()))[0]
        embed = self.bot.var[ctx.message.guild.id]['anime_msg'][aid].embeds[0]
        embed.clear_fields()
        result = await asyncio.gather(*[self.getVid(l.get('href')) for l in self.bot.var[ctx.message.guild.id]['anime'][aid]])
        for it, r in enumerate(result):
            embed.add_field(name="stream {}".format(it + 1), value=r, inline=False)
        await ctx.send(embed=embed)
        await ctx.send("-----------------------------------------------------------------------------")
        self.reset(ctx.message.guild.id)

    @vote.after_invoke
    @endvote.after_invoke
    @ranime.after_invoke
    async def del_msg(self, ctx):
        await ctx.message.delete()
