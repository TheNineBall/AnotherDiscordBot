import discord
import json
import utility
import asyncio
from cogs.cat import Cat
from cogs.image import Image
from cogs.filter import Filter
from cogs.various import Various
from persistence import Persistence
from discord.ext import commands
from cogs.audio import Audio
from cogs.anime import Anime
from cogs.timer import Timer

async def main():
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"), description="Another random discord bot")
    with open('auth.json') as jf:
        data = json.loads(jf.read())
        bot.key_dis = data['discord']
        bot.key_yt = data['youtube']
        bot.key_azure = data['azure']
    bot.resources = "resources/"
    bot.get_images = utility.get_images
    bot.db = Persistence()
    bot.var = {}

    @bot.event
    async def on_reminder(channel_id, author_id, text):
        channel = bot.get_channel(channel_id)
        await channel.send("<@{0}>, remember: {1}".format(author_id, text))

    @bot.event
    async def on_ready():
        for g in bot.guilds:
            if not g.id in bot.var:
                bot.var[g.id] = {}
                bot.var[g.id]['vote'] = 0
                bot.var[g.id]['voted'] = {}
                bot.var[g.id]['anime'] = {}
                bot.var[g.id]['anime_msg'] = {}
        print("rdy")

    bot.add_cog(Cat(bot))
    bot.add_cog(Image(bot))
    bot.add_cog(Filter(bot))
    bot.add_cog(Various(bot))
    bot.add_cog(Audio(bot))
    bot.add_cog(Anime(bot))
    bot.add_cog(Timer(bot))

    try:
        await bot.start(bot.key_dis)
    except KeyboardInterrupt:
        await bot.db.close()
        await bot.logout()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
