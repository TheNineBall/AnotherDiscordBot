import sqlalchemy as sa
from databases import Database
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Word(Base):
    __tablename__ = 'Word'
    id = sa.Column(sa.Integer, primary_key=True)
    word = sa.Column(sa.String(length=100), unique=True)
    guild = sa.Column(sa.String(length=50))
    channel = sa.Column(sa.String(length=50))


class Youtube(Base):
    __tablename__ = 'Youtube'
    id = sa.Column(sa.Integer, primary_key=True)
    vid_id = sa.Column(sa.String(length=50), unique=True)
    title = sa.Column(sa.String(length=50))
    guild = sa.Column(sa.String(length=50))
    channel = sa.Column(sa.String(length=50))


class Hashes(Base):
    __tablename__ = 'Hashes'
    id = sa.Column(sa.Integer, primary_key=True)
    hash = sa.Column(sa.String(length=50), unique=True)
    desc = sa.Column(sa.String(length=50))
    guild = sa.Column(sa.String(length=50))
    channel = sa.Column(sa.String(length=50))


class User(Base):
    __tablename__ = 'User'
    id = sa.Column(sa.Integer, primary_key=True, unique=True)
    rank = sa.Column(sa.Integer)
    exp = sa.Column(sa.Integer)
    guild = sa.Column(sa.String(length=50), primary_key=True, unique=False)


class Persistence(object):
    async def __aenter__(self):
        self.url = 'sqlite:///discord.db'
        self.engine = sa.create_engine(self.url)
        self.words = Word.__table__
        self.youtube = Youtube.__table__
        self.hashes = Hashes.__table__
        self.users = User.__table__
        Base.metadata.create_all(self.engine)
        self.database = Database(self.url)
        await self.database.connect()


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.database.disconnect()


    async def addw(self, word: str, guild: str, channel: str = ""):
        async with self.database.transaction():
            q = self.words.insert().values(word=word, guild=guild, channel=channel)
            await self.database.execute(q)
    async def delw(self, word: str, guild: str, channel: str = ""):
        async with self.database.transaction():
            q = self.words.delete().where(sa.and_(self.words.c.word == word, self.words.c.guild == guild,
                                          self.words.c.channel == channel))
            await self.database.execute(q)
    async def getw(self, guild: str, channel: str = ""):
        print(guild)
        print(channel)
        async with self.database.transaction():
            q = self.words.select().where(sa.and_(self.words.c.guild == guild, self.words.c.channel == channel))
            return await self.database.fetch_all(q)


    async def addy(self, vid_id: str, title: str, guild: str, channel: str = ""):
        async with self.database.transaction() as t:
            q = self.youtube.insert().values(vid_id = vid_id, title=title, guild=guild, channel=channel)
            await self.database.execute(q)
    async def dely(self, vid_id: str, guild: str, channel: str = ""):
        async with self.database.transaction():
            q = self.youtube.delete().where(sa.and_(self.youtube.c.vid_id == vid_id,self.youtube.c.guild == guild,
                                            self.youtube.c.channel == channel))
            await self.database.execute(q)
    async def gety(self, guild: str, channel: str = ""):
        async with self.database.transaction():
            q = self.youtube.select().where(sa.and_(self.youtube.c.guild == guild, self.youtube.c.channel == channel))
            return await self.database.fetch_all(q)


    async def addh(self, hash: str, guild: str, channel: str = "", desc: str = "/"):
        async with self.database.transaction():
            q = self.hashes.insert().values(hash=hash, desc=desc, guild=guild, channel=channel)
            await self.database.execute(q)
    async def delh(self, hash: str, guild: str, channel: str = ""):
        async with self.database.transaction():
            q = self.hashes.delete().where(sa.and_(self.hashes.c.hash == hash, self.hashes.c.guild == guild,
                                          self.hashes.c.channel == channel))
            await self.database.execute(q)
    async def geth(self, guild: str, channel: str = ""):
        async with self.database.transaction():
            q = self.hashes.select().where(sa.and_(self.hashes.c.guild == guild, self.hashes.c.channel == channel))
            return await self.database.fetch_all(q)


    async def addu(self, user: str, guild: str, exp: int = 0, level: int = -1):
        async with self.database.transaction():
            u = self.getu(user, guild)
            if len(u) > 0:
                q = self.users.update().values(rank=u['rank'] if level == -1 else level, exp=(int(u['exp']) + exp))
            else:
                q = self.users.insert().values(id=user, rank=0 if level == -1 else level, exp=exp, guild=guild)
            return await self.database.execute(q)
    async def delu(self, user: str, guild: str):
        async with self.database.transaction():
            q = self.users.delete().where(sa.and_(self.users.c.user == user, self.users.c.guild == guild))
            await self.database.execute(q)
    async def getu(self, user: str, guild: str):
        async with self.database.transaction():
            q = self.users.select().where(sa.and_(self.users.c.user == user,self.users.c.guild == guild))
            return await self.database.fetch_all(q)
    async def getau(self, guild: str):
        async with self.database.transaction():
            q = self.users.select().where(self.users.c.guild == guild)
            return await self.database.fetch_all(q)