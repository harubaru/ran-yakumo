import time
import parse
import discord

from ratelimiter import AsyncRateLimiter
from util import Util
from discord import Embed
from discord import Colour
from discord import channel

# Import the pipelines
from pipeline import TranslationPipeline
from pipeline import QnAPipeline
from pipeline import DanbooruPipeline
from pipeline import YoutubePipeline
from pipeline import WikipediaPipeline

class Client():
    def __init__(self, util, keys=None):
        self.util = util
        self.client = discord.Client()
        self.token = keys["discord_token"]
        self.tl_pipeline = TranslationPipeline(self.util, keys)
        self.qna_pipeline = QnAPipeline(self.util, keys)
        self.db_pipeline = DanbooruPipeline(self.util, keys)
        self.yt_pipeline = YoutubePipeline(self.util, keys)
        self.wiki_pipeline = WikipediaPipeline(self.util, keys)
        self.last_message = None
        self.until = None
        self.rate_limited = False
        # Limit generation to 6 messages per minute.
        self.rate_limiter = AsyncRateLimiter(max_calls=3, period=5, callback=self.limited)

    def log(self, message):
        if self.util is not None:
            self.util.log(self.__class__.__name__, message)
    
    async def limited(self, until):
        duration = int(round(until - time.time()))
        self.until = until
        self.rate_limited = True
        await self.last_message.channel.send('Please wait for {0} seconds to use this command again.'.format(duration))

    def run(self):
        self.log('Starting Discord Client')
        # Setup events
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)
        self.client.run(self.token)
    
    async def on_ready(self):
        self.log('Connected to Discord Servers.')
    
    async def on_message(self, message):
        if not message.content.startswith('r!'):
            return
        
        self.last_message = message
        
        # Check if rate limited, if so, return
        if self.until != None:
            if self.until > time.time():
                duration = int(round(self.until - time.time()))
                await message.channel.send('Please wait for {0} seconds to use this command again.'.format(duration))
                return
        
        async with self.rate_limiter:
            if self.rate_limited:
                self.rate_limited = False
                await self.rate_limiter.pop_call()
                return
            else:
                await self.message_handler(message)
    
    async def send_embed(self, title, message, channel):
        embed = discord.Embed(title=title, description=message, colour=0xf1ab37)
        await channel.send(embed=embed)

    async def help(self, message):
        command_dict = {
            'tl': 'Translate text from one language to another.\nUsage: ``r!tl [from] [to] [text]``',
            'd': 'Danbooru search.\nUsage: ``r!d [tags]``',
            'yt': 'Search YouTube for videos.\nUsage: ``r!yt [search]``',
            'wiki': 'Search Wikipedia for a page.\nUsage: ``r!wiki [search]``',
            'q': 'Ask a question.\nUsage: ``r!q [question]``',
        }
        msg = "**Ran Yakumo Bot**\nVersion: ``0.1.0``\nGithub repo: [**Come contribute!**](https://github.com/harubaru/ran-yakumo)\n\nCommands:"
        for key, value in command_dict.items():
            msg += '\n**{0}** - {1}\n'.format(key, value)
        
        await self.send_embed(title='Help', message=msg, channel=message.channel)
        
    async def message_handler(self, message):
        if message.content.startswith('r!t'):
            msg = parse.parse('r!tl {0} {1} {2}', message.content.replace('\n', ''))
            from_lang = msg[0]
            to_lang = msg[1]
            text = msg[2]
            await message.channel.send(self.tl_pipeline.generate(text, from_lang, to_lang))
        
        # danbooru
        if message.content.startswith('r!d'):
            await self.rate_limiter.pop_call()
            print(message.content)
            msg = parse.parse('r!d {0}', message.content.replace('\n', '').replace('\\', ''))
            print(msg)
            await message.channel.send(self.db_pipeline.generate(msg[0], message.channel.is_nsfw()))
        
        if message.content.startswith('r!yt'):
            msg = parse.parse('r!yt {0}', message.content)
            await message.channel.send(self.yt_pipeline.generate(msg[0]))

        if message.content.startswith('r!wiki'):
            await self.rate_limiter.pop_call()
            msg = parse.parse('r!wiki {0}', message.content)
            await message.channel.send(self.wiki_pipeline.generate(msg[0]))
        
        if message.content.startswith('r!q'):
            await message.channel.send("This has been disabled.")
        
        if message.content.startswith('r!help'):
            await self.rate_limiter.pop_call()
            await self.help(message)
