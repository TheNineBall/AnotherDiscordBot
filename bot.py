import discord
import json
from cogs.cat import Cat
from cogs.image import Image
from cogs.various import Various


from discord.ext import commands

with open('auth.json') as jf:
    data = json.loads(jf.read())
    TOKEN = data['token']
    YTAPI = data['key']

bot = commands.Bot(command_prefix='?', description="description")

@bot.event
async def on_ready():
    print("rdy")

bot.add_cog(Cat(bot))
bot.add_cog(Image(bot))
bot.add_cog(Various(bot))
bot.run(TOKEN)
