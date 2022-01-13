# Discord message pipeline
# Takes in message, parses it, and returns response.

import discord

embed_color = discord.Colour.from_rgb(215,195,134)

class Pipeline():
    def __init__(self, util=None, keys=None):
        self.util = util
        self.keys = keys
    
    def log(self, message):
        if self.util:
            self.util.log(self.__class__.__name__, message)
    
    def generate(self, message):
        return message

import wikipedia
from youtube_search import YoutubeSearch

class WikipediaPipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.log("Pipeline Initialized.")
    
    def generate(self, message):
        if not message:
            return "Please specify a search term."
        
        try:
            result_terms = wikipedia.search(message, results='5')
        except wikipedia.exceptions.DisambiguationError as e:
            result_terms = e.options
            result_terms.pop(0)
        
        if not result_terms:
            return "No results found."
        
        try:
            article = wikipedia.page(title=result_terms[0], auto_suggest=False)
            return article.url
        except wikipedia.exceptions.PageError:
            return "No results found."

class YoutubePipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.log("Pipeline Initialized.")

    def generate(self, message):
        if not message:
            return "Please specify a search term."
        
        results = YoutubeSearch(message, max_results=1)
        if not results:
            return 'Could not find YouTube video.'
        
        return 'https://www.youtube.com' + results.videos[1]['url_suffix']

from pybooru import Danbooru

# returns an embed
# Message pipeline for Danbooru images.
class DanbooruPipeline(Pipeline):

    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.nsfw_client = Danbooru('danbooru', username=keys["danbooru_username"], api_key=keys["danbooru_token"])
        self.sfw_client = Danbooru('safebooru', username=keys["danbooru_username"], api_key=keys["danbooru_token"])
        self.log("Pipeline Initialized.")

    def generate(self, message, nsfw, author):
        embed = discord.Embed()
        embed.set_footer(text=author.name + '#' + author.discriminator, icon_url=author.avatar_url)
        embed.colour = embed_color

        if not message:
            embed.title = 'Error'
            embed.description = 'Please input a search term!'
            return embed
        
        if nsfw:
            output = self.nsfw_client.post_list(tags=message, limit=1, random=True)
        else:
            output = self.sfw_client.post_list(tags=message, limit=1, random=True)
        if not output:
            embed.title = 'Error'
            embed.description = 'Post not found.'
            return embed
        
        embed.title = message

        try:
            embed.set_image(url=output['file_url'])
            embed.url = output['file_url']
            return embed
        except:
            try:
                embed.set_image(url=output[0]['file_url'])
                embed.url = output[0]['file_url']
                return embed
            except:
                embed.title = 'Error'
                embed.description = 'Post not found.'
                return embed


from gptj import GPTJGeneratorService

# Q&A Pipeline
class QnAPipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.model = GPTJGeneratorService(ip=keys["sukima_ip"], username=keys["sukima_username"], password=keys["sukima_password"])
        self.log("Pipeline Initialized.")
        self.prompt = "{author}: How does a telescope work?\nRan Yakumo: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n{author}: {question}\nRan Yakumo:"
    
    def generate(self, message, author):
        embed = discord.Embed()
        embed.set_footer(text=author.name + '#' + author.discriminator, icon_url=author.avatar_url)
        embed.colour = embed_color

        prompt_formatted = self.prompt.format(question=message, author=author.name)
        prompt_formatted = prompt_formatted[0:400] # 400 character limit
        response = self.model.sample_sequence_raw(prompt_formatted)
        embed.description = response
        
        return embed

# Dictionary Pipeline
class DictionaryPipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.model = GPTJGeneratorService(ip=keys["sukima_ip"], username=keys["sukima_username"], password=keys["sukima_password"])
        self.log("Pipeline Initialized.")
        self.prompt = "world - the earth, together with all of its countries, peoples, and natural features.\nbrain - an organ of soft nervous tissue having a grayish-white surface and a number of minute blood vessels, functioning as the center of the nervous system.\nlinker (programming) - a program that links the source code of a software program into a single executable file.\nintracranial hemorrhaging - the process of bleeding within the brain.\npresident - a person who presides over an organization, usually with the title of chairman.\nsenator - a person who is elected to represent a state in the U.S. Senate.\nvirtual machine - a computer program that emulates the behavior of a real machine.\nhole - a small opening or cavity.\n{term} -"

    def generate(self, message, author):
        embed = discord.Embed()
        embed.set_footer(text=author.name + '#' + author.discriminator, icon_url=author.avatar_url)
        embed.colour = embed_color

        prompt_formatted = self.prompt.format(term=message)
        response = self.model.sample_sequence_raw(prompt_formatted)
        embed.description = response

        return embed

