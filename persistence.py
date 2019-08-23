from databases import Database
from os.path import isfile


class DB(object):

    async def init(self):
        self.database = Database('sqlite:///discord.db')
        if not isfile("discord.db"):
            await self.database.connect()
            query = """CREATE TABLE Words (id INTEGER PRIMARY KEY, word VARCHAR(100) UNIQUE)"""
            await self.database.execute(query=query)
            query = """CREATE TABLE Links (id INTEGER PRIMARY KEY, ytid VARCHAR(100) UNIQUE, title VARCHAR(100))"""
            await self.database.execute(query=query)
            query = """CREATE TABLE Hashes (id INTEGER PRIMARY KEY, hash VARCHAR(100) UNIQUE, desc VARCHAR(100))"""
            await self.database.execute(query=query)
            query = """CREATE TABLE Users (id INTEGER PRIMARY KEY, user VARCHAR(100) UNIQUE, rank INT, exp INT)"""
            await self.database.execute(query=query)


    async def addWord(self, word: str):
        query = """INSERT INTO Words(word) VALUES (:word)"""
        await self.database.execute(query=query, values={"word": word})
    async def deleteWord(self, word: str):
        query = """DELETE FROM Words WHERE word = (:word)"""
        await self.database.execute(query=query, values={"word": word})
    async def getWords(self):
        query = """SELECT * FROM Words"""
        return await self.database.fetch_all(query=query)


    async def addYt(self, ytid: str, title: str):
        query = """INSERT INTO Links(ytid,title) VALUES (:ytid,:title)"""
        await self.database.execute(query=query, values={"ytid": ytid, "title": title})
    async def deleteYt(self, ytid: str):
        query = """DELETE FROM Links WHERE ytid = (:ytid)"""
        await self.database.execute(query=query, values={"ytid": hash})
    async def getYt(self):
        query = """SELECT * FROM Links"""
        return await self.database.fetch_all(query=query)


    async def addHash(self, hash: str, desc: str):
        query = """INSERT INTO Hashes(hash,desc) VALUES (:hash,:desc)"""
        await self.database.execute(query=query, values={"hash": hash, "desc": desc})
    async def deleteHash(self, hash: str):
        query = """DELETE FROM Hashes WHERE hash = (:hash)"""
        await self.database.execute(query=query, values={"word": hash})
    async def getHashes(self):
        query = """SELECT * FROM Hashes"""
        return await self.database.fetch_all(query=query)


    async def addUser(self, user: str, level: int):
        query = """INSERT INTO Users(user,level) VALUES (:user,:level)"""
        await self.database.execute(query=query, values={"user": user, "level": level})
    async def deleteUser(self, user: str):
        query = """DELETE FROM Users WHERE user = (:user)"""
        await self.database.execute(query=query, values={"user": user})
    async def getUsers(self):
        query = """SELECT * FROM Users"""
        return await self.database.fetch_all(query=query)

