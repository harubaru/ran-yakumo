import os
import openai

from gptauto import GeneratorService

class GPT3GeneratorService(GeneratorService):
        def __init__(self, generate_num=30, temperature=0.75, top_p=1.0, repetition_penalty=0.0, presence_penalty=0.0, model_name='babbage', stop_sequences=['\n'], api_key=None):
                self.generate_num = generate_num
                self.temperature = temperature
                self.top_p = top_p
                self.repetition_penalty = repetition_penalty
                self.presence_penalty = presence_penalty
                self.max_tokens = 2048 - generate_num
                self.stop_sequences = stop_sequences
                self.model_name = model_name

                if api_key == None:
                    openai.api_key = os.getenv('OPENAI_API_KEY')
                else:
                    openai.api_key = api_key
        
        def sample_sequence_raw(self, context):
                try:
                    output = openai.Completion.create(
                        engine = self.model_name,
                        prompt = context,
                        max_tokens = self.generate_num,
                        temperature = self.temperature,
                        top_p = self.top_p,
                        frequency_penalty = self.repetition_penalty,
                        presence_penalty = self.presence_penalty,
                        stop = self.stop_sequences
                    )
                    text = output.choices[0].text
                except openai.error.AuthenticationError:
                    print('Invalid OpenAI API Key')
                    text = ''

                return text