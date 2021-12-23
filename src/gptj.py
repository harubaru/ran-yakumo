import api
from gptauto import GeneratorService

class GPTJGeneratorService(GeneratorService):
        def __init__(self, generate_num=100, temperature=0.51, tfs=0.993, repetition_penalty=1.155, model_name='c1-6b', stop_sequences=['\n'], ip=None, username=None, password=None):
                self.stop_sequences = stop_sequences
                self.api = api.Sukima_API(ip, username, password)
                self.args = {
                        'model': model_name,
                        'prompt': '',
                        'softprompt': 'gap',
                        'sample_args': {
                                'temp': temperature,
                                'tfs': tfs,
                                'rep_p': repetition_penalty,
                                'rep_p_range': 2048,
                                'rep_p_slope': 0.18,
                                'bad_words': ['***', "Author's Note", 'Deleted', ' [', ' :', 'https', ' https', 'http', ' http', " I don't know!"],
                        },
                        'gen_args': {
                                'max_length': generate_num
                        }
                }

        def sample_sequence_raw(self, context):
                self.args['prompt'] = context
                text = self.api.generate(self.args)
                for stop_sequence in self.stop_sequences:
                        if stop_sequence in text:
                                text = text[:text.index(stop_sequence)]
                                break
                return text