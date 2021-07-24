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

class WikipediaPipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.log("Pipeline Initialized.")

class YoutubePipeline(Pipeline):
    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.log("Pipeline Initialized.")


from pybooru import Danbooru

# Message pipeline for Danbooru images.
class DanbooruPipeline(Pipeline):

    def __init__(self, util=None, keys=None):
        super().__init__(util, keys)
        self.nsfw_client = Danbooru('danbooru', api_key=keys["danbooru_token"])
        self.sfw_client = Danbooru('safebooru', api_key=keys["danbooru_token"])
        self.log("Pipeline Initialized.")

    def generate(self, message, nsfw=False):
        if not message:
            return None
        
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
        self.log('{} -> {}'.format(from_lang, to_lang))
        
        if from_lang not in self.tl_configurations:
            return "Invalid language code."
        if to_lang not in self.tl_configurations:
            return "Invalid language code."
        
        prompt_formatted = self.prompt.format(from_lang=self.tl_configurations[from_lang], to_lang=self.tl_configurations[to_lang], message=message)
        response = self.model.sample_sequence_raw(prompt_formatted)

        return response
