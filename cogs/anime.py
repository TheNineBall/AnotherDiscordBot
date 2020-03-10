from discord.ext import commands
import requests
import asyncio
import lxml.html
from typing import Optional
from lxml.cssselect import CSSSelector
import discord
from collections import Counter
import random


class Anime(commands.Cog):
    """Generate random Anime links"""

    def __init__(self, bot):
        self.bot = bot

    async def random(self, aid, message):
        l = "https://www16.gogoanime.io/anime-list.html?page={}".format(random.randint(0, 54))
        data = requests.get(l)
        sel = CSSSelector("a")
        vids = sel(lxml.html.fromstring(data.content).find_class("listing")[0])
        #vid = random.choice(vids).get("href").replace("/category", "") + "-episode-1"

        data = requests.get("https://www16.gogoanime.io" + random.choice(vids).get("href"))
        url = data.url
        lx = lxml.html.fromstring(data.content)
        title = lx.findtext('.//title').replace("at Gogoanime", "")
        genre = ""
        genres = sel(lx.find_class("anime_info_body_bg")[0])
        for g in genres[2:]:
            genre = genre + g.text_content()
        im = CSSSelector("img")
        img = im(lx.find_class("anime_info_body_bg")[0])[0].get('src').replace(" ", "%20")
        vid = url.replace("/category", "") + "-episode-1"

        embed = discord.Embed(title=title, description=url, color=0x36393f)#eee657
        embed.add_field(name="ID", value=aid, inline=True)
        embed.add_field(name="Votes", value="0", inline=True)
        embed.add_field(name="Genres", value=genre, inline=True)
        print(img)
        embed.set_thumbnail(url=img) #set_image
        msg = await message.channel.send(embed=embed)

        self.bot.var[message.guild.id]['anime_msg'][aid] = msg
        self.bot.var[message.guild.id]['anime'][aid] = vid

    def getvid(self, link):
        if not link.startswith("http"):
            link = "http:" + link
            return link
        return link

    async def repostList(self, message, votes):
        for idx, anime in self.bot.var[message.guild.id]['anime_msg'].items():
            #await anime.delete()
            embed = anime.embeds[0]
            embed.remove_field(1)
            embed.insert_field_at(1, name="Votes", value=votes[idx], inline=True)
            await anime.edit(embed=embed)

    def reset(self, guild):
        self.bot.var[guild]['vote'] = 0 #ammount of votes needed to auto end vote
        self.bot.var[guild]['voted'] = {} #vote of each user with user as key and id of show as value
        self.bot.var[guild]['anime'] = {} #video sources for each show
        self.bot.var[guild]['anime_msg'] = {} #discord message with embeds for each show

    @commands.command()
    async def Ranime(self, ctx, num: Optional[int] = 1, votes: Optional[int] = 0):
        '''start, arguments: number(ammont of anime), number(ammount of votes)'''
        if self.bot.var[ctx.message.guild.id]['vote'] > 0:
            await ctx.send("please finish the current vote before starting a new one")
            return
        if num > 1 and votes == 0:
            votes = 1
        self.reset(ctx.message.guild.id)
        #await asyncio.gather(*[self.random(i, ctx) for i in range(0, num)])
        for i in range(0, num):
            await self.random(i, ctx.message)
        self.bot.var[ctx.message.guild.id]['vote'] = votes
        if votes == 0:
            await self.endvote(ctx)

    @commands.command()
    async def ranime(self, ctx):
        '''starts a random anime vote with n anime and 5 votes with n being the nubmer of people in the posters voice channel'''
        if ctx.author.voice != None:
            l = len(ctx.author.voice.channel.members)
            await self.Ranime(ctx, l, l)

    @commands.command()
    async def rtanime(self, ctx, time: Optional[int] = 100):
        '''same as ranime, but will end after 100 seconds, or the given time'''
        if ctx.author.voice != None:
            l = len(ctx.author.voice.channel.members)
            await self.Ranime(ctx, l, l)
        m = await ctx.send("vote ends in 100 sec")
        await asyncio.sleep(time)
        await self.end(ctx.message)
        await m.delete()


    @commands.command()
    async def vote(self, ctx, num: Optional[int] = 0):
        """vote for a series, argument: number(series id)"""
        await self.vote_anime(ctx.message, ctx.message.author.id, num)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not reaction.message.author.bot:
            return
        guild = reaction.message.guild.id
        num = [x for x, a in self.bot.var[guild]['anime_msg'].items() if a.id == reaction.message.id]
        if len(num) <= 0:
            return
        num = num[0]
        if reaction.emoji == "👎":
            await self.roll(reaction.message, num)
        await self.vote_anime(reaction.message, user.id, num)

    async def vote_anime(self, message, author, num):
        guild = message.guild.id
        if self.bot.var[guild]['vote'] == 0:
            return
        self.bot.var[guild]['voted'][author] = num
        ct = Counter(self.bot.var[guild]['voted'].values())
        await self.repostList(message, ct)
        if len(self.bot.var[guild]['voted']) >= self.bot.var[guild]['vote'] or \
                list(Counter(self.bot.var[guild]['voted'].values()))[0] > self.bot.var[guild]['vote'] / 2:
            await self.end(message)

    async def end(self, message):
        guild = message.guild.id
        if len(self.bot.var[guild]['anime_msg']) <= 0:
            return
        if len(list(Counter(self.bot.var[guild]['voted'].values()))) > 0:
            aid = list(Counter(self.bot.var[guild]['voted'].values()))[0]
        else:
            aid = random.choice(list(self.bot.var[guild]['anime'].keys()))
        embed = self.bot.var[guild]['anime_msg'][aid].embeds[0]
        embed.colour = 0x5cd65c
        embed.clear_fields()

        link = self.bot.var[guild]['anime'][aid]
        data = requests.get(link)
        sel = CSSSelector("a")
        sources = sel(lxml.html.fromstring(data.content).find_class("anime_muti_link")[0])
        for it, r in enumerate(sources):
            embed.add_field(name="stream {}".format(it + 1), value=self.getvid(r.get("data-video")), inline=False)

        await message.channel.send(embed=embed)
        self.reset(guild)

    async def roll(self, message, num):
        try:
            await self.bot.var[message.guild.id]['anime_msg'][num].delete()
        except:
            await message.channel.send("given id might be wrong")
        await self.random(num, message)

    @commands.command()
    async def endvote(self, ctx):
        """ends a vote early"""
        await self.end(ctx.message)

    @commands.command()
    async def reroll(self, ctx, num: Optional[int] = -1):
        """replace id with a new random series, argument: number(series id)"""
        if num == -1:
            return;
        await self.roll(ctx.message, num)

    @vote.after_invoke
    @endvote.after_invoke
    @ranime.after_invoke
    @reroll.after_invoke
    @Ranime.after_invoke
    async def del_msg(self, ctx):
        await ctx.message.delete()
