# Discord message pipeline
# Takes in message, parses it, and returns response.

from gpt3 import GPT3GeneratorService

class TranslationPipeline():
    def __init__(self, util=None, keys=None):
        self.util = util
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

    def log(self, message):
        if self.util is not None:
            self.util.log('TranslationPipeline', message)
    
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
