import discord
import json
import utility
import asyncio
from utils.config import config
from utils.react import React
from cogs.anime import Anime
from cogs.cat import Cat
from cogs.image import Image
from cogs.various import Various
from discord.ext import commands
from cogs.audio import Audio

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config.BOT_PREFIX),
                   description="Another random discord bot")


@bot.event
async def on_reminder(channel_id, author_id, text):
    channel = bot.get_channel(channel_id)
    await channel.send("<@{0}>, remember: {1}".format(author_id, text))


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id or payload.message_id in bot.react.reacts:
        return
    for c in bot.cogs:
        if (r_handler := getattr(bot.cogs[c], "handle_reactions", None)) is not None:
            await r_handler(payload)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if await bot.react.check(reaction, user):
        try:
            await reaction.remove(user)
        except discord.NotFound:
            pass


@bot.event
async def on_guild_join(guild):
    for c in bot.cogs:
        if (setup := getattr(bot.cogs[c], "setup", None)) is not None:
            setup(guild)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(name="prefix: \"{}\"".format(config.BOT_PREFIX)))
    for g in bot.guilds:
        if not g.id in bot.var:
            bot.var[g.id] = {}
        for c in bot.cogs:
            if (setup := getattr(bot.cogs[c], "setup", None)) is not None:
                setup(g)
    print("rdy")


with open('auth.json') as jf:
    data = json.loads(jf.read())
    bot.key_dis = data['discord']
    bot.key_yt = data['youtube']
    bot.key_azure = data['azure']
bot.resources = "resources/"
bot.get_images = utility.get_images
bot.var = {}
bot.react = React()
bot.config = config

bot.add_cog(Cat(bot))
bot.add_cog(Image(bot))
bot.add_cog(Various(bot))
bot.add_cog(Audio(bot))
bot.add_cog(Anime(bot))
#bot.add_cog(Timer(bot))


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.start(bot.key_dis))
except KeyboardInterrupt:
    loop.run_until_complete(bot.react.delete_all(bot))
    loop.run_until_complete(bot.close())
finally:
    loop.close()