from context import *
import datetime

# Conversational Pipeline
class ConversationalPipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.model = GPTJGeneratorService(ip=keys["sukima_ip"], username=keys["sukima_username"], password=keys["sukima_password"])
        self.log("Pipeline Initialized.")
        self.prompt = " [Ran Yakumo is a fluffy nine tailed kitsune who lives with Yukari Yakumo and takes care of Chen.]"
        self.name = 'Ran Yakumo'

    def generate(self, message):
        ctxmanager = ContextManager()
        ctxmanager.add_entry(ContextEntry(text=self.prompt, insertion_order=800, insertion_position=0, forced_activation=True, insertion_type=INSERTION_TYPE_NEWLINE))
        ctxmanager.add_entry(ContextEntry(text=message, suffix=f'{self.name}:', reserved_tokens=512, insertion_order=0, trim_direction=TRIM_DIR_TOP, forced_activation=True, cascading_activation=True, insertion_type=INSERTION_TYPE_NEWLINE, insertion_position=-1))
        ctxmanager.add_entry(ContextEntry(text=f" [The current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]", insertion_position=-10, insertion_order=-400, insertion_type=INSERTION_TYPE_NEWLINE, forced_activation=True))
        prompt_formatted = ctxmanager.context()
        response = self.model.sample_sequence_raw(prompt_formatted)

        return response
    
    async def respond(self, message, forced):
        messages = await message.channel.history(limit=80).flatten()
        msg = ''
        for i in reversed(messages):
            if not i.embeds and i.content:
                content = re.sub(r'\<[^>]*\>', '', f'{i.content}')
                if content == '':
                    continue
                msg += f'{i.author.name}: {content}\n'
            elif i.embeds:
                content = i.embeds[0].description
                if content == '':
                    continue
                msg += f'{i.author.name}: [Embed: {content}]\n'
            elif i.attachments:
                msg += f'{i.author.name}: [Image attached]\n'
        
        ctxmanager = ContextManager()
        ctxmanager.add_entry(ContextEntry(text=self.prompt, insertion_order=800, insertion_position=0, forced_activation=True, insertion_type=INSERTION_TYPE_NEWLINE))
        ctxmanager.add_entry(ContextEntry(text=msg, suffix='\n', reserved_tokens=512, insertion_order=0, trim_direction=TRIM_DIR_TOP, forced_activation=True, cascading_activation=True, insertion_type=INSERTION_TYPE_NEWLINE, insertion_position=-1))
        ctxmanager.add_entry(ContextEntry(text=f" [The current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]", insertion_position=-10, insertion_order=-400, insertion_type=INSERTION_TYPE_NEWLINE, forced_activation=True))
        prompt_formatted = ctxmanager.context()
        self.model.args['gen_args']['eos_token_id'] = 25
        self.model.args['sample_args']['temp'] = 0.25
        self.model.args['sample_args']['phrase_biases'] = [{'sequences':[self.name], 'bias':0.5, 'ensure_sequence_finish':True, 'generate_once':True}]
        response = self.model.sample_sequence_raw(prompt_formatted)
        self.model.args['sample_args']['temp'] = 0.4
        self.model.args['sample_args']['phrase_biases'] = None
        self.model.args['gen_args']['eos_token_id'] = 198
        print(prompt_formatted, '\n===')
        print(response)
        if response.startswith(self.name) or forced:
            return self.generate(msg)
        return None

        

from google.cloud import translate_v2 as translate

# Message pipeline for translation tasks.
class TranslationPipeline(Pipeline):

    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.translate_client = translate.Client()
        self.tl_configurations = {
            'ja': 'Japanese',
            'en': 'English',
            'es': 'Spanish',
            'br': 'Brazilian',
            'pt': 'Portuguese',
            'fr': 'French',
            'it': 'Italian',
            'de': 'German',
            'ru': 'Russian',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'nl': 'Dutch',
            'fi': 'Finnish',
            'fr': 'French',
            'hi': 'Hindi',
            'id': 'Indonesian'
        }
        self.log("Pipeline initialized.")
    
    def generate(self, message, to_lang, author):
        if to_lang not in self.tl_configurations:
            return discord.Embed(description="Invalid target language code.")
        
        result = self.translate_client.translate(message, target_language=to_lang)
        embed = discord.Embed()
        embed.set_footer(text=author.name + '#' + author.discriminator, icon_url=author.avatar_url)
        embed.colour = embed_color
        embed.description = f'```{result["translatedText"]}```'
        embed.title = f'{self.tl_configurations[result["detectedSourceLanguage"]]} to {self.tl_configurations[to_lang]}'

        return embed
