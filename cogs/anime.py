import asyncio
import random
import json
from typing import Optional
from collections import Counter
from discord.ext import commands
from utils.anime import gogoanime


class Anime(commands.Cog):
    """Vote on random Anime links"""

    def __init__(self, bot):
        self.bot = bot
        self.backend = gogoanime.GogoAnime

    def setup(self, guild):
        self.bot.var[guild.id]['anime'] = self.backend()

    async def random(self, aid, message):
         msg = await message.channel.send(embed=self.bot.var[message.guild.id]['anime'].get_random(aid))
         self.bot.var[message.guild.id]['anime'].messages[aid] = msg

    async def repostList(self, message, votes):
        for idx, anime in self.bot.var[message.guild.id]['anime'].messages.items():
            #await anime.delete()
            embed = anime.embeds[0]
            embed.remove_field(1)
            embed.insert_field_at(1, name="Votes", value=votes[idx], inline=True)
            await anime.edit(embed=embed)

    def reset(self, guild):
        self.bot.var[guild]['anime'].reset()

    async def get_episode(self, message, url, ep, abs=True):
        ep = ep
        try:
            if url is not None:
                self.bot.var[message.guild.id]['anime'].episode = ep
                self.bot.var[message.guild.id]['anime'].url = url
                self.bot.var[message.guild.id]['anime'].message = None
                embed = self.bot.var[message.guild.id]['anime'].get_ep(ep)
                msg = await message.channel.send(embed=embed)
                self.bot.var[message.guild.id]['anime'].message = msg
            else:
                self.bot.var[message.guild.id]['anime'].episode = \
                    self.bot.var[message.guild.id]['anime'].episode + ep if abs else ep
                msg = self.bot.var[message.guild.id]['anime'].message
                embed = self.bot.var[message.guild.id]['anime'].get_ep(ep)
                if embed is not None:
                    await msg.edit(embed=embed)
            await self.bot.react.add(msg, '➖', self.get_episode, True, (msg, None, ep - 1, False))
            await self.bot.react.add(msg, '➕', self.get_episode, True, (msg, None, ep + 1, False))
        except:
            await message.channel.send("Error during \"get_episode()\"")

    @commands.command()
    async def anime(self, ctx, ep: Optional[int] = 1, url: Optional[str] = None):
        '''get stream-links from an url'''
        await self.get_episode(ctx.message, url, ep)


    @commands.has_permissions(administrator=True)
    @commands.command()
    async def Ranime(self, ctx, num: Optional[int] = 1, votes: Optional[int] = 0):
        '''custom amount of anime and votes'''
        if self.bot.var[ctx.message.guild.id]['anime'].vote > 0:
            await ctx.send("please finish the current vote before starting a new one")
            return
        if num > 1 and votes == 0:
            votes = 1
        self.reset(ctx.message.guild.id)
        #await asyncio.gather(*[self.random(i, ctx) for i in range(0, num)])
        for i in range(0, num):
            await self.random(i, ctx.message)
        self.bot.var[ctx.message.guild.id]['anime'].vote = votes
        if votes == 0:
            await self.endvote(ctx)

    @commands.command()
    async def ranime(self, ctx):
        '''starts random anime vote depending on people in current voice channel'''
        if ctx.author.voice == None or self.bot.var[ctx.message.guild.id]['anime'].vote == 0:
            return
        l = len(ctx.author.voice.channel.members)
        await self.Ranime(ctx, l, l)

    @commands.command()
    async def rtanime(self, ctx, time: Optional[int] = 10):
        '''same as ranime, but will end after 100 seconds, or the given time'''
        if ctx.author.voice == None or self.bot.var[ctx.message.guild.id]['anime'].vote == 0:
            return
        l = len(ctx.author.voice.channel.members)
        await self.Ranime(ctx, l, l)
        dic = json.dumps(self.bot.var[ctx.message.guild.id]['anime'].anime, sort_keys=True)
        m = await ctx.send("vote ends in {} sec".format(time))
        await asyncio.sleep(time)
        if dic == json.dumps(self.bot.var[ctx.message.guild.id]['anime'].anime, sort_keys=True):
            await self.end(ctx.message)
        await m.delete()


    @commands.command()
    async def vote(self, ctx, num: Optional[int] = 0):
        """vote for given id"""
        await self.vote_anime(ctx.message, ctx.message.author.id, num)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not reaction.message.author.bot:
            return
        guild = reaction.message.guild.id
        num = [x for x, a in self.bot.var[guild]['anime'].messages.items() if a.id == reaction.message.id]
        if len(num) <= 0:
            return
        num = num[0]
        if reaction.emoji == "👎":
            await self.roll(reaction.message, num)
            return
        await self.vote_anime(reaction.message, user.id, num)

    async def vote_anime(self, message, author, num):
        guild = message.guild.id
        if self.bot.var[guild]['anime'].vote == 0:
            return
        self.bot.var[guild]['anime'].voted[author] = num
        ct = Counter(self.bot.var[guild]['anime'].voted.values())
        await self.repostList(message, ct)
        if len(self.bot.var[guild]['anime'].voted) >= self.bot.var[guild]['anime'].vote or \
                list(Counter(self.bot.var[guild]['anime'].voted.values()))[0] > self.bot.var[guild]['anime'].vote / 2:
            await self.end(message)

    async def end(self, message):
        guild = message.guild.id
        if len(self.bot.var[guild]['anime'].messages) <= 0:
            return
        if len(list(Counter(self.bot.var[guild]['anime'].voted.values()))) > 0:
            aid = list(Counter(self.bot.var[guild]['anime'].voted.values()))[0]
        else:
            aid = random.choice(list(self.bot.var[guild]['anime'].anime.keys()))
        self.bot.var[message.guild.id]['anime'].episode = 0
        url = self.bot.var[guild]['anime'].anime[aid]
        self.bot.var[message.guild.id]['anime'].url = url
        self.bot.var[message.guild.id]['anime'].message = self.bot.var[guild]['anime'].messages[aid]
        await self.get_episode(message, url, self.bot.var[message.guild.id]['anime'].episode+1)
        self.reset(guild)

    async def roll(self, message, num):
        try:
            await self.bot.var[message.guild.id]['anime'].messages[num].delete()
        except:
            await message.channel.send("given id might be wrong")
        await self.random(num, message)

    @commands.command()
    async def endvote(self, ctx):
        """ends a vote early"""
        await self.end(ctx.message)

    @commands.command()
    async def reroll(self, ctx, num: Optional[int] = -1):
        """replace given id"""
        if num == -1:
            return
        await self.roll(ctx.message, num)

    async def cog_after_invoke(self, ctx):
        await ctx.message.delete()
