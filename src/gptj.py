import api
from gptauto import GeneratorService

from prefix import prefix

class GPTJGeneratorService(GeneratorService):
        def __init__(self, generate_num=100, temperature=0.4, tfs=0.993, repetition_penalty=1.25, model_name='c1-6b', stop_sequences=['\n'], ip=None, username=None, password=None):
                self.stop_sequences = stop_sequences
                self.api = api.Sukima_API(ip, username, password)
                self.args = {
                        'model': model_name,
                        'prompt': '',
                        'softprompt': prefix,
                        'sample_args': {
                                'temp': temperature,
                                'top_p': 0.95,
                                'tfs': tfs,
                                'rep_p': repetition_penalty,
                                'rep_p_range': 1024,
                                'rep_p_slope': 0.18,
                                'bad_words': ['***', "Author's Note", 'Deleted', ' [', ' :', 'https', ' https', 'http', ' http', " I don't know!", '```', '``', ' hole', ' holes', '<', ' <', ' @', '._.', ' ._.'],
                        },
                        'gen_args': {
                                'max_length': generate_num,
                                'min_length': 1,
                                'eos_token_id': 198
                        }
                }

        def sample_sequence_raw(self, context):
                self.args['prompt'] = context
                try:
                        text = self.api.generate(self.args)
                except Exception as e:
                        raise e
                for stop_sequence in self.stop_sequences:
                        if stop_sequence in text:
                                text = text[:text.index(stop_sequence)]
                                break
                return text
