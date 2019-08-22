import discord
import cogs.cat
import json

from discord.ext import commands

with open('auth.json') as jf:
    data = json.loads(jf.read())
    TOKEN = data['token']
    YTAPI = data['key']

bot = commands.Bot(command_prefix='?', description="description")

bot.add_cog(cogs.cat.Cat(bot))
bot.run(TOKEN)
