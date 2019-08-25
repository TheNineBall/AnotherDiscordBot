import discord
import json
from cogs.cat import Cat
from cogs.image import Image
from cogs.various import Various
from discord.ext import commands


bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"), description="Another random discord bot")

with open('auth.json') as jf:
    data = json.loads(jf.read())
    bot.key_dis = data['discord']
    bot.key_yt = data['youtube']
    bot.key_azur = data['azure']
bot.resources = "resources/"

@bot.event
async def on_ready():
    print("rdy")

bot.add_cog(Cat(bot))
bot.add_cog(Image(bot))
bot.add_cog(Various(bot))
bot.run(bot.key_dis)
