import discord
from abc import ABC
from abc import abstractmethod


class Anime(ABC):
    def __init__(self, site_name):
        self.site_name = site_name
        self.reset()
        self.url = ""
        self.message = None
        self.episode = 1

    def reset(self):
        self.messages = {}
        self.vote = 0
        self.voted = {}
        self.anime = {}

    def embed_vote(self, aid, title, url, genres, thumbnail):
        embed = discord.Embed(title=title, description=url, color=0x36393f) #eee657
        embed.add_field(name="ID", value=aid, inline=True)
        embed.add_field(name="Votes", value="0", inline=True)
        embed.add_field(name="Genres", value=genres, inline=True)
        embed.set_thumbnail(url=thumbnail) #set_image
        return embed

    def embed_watch(self, title, thumbnail):
        if self.message is None:
            embed = discord.Embed(title=title, description=self.url, color=0x5cd65c)
            embed.set_thumbnail(url=thumbnail)  # set_image
        else:
            embed = self.message.embeds[0] #.bot.var[guild]['gogo-msg'].embeds[0]
            embed.clear_fields()
            embed.title = title
            embed.color = 0x5cd65c
        for it, r in enumerate(self.sources):
            if not (link := r.get("data-video")).startswith("http"):
                link = "https:" + link
            embed.add_field(name="stream {}".format(it + 1), value=link, inline=False)
        return embed

    @abstractmethod
    def get_ep(self, id):
        raise NotImplementedError
