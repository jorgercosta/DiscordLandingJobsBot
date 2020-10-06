import os
import discord
import requests
from time import sleep

from dotenv import load_dotenv, set_key

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHANNELID = int(os.getenv('CHANNELID'))
TAGS = os.getenv('TAGS').split(',')
URL = os.getenv('URL')
LASTPUBLISHEDID = int(os.getenv('LASTPUBLISHEDID'))
FETCHINTERVAL = int(os.getenv('FETCHINTERVAL'))


class DiscordClient(discord.Client):
    token = ""
    channel_id = 0
    tags = []
    url = ""
    last_published_id = 0
    fetch_interval = 0

    def __init__(self, token: str, channel_id: int, tags: list, url: str, last_published_id: int, fetch_interval: int):
        super().__init__()
        self.token = token
        self.channel_id = channel_id
        self.tags = tags
        self.url = url
        self.last_published_id = last_published_id
        self.fetch_interval = fetch_interval

    async def on_ready(self):
        print('Hello i\'am Bot for Landing Jobs', self.user)
        while True:
            jobs = Jobs(self.url, self.tags, self.last_published_id)
            #print('Found new ' + str(len(jobs)) + 'jobs!')
            for job in jobs.get():
                print('Sending message for job id:' + str(job['id']))
                await self.sendMessage(job)
                if job['id'] > self.last_published_id:
                    self.last_published_id = job['id']
                    self.__persistLastPublishedId(self.last_published_id)
            sleep(self.fetch_interval)

    async def sendMessage(self, job: dict):
        channel = self.get_channel(self.channel_id)
        await channel.send(job['url'])

    def __persistLastPublishedId(self, id: int):
        print('Persinting LASTPUBLISHEDID==' + str(id))
        set_key(os.path.join(os.path.dirname(os.path.realpath(
            __file__)), '.env'), 'LASTPUBLISHEDID', str(id))


class Jobs():
    tags = []
    url = ""
    last_published_id = 0

    def __init__(self, url: str, tags: list, last_published_id: int):
        self.tags = tags
        self.url = url
        self.last_published_id = last_published_id

    def get(self) -> list:
        limit = 50
        offset = 0
        results = []
        for offset in range(0, 1000, limit):
            url = self.url + '?limit=' + str(limit) + '&offset=' + str(offset)
            print(url)
            r = requests.get(url)
            t = r.json()
            if len(r.json()) == 0:
                break
            results = results+r.json()

        results = list(
            filter(lambda j: self.__filterByTags(j['tags']), results))
        results = list(
            filter(lambda j: self.__filterUnPublished(j['id']), results))
        return results

    def __filterByTags(self, tags: list) -> bool:
        for tag in self.tags:
            if (tag in tags):
                return True
        return False

    def __filterUnPublished(self, id: int) -> bool:
        return id > self.last_published_id


client = DiscordClient(TOKEN, CHANNELID, TAGS, URL,
                       LASTPUBLISHEDID, FETCHINTERVAL)
client.run(TOKEN)

exit
