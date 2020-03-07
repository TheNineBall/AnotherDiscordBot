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
import random

WEBSITE = "https://aniwatcher.com"


class Anime(commands.Cog):
    """Generate random Anime links"""

    def __init__(self, bot):
        self.bot = bot

    async def random(self, aid, ctx):
        l = "https://www16.gogoanime.io/anime-list.html?page={}".format(random.randint(0, 54))
        data = requests.get(l)
        sel = CSSSelector("a")
        vids = sel(lxml.html.fromstring(data.content).find_class("listing")[0])
        vid = random.choice(vids).get("href").replace("/category", "") + "-episode-1"

        data = requests.get("https://www16.gogoanime.io" + random.choice(vids).get("href"))
        url = data.url
        lx = lxml.html.fromstring(data.content)
        title = lx.findtext('.//title').replace("at Gogoanime", "")
        genre = ""
        genres = sel(lx.find_class("anime_info_body_bg")[0])
        for g in genres[2:]:
            genre = genre + g.text_content()
        im = CSSSelector("img")
        img = im(lx.find_class("anime_info_body_bg")[0])[0].get('src')

        l = "https://www16.gogoanime.io" + vid
        data = requests.get(l)
        sources = sel(lxml.html.fromstring(data.content).find_class("anime_muti_link")[0])

        embed = discord.Embed(title=title, description=url, color=0xeee657)
        embed.add_field(name="ID", value=aid, inline=True)
        embed.add_field(name="Votes", value="0", inline=True)
        embed.add_field(name="Genres", value=genre, inline=True)
        print(img)
        embed.set_thumbnail(url=img) #set_image
        msg = await ctx.send(embed=embed)

        self.bot.var[ctx.message.guild.id]['anime_msg'][aid] = msg
        self.bot.var[ctx.message.guild.id]['anime'][aid] = sources

    def getvid(self, link):
        if not link.startswith("http"):
            link = "http:" + link
            return link
        return link


    async def repostList(self, ctx, votes):
        for idx, anime in self.bot.var[ctx.message.guild.id]['anime_msg'].items():
            await anime.delete()
            embed = anime.embeds[0]
            embed.remove_field(1)
            embed.insert_field_at(1, name="Votes", value=votes[idx], inline=True)
            self.bot.var[ctx.message.guild.id]['anime_msg'][idx] = await ctx.send(embed=embed)

    def reset(self, guild):
        self.bot.var[guild]['vote'] = 0 #ammount of votes needed to auto end vote
        self.bot.var[guild]['voted'] = {} #vote of each user with user as key and id of show as value
        self.bot.var[guild]['anime'] = {} #video sources for each show
        self.bot.var[guild]['anime_msg'] = {} #discord message with embeds for each show

    @commands.command()
    async def ranime(self, ctx, num: Optional[int] = 1, votes: Optional[int] = 0):
        '''start, arguments: number(ammont of anime), number(ammount of votes)'''
        if num > 1 and votes == 0:
            votes = 1
        self.reset(ctx.message.guild.id)
        await asyncio.gather(*[self.random(i, ctx) for i in range(0, num)])
        self.bot.var[ctx.message.guild.id]['vote'] = votes
        if votes == 0:
            await self.endvote(ctx)

    @commands.command()
    async def Ranime(self, ctx):
        l = len(ctx.author.voice.channel.members)
        await self.ranime(ctx,l,l)


    @commands.command()
    async def vote(self, ctx, num: Optional[int] = 0):
        """vote for a series, argument: number(series id)"""
        if self.bot.var[ctx.message.guild.id]['vote'] == 0:
            await ctx.send("no vote")
            return
        self.bot.var[ctx.message.guild.id]['voted'][ctx.message.author.id] = num
        await self.repostList(ctx, Counter(self.bot.var[ctx.message.guild.id]['voted'].values()))
        if len(self.bot.var[ctx.message.guild.id]['voted']) >= self.bot.var[ctx.message.guild.id]['vote']:
            await self.endvote(ctx)

    @commands.command()
    async def endvote(self, ctx):
        """ends a vote early"""
        # await ctx.send("winner:")
        if len(list(Counter(self.bot.var[ctx.message.guild.id]['voted'].values()))) > 0:
            aid = list(Counter(self.bot.var[ctx.message.guild.id]['voted'].values()))[0]
        else:
            aid = random.choice(list(self.bot.var[ctx.message.guild.id]['anime'].keys()))
        embed = self.bot.var[ctx.message.guild.id]['anime_msg'][aid].embeds[0]
        embed.clear_fields()

        sources = self.bot.var[ctx.message.guild.id]['anime'][aid]
        for it, r in enumerate(sources):
            embed.add_field(name="stream {}".format(it + 1), value=self.getvid(r.get("data-video")), inline=False)

        await ctx.send(embed=embed)
        await ctx.send("-----------------------------------------------------------------------------")
        self.reset(ctx.message.guild.id)

    @commands.command()
    async def reroll(self, ctx, num: Optional[int] = -1):
        """replace id with a new random series, argument: number(series id)"""
        if num == -1:
            return;
        try:
            await self.bot.var[ctx.message.guild.id]['anime_msg'][num].delete()
        except:
            await ctx.send("given id might be wrong")
        await self.random(num, ctx)

    @vote.after_invoke
    @endvote.after_invoke
    @ranime.after_invoke
    @reroll.after_invoke
    async def del_msg(self, ctx):
        await ctx.message.delete()
