import discord
import json
import utility
from cogs.cat import Cat
from cogs.image import Image
#from cogs.filter import Filter
from cogs.various import Various
#from persistence import Persistence
from discord.ext import commands
from cogs.audio import Audio

bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"), description="Another random discord bot")

with open('auth.json') as jf:
    data = json.loads(jf.read())
    bot.key_dis = data['discord']
    bot.key_yt = data['youtube']
    bot.key_azur = data['azure']
bot.resources = "resources/"
bot.get_images = utility.get_images
#bot.db = Persistence()

@bot.event
async def on_ready():
    print("rdy")

bot.add_cog(Cat(bot))
bot.add_cog(Image(bot))
#bot.add_cog(Filter(bot))
bot.add_cog(Various(bot))
bot.add_cog(Audio(bot))
bot.run(bot.key_dis)

