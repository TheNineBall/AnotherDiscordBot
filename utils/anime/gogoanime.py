from utils.anime.Anime import Anime
from lxml.cssselect import CSSSelector
import random
import requests
import asyncio
import lxml.html

URL = "https://gogoanime.tv"


class GogoAnime(Anime):

    def __init__(self):
        super().__init__('gogoanime')

    def get_random(self, aid):
        l = URL + "/anime-list.html?page={}".format(random.randint(0, 54))
        data = requests.get(l)
        sel = CSSSelector("a")
        vids = sel(lxml.html.fromstring(data.content).find_class("listing")[0])
        #vid = random.choice(vids).get("href").replace("/category", "") + "-episode-1"
        data = requests.get(URL + random.choice(vids).get("href"))
        url = data.url
        lx = lxml.html.fromstring(data.content)
        title = lx.findtext('.//title').replace("at Gogoanime", "")
        genre = ""
        genres = sel(lx.find_class("anime_info_body_bg")[0])
        for g in genres[2:]:
            genre = genre + g.text_content()
        genres = genres
        im = CSSSelector("img")
        thumbnail = im(lx.find_class("anime_info_body_bg")[0])[0].get('src').replace(" ", "%20")
        # vid = url.replace("/category", "") + "-episode-1"
        self.anime[aid] = url
        return self.embed_vote(aid, title, url, genres, thumbnail)

    def get_ep(self, episode):
        data = requests.get(self.url)
        lx = lxml.html.fromstring(data.content)
        title = lx.findtext('.//title').replace("at Gogoanime", "") + " - Episode: {}".format(self.episode)
        vid = self.url.replace("/category", "") + "-episode-{}".format(self.episode)
        im = CSSSelector("img")
        thumbnail = im(lx.find_class("anime_info_body_bg")[0])[0].get('src').replace(" ", "%20")
        data = requests.get(vid)
        sel = CSSSelector("a")
        try:
            self.sources = sel(lxml.html.fromstring(data.content).find_class("anime_muti_link")[0])
        except IndexError:
            return None
        #self.anime[id] = vid
        return self.embed_watch(title, thumbnail)

