class GeneratorService:
        def __init__(self, generate_num=30, temperature=0.75, top_p=1.0, repetition_penalty=0.5, presence_penalty=0.0, model_name='generic', stop_sequences=[], api_key=None):
                self.generate_num = generate_num
                self.temperature = temperature
                self.top_p = top_p
                self.repetition_penalty = repetition_penalty
                self.presence_penalty = presence_penalty
                self.max_tokens = 2048 - generate_num
                self.stop_sequences = stop_sequences
                self.model_name = model_name
                self.api_key = api_key
        
        def sample_sequence_raw(self, context):
                return context
