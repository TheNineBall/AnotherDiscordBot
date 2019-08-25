import random
from discord.ext import commands


class Various(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(ctx, dice: str = ""):
        """rolls a ndn dice"""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            return
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)