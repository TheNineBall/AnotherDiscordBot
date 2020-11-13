import discord

class React():
    def __init__(self):
        self.reacts = {}

    async def add(self, msg, emoji, func, *args):
        if msg.id not in self.reacts:
            self.reacts[msg.id] = {}
        self.reacts[msg.id][emoji] = [func, *args]
        await msg.add_reaction(emoji)

    async def check(self, reaction):
        if reaction.message.id in self.reacts:
            if reaction.emoji in self.reacts[reaction.message.id]:
                tmp = self.reacts[reaction.message.id][reaction.emoji]
                await tmp[0](*tmp[1])
                return True
        return False

#self.bot.var['react'][msg.id] = {'➕': self.gogoepisodes}
#await msg.add_reaction('➕')

#if reaction.emoji in bot.var['react'][reaction.message.id]:
#    await bot.var['react'][reaction.message.id][reaction.emoji](reaction.message, None, 1)