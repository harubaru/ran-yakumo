import time
import parse
import discord
import re
import asyncio
import random

from ratelimiter import AsyncRateLimiter
from util import Util
from discord import Embed
from discord import Colour
from discord import channel

# Import the pipelines
from pipeline import ConversationalPipeline
from pipeline import TranslationPipeline
from pipeline import QnAPipeline
from pipeline import DictionaryPipeline
from pipeline import DanbooruPipeline
from pipeline import YoutubePipeline
from pipeline import WikipediaPipeline

class Client():
    def __init__(self, util, keys=None):
        self.util = util
        self.client = discord.Client()
        self.token = keys["discord_token"]
        self.conv_pipeline = ConversationalPipeline(self.util, keys)
        self.tl_pipeline = TranslationPipeline(self.util, keys)
        self.qna_pipeline = QnAPipeline(self.util, keys)
        self.dict_pipeline = DictionaryPipeline(self.util, keys)
        self.db_pipeline = DanbooruPipeline(self.util, keys)
        self.yt_pipeline = YoutubePipeline(self.util, keys)
        self.wiki_pipeline = WikipediaPipeline(self.util, keys)
        self.last_message = None
        self.until = None
        self.rate_limited = False
        # Limit generation to 6 messages per minute.
        self.rate_limiter = AsyncRateLimiter(max_calls=3, period=5, callback=self.limited)
        self.last = 2

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
        if self.client.user.mentioned_in(message):
            if message.author.id == self.client.user.id:
                return
            await asyncio.sleep(random.uniform(1.5, 8.0))
            async with message.channel.typing():
                msg = ''
                messages = await message.channel.history(limit=80).flatten()
                for i in reversed(messages):
                    content = re.sub(r'\<[^>]*\>', '', f'{i.content}')
                    if content == '':
                        continue
                    msg += f'{i.author.name}: {content}\n'
            await message.channel.send(self.conv_pipeline.generate(msg))
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
    
    async def send_embed(self, title, message, messageobj):
        embed = discord.Embed(title=title, description=message, colour=0xf1ab37)
        await messageobj.reply(embed=embed)

    async def help(self, message):
        command_dict = {
            'tl': 'Translate text from one language to another.\nUsage: ``r!tl [from] [to] [text]``',
            'dan': 'Danbooru search.\nUsage: ``r!dan [tags]``',
            'yt': 'Search YouTube for videos.\nUsage: ``r!yt [search]``',
            'wiki': 'Search Wikipedia for a page.\nUsage: ``r!wiki [search]``',
            'q': 'Ask a question.\nUsage: ``r!q [question]``',
            'def': 'Look up a word in the dictionary.\nUsage: ``r!def [word]``',
        }
        msg = "**Ran Yakumo Bot**\nVersion: ``0.1.1``\nGithub repo: [**Come contribute!**](https://github.com/harubaru/ran-yakumo)\n\nCommands:"
        for key, value in command_dict.items():
            msg += '\n**{0}** - {1}\n'.format(key, value)
        
        await self.send_embed(title='Help', message=msg, messageobj=message)
        
    async def message_handler(self, message):
        await message.channel.trigger_typing()
        try:
            if message.content.startswith('r!t'):
                msg = parse.parse('r!tl {0} {1} {2}', message.content.replace('\n', ''))
                from_lang = msg[0]
                to_lang = msg[1]
                text = msg[2]
                await message.reply(self.tl_pipeline.generate(text, from_lang, to_lang))
            
            # danbooru
            if message.content.startswith('r!dan'):
                await self.rate_limiter.pop_call()
                msg = parse.parse('r!dan {0}', message.content.replace('\n', ''))
                await message.reply(embed=self.db_pipeline.generate(msg[0], message.channel.is_nsfw(), message.author))
            
            if message.content.startswith('r!yt'):
                msg = parse.parse('r!yt {0}', message.content)
                await message.reply(self.yt_pipeline.generate(msg[0]))

            if message.content.startswith('r!wiki'):
                await self.rate_limiter.pop_call()
                msg = parse.parse('r!wiki {0}', message.content)
                await message.reply(self.wiki_pipeline.generate(msg[0]))
            
            if message.content.startswith('r!q'):
                msg = parse.parse('r!q {0}', message.content)
                await message.reply(embed=self.qna_pipeline.generate(msg[0], message.author))
            
            if message.content.startswith('r!def'):
                msg = parse.parse('r!def {0}', message.content)
                await message.reply(embed=self.dict_pipeline.generate(msg[0], message.author))

            if message.content.startswith('r!help'):
                await self.rate_limiter.pop_call()
                await self.help(message)
        except Exception as e:
            if message:
                embed = Embed(title='Error!', description=f'``{e}``')
                embed.set_footer(text=message.author.name + '#' + message.author.discriminator, icon_url=message.author.avatar_url)
                await message.reply(embed=embed)
