# Discord message pipeline
# Takes in message, parses it, and returns response.

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
from gpt3search import SearchService

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
        self.service = SearchService(api_key=keys["openai_token"])
        self.log("Pipeline Initialized.")

    def generate(self, message):
        if not message:
            return "Please specify a search term."
        
        results = YoutubeSearch(message, max_results=8)
        if not results:
            return 'Could not find YouTube video.'
        
        search_query = []
        for i in results.videos:
            search_query.append(i['title'])
        
        selection = self.service.classify_sequence(message, search_query)
        return 'https://www.youtube.com' + results.videos[selection]['url_suffix']

from pybooru import Danbooru

# Message pipeline for Danbooru images.
class DanbooruPipeline(Pipeline):

    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.nsfw_client = Danbooru('danbooru', username=keys["danbooru_username"], api_key=keys["danbooru_token"])
        self.sfw_client = Danbooru('safebooru', username=keys["danbooru_username"], api_key=keys["danbooru_token"])
        self.log("Pipeline Initialized.")

    def generate(self, message, nsfw=False):
        if not message:
            return "Please specify a search term."
        
        if nsfw:
            output = self.nsfw_client.post_list(tags=message, limit=1, random=True)
        else:
            output = self.sfw_client.post_list(tags=message, limit=1, random=True)
        if not output:
            return 'Post not found.'
        
        try:
            return output[0]['file_url']
        except:
            return 'Post not found.'


from gpt3 import GPT3GeneratorService

# Q&A Pipeline
class QnAPipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.model = GPT3GeneratorService(generate_num=60, temperature=0.5, repetition_penalty=0.5, model_name='davinci', api_key=keys["openai_token"])
        self.log("Pipeline Initialized.")

        self.prompt = "I am a highly intelligent youkai from the Touhou Project named Ran Yakumo. My answers will always be truthful.\n\nQ: How does a telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n\nQ: {question}\nA:"
    
    def generate(self, message):
        prompt_formatted = self.prompt.format(question=message)
        prompt_formatted = prompt_formatted[0:400] # 400 character limit
        response = self.model.sample_sequence_raw(prompt_formatted)
        
        if response == '':
            response = 'Unknown'
        
        return response

# Message pipeline for translation tasks.
class TranslationPipeline(Pipeline):

    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.model = GPT3GeneratorService(generate_num=32, temperature=0.33, model_name='davinci', api_key=keys["openai_token"])
        self.prompt = "This is a translation from {from_lang} to {to_lang}.\n{from_lang}: {message}\n{to_lang}:"
        self.tl_configurations = {
            'ja': 'Japanese',
            'en': 'English',
            'es': 'Spanish',
            'br': 'Brazilian',
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
    
    def generate(self, message, from_lang, to_lang):
        # log from language and to language

        if from_lang not in self.tl_configurations:
            return "Invalid language code."
        if to_lang not in self.tl_configurations:
            return "Invalid language code."
        
        prompt_formatted = self.prompt.format(from_lang=self.tl_configurations[from_lang], to_lang=self.tl_configurations[to_lang], message=message)
        prompt_formatted = prompt_formatted[0:400] # 400 character limit
        response = self.model.sample_sequence_raw(prompt_formatted)

        if response == '':
            response = 'Unable to translate.'

        return response
