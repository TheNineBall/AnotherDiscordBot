import discord

class React:
    def __init__(self):
        self.reacts = {}
        self.messages = []

    async def delete_all(self, ctx):
        for msg in self.messages:
            try:
                await msg.clear_reactions()
            except discord.NotFound:
                pass

    async def add(self, msg, emoji, func, delete=True, *args, **kwargs):
        if msg.id not in self.reacts:
            self.reacts[msg.id] = {}
        delete, remove = delete if type(delete) is tuple else (delete, False)
        self.reacts[msg.id][emoji] = (delete, remove, False, [func, *args, kwargs])
        self.messages.append(msg)
        await msg.add_reaction(emoji)

    async def add_new(self, msg, emoji, func, delete=True, react=False, *args, **kwargs):
        # TODO fix the old stuff, there really dont need to be 2 add methods
        if msg.id not in self.reacts:
            self.reacts[msg.id] = {}
        delete, remove = delete if type(delete) is tuple else (delete, False)
        self.reacts[msg.id][emoji] = (delete, remove, react, [func, *args, kwargs])
        self.messages.append(msg)
        await msg.add_reaction(emoji)

    async def check(self, reaction, user):
        if reaction.message.id in self.reacts:
            if reaction.emoji in self.reacts[reaction.message.id]:
                delete, remove, react, tmp = self.reacts[reaction.message.id][reaction.emoji]
                if len(tmp) == 1:
                    await tmp[0]() if not react else await tmp[0](user)
                if len(tmp) == 2:
                    await tmp[0](*tmp[1]) if not react else await tmp[0](user, *tmp[1])
                if len(tmp) == 3:
                    await tmp[0](*tmp[1], **tmp[2]) if not react else await tmp[0](user, *tmp[1], **tmp[2])
                if remove:
                    await reaction.message.clear_reaction(reaction.emoji)
                    return False
                return delete
        return False
